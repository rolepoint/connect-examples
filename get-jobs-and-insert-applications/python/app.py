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
    'username': 'Replace with Connect username',
    'password': 'Replace with Connect password',
    'connector_id': 'Replace with Connect ID',
    'ngrok_url': 'Replace Me with your ngrok URL'
}

app.config['SERVER_NAME'] = CONFIG['ngrok_url']

CONNECT_URL = 'https://api.rolepoint-connect.com/v1/{}'.format(
    CONFIG['connector_id']
)

JOB_ADD_URL = 'http://{}/test_webhook/send_job_add_event'.format(
    CONFIG['ngrok_url']
)

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

    # We return an empty response to Connect.
    return ''


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

    # We return an empty response to Connect.
    return ''


@app.route('/')
def render_application_form():
    return render_template_string("""
    <html>
      <form action="make_application" method="post">
        First name:<br>
        <input type="text" name="first_name"><br>
        Last name:<br>
        <input type="text" name="last_name"><br>
        Email Address:<br>
        <input type="text" name="email"><br>
        <select name="job_id">
          {% for job_id, title in jobs.items() %}
            <option value="{{job_id}}">{{title}}</option>
          {% endfor %}
        </select><br>
        <input type="submit" value="Submit">
      </form>
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
    # we use the callback funtionality.
    headers = {
        'content-type': 'application/rolepoint.v2+json',
        'x-rolepoint-callback-url': url_for(
            'application_processed_callback',
            app_id=application_id, _external=True
        )
    }
    # Send the application to Connect for processing.
    requests.post(CONNECT_URL + '/applications',
                  json=payload, auth=AUTH, headers=headers)

    return redirect('show_applications')


@app.route('/show_applications')
def show_applications():
    """
    Renders a basic HTML table showing the current job applications and their
    statuses.
    """
    return render_template_string("""
    <html>
      <table border="1">
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
            <th>{{ application.candidate.first_name }}</th>
            <th>{{ application.candidate.last_name }}</th>
            <th>{{ application.candidate.email }}</th>
            <th>{{ jobs[application.job_id] }}</th>
            <th>{{ application.status }}</th>
            <th>{{ application.candidate_id }}</th>
            <th>{{ application.application_ids }}</th>
          </tr>
        {% endfor %}
      </table>
    </html>
    """, job_applications=JOB_APPLICATIONS, jobs=JOBS)


@app.route('/test_job_webhook')
def populate_job():
    """
    Sends a request to connect to send a test webhook
    """
    requests.post(CONNECT_URL + 'test_webhook/send_job_add_event',
                  json={'webhook_url': JOB_ADD_URL})
    redirect('/')

if __name__ == "__main__":
    if CONFIG == {
        'username': 'Replace with Connect username',
        'password': 'Replace with Connect password',
        'connector_id': 'Replace with Connect ID',
        'ngrok_url': 'Replace Me with your ngrok URL'
    }:
        print("You must configure the CONFIG with your settings to run the "
              "example.")
        sys.exit()
    app.run()
