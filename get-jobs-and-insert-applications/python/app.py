"""
A simple application with an endpoint for recieving Connect webhook
events and making job applications.

We define:
- An endpoint for handling incoming web hooks, so we can save jobs
- A view for applying for jobs
- A view for handling job applications and sending them on to Connect
- A callback endpoint for Connect to call back to once the
  application has finished processing.
- A view for listing all current job applications.
"""
import sys

from flask import Flask
from flask import redirect, request, render_template_string
from flask import url_for
import requests
from requests.auth import HTTPBasicAuth

# Setup our Flask application
app = Flask(__name__)

# Create our config with Connect details
# NOTE: You must fill in this section with YOUR details in order to run this
#       example application

CONFIG = {
    'username': 'Replace with Connector username',
    'password': 'Replace with Connector password',
    'connector_id': 'Replace with Connector ID',
    'ngrok_url': 'Replace Me with your ngrok URL (e.g 38gbvy74.ngrok.io)'
}

app.config['SERVER_NAME'] = CONFIG['ngrok_url']

CONNECT_URL = 'https://api.rolepoint-connect.com'

AUTH = HTTPBasicAuth(CONFIG['username'], CONFIG['password'])

# We will store our jobs as a mapping of the ID of the job in the ATS, to the
# title of the Job.
#
# NOTE: Restarting the server will empty this dictionary of jobs.
JOBS = {}

# We will store our Job Applications as a list of dicts of the form:
# {'job_id': ID of the job in the ATS,
#  'candidate': {'first_name': string, 'last_name': string, 'email': string},
#  'status': In Progress,Complete or Failed,
#  'candidate_id': The ID of the Candidate in Connect,
#  'application_ids': The ID's of the applications in Connect.}
#
# NOTE: Restarting the server will empty this list of job applications.
JOB_APPLICATIONS = []


@app.route('/webhook_url', methods=['POST'])
def jobs_webhook_handler():
    """
    An endpoint for handling Connect webhook events. Only handles
    `job_add` events, as that is all we are interested in for this example
    application.
    """
    for event in request.get_json(force=True):
        if event['event'] == 'job_add':
                JOBS[event['data']['ats_id']] = event['data']['title']

    # We return an empty response to Connect as it will retry webhooks
    # otherwise.
    return '', 200


@app.route('/application_processed_callback/<int:app_id>', methods=['POST'])
def application_processed_callback(app_id):
    """
    An endpoint for handling Connect application callbacks.
    Here we update our candidate application once Connect has
    processed them.
    """
    status = request.json['status']
    JOB_APPLICATIONS[app_id]['status'] = status

    if status == 'complete':
        result = requests.get(request.json['result_info']['url'], auth=AUTH)
        json = result.json()
        JOB_APPLICATIONS[app_id]['candidate_id'] = json['candidate_id']
        JOB_APPLICATIONS[app_id]['application_ids'] = json['application_ids']

    # We return an empty response to Connect as it will retry callbacks
    # otherwise.
    return '', 200


@app.route('/')
def render_application_form():
    if not JOBS:
        requests.post(
            CONNECT_URL + '/examples/send-job-add-event',
            json={
                'webhook_url': (
                    'http://{}/webhook_url'.format(CONFIG['ngrok_url'])
                )
            }
        )
    return render_template_string("""
    <html>
      <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" integrity="sha384-1q8mTJOASx8j1Au+a5WDVnPi2lkFfwwEAa8hDDdjZlpLegxhjVME1fgjWPGmkzs7" crossorigin="anonymous">
      <div class="container-fluid">
        <form action="make_application" method="post">
          <div class="form-group">
            <label for="first_name">First Name</label>
            <input type="text" class="form-control" id="first_name" name="first_name" placeholder="First Name">
          </div>
          <div class="form-group">
            <label for="last_name">Last Name</label>
            <input type="text" class="form-control" id="last_name" name="last_name" placeholder="Last Name">
          </div>
          <div class="form-group">
            <label for="email">Email Address</label>
            <input type="email" class="form-control" id="email" name="email" placeholder="Email Address">
          </div>
          <div class="form-group">
            <label for="job_id">Job</label>
            <select class="form-control" name="job_id" id="job_id">
              {% for job_id, title in jobs.items() %}
                <option value="{{job_id}}">{{title}}</option>
              {% endfor %}
            </select>
          </div>
          <button type="submit" class="btn btn-default">Submit</button>
        </form>
      </div>
    </html>
    """, jobs=JOBS)


@app.route('/make_application', methods=['POST'])
def make_application():
    """
    Save an application to our JOB_APPLICATIONS and send it to Connect for
    processing.
    """
    # Create our application from the submitted form data
    candidate = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email']
    }
    job_id = request.form['job_id']

    JOB_APPLICATIONS.append({
        'candidate': candidate, 'job_id': job_id, 'status': 'In Progress'
    })

    # Build our payload to include our candidate and the job they are applying
    # for.
    payload = {'candidate': candidate, 'applications': [{'job_id': job_id}]}

    # Out application_id is just the index of the application in our list of
    # JOB_APPLICATIONS
    application_id = len(JOB_APPLICATIONS) - 1

    # We can choose to either include a callback header with our
    # request, or to poll until the application is complete. Here
    # we use the callback functionality.
    headers = {
        'content-type': 'application/rolepoint.v2+json',
        'x-rolepoint-callback-url': url_for(
            'application_processed_callback',
            app_id=application_id, _external=True
        )
    }
    # Send the application to Connect for processing.
    requests.post(
        CONNECT_URL + '/v1/{}/candidate'.format(CONFIG['connector_id']),
        json=payload, auth=AUTH, headers=headers
    )

    return redirect('show_applications')


@app.route('/show_applications')
def show_applications():
    """
    Renders a basic HTML table showing the current job applications and their
    statuses.
    """
    return render_template_string("""
    <html>
      <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" integrity="sha384-1q8mTJOASx8j1Au+a5WDVnPi2lkFfwwEAa8hDDdjZlpLegxhjVME1fgjWPGmkzs7" crossorigin="anonymous">
      <div class="container-fluid">
        <table class="table">
          <tr>
            <th>First Name</th>
            <th>Last Name</th>
            <th>Email Address</th>
            <th>Job Title Applied For</th>
            <th>Application Status in Connect</th>
            <th>ATS ID</th>
            <th>Application ID's</th>
          </tr>
          {% for application in job_applications %}
            <tr>
              <td>{{ application.candidate.first_name }}</td>
              <td>{{ application.candidate.last_name }}</td>
              <td>{{ application.candidate.email }}</td>
              <td>{{ jobs[application.job_id] }}</td>
              <td>{{ application.status }}</td>
              <td>{{ application.candidate_id }}</td>
              <td>{{ application.application_ids }}</td>
            </tr>
          {% endfor %}
        </table>
      </div>
    </html>
    """, job_applications=JOB_APPLICATIONS, jobs=JOBS)

if __name__ == "__main__":
    if CONFIG == {
        'username': 'Replace with Connector username',
        'password': 'Replace with Connector password',
        'connector_id': 'Replace with Connector ID',
        'ngrok_url': 'Replace Me with your ngrok URL (e.g 38gbvy74.ngrok.io)'
    }:
        print("You must configure the CONFIG with your settings to run the "
              "example.")
        sys.exit()
    app.run()
