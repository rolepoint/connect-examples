"""
A simple application with an endpoint for making job applications, and an
endpoint for processing candidate status webhooks.

We define:
- An endpoint for handling incoming web hooks, so we can update candidate
  statuses
- A view for creating candidates, listing candidates and updating the status
- Endpoints to create candidates and update their statuses.
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


# We will store our Job Applications as a list of dicts of the form:
# {'candidate': {'first_name': string, 'last_name': string, 'email': string},
#  'candidate_id': The ID of the Candidate in Connect,
#  'connect_status': In Progress,Complete or Failed,
#  'candidate_status': String of the candidate status in the ATS.
#
# NOTE: Restarting the server will empty this list of job applications.
JOB_APPLICATIONS = []


@app.route('/webhook_url', methods=['POST'])
def status_webhook_handler():
    """
    An endpoint for handling Connect webhook events. Only handles
    `candidate_status_update` events, as that is all we are interested in for
    this example application.
    """
    for event in request.get_json(force=True):
        event_type = event['event']

        if event_type == 'candidate_status_update':
            for application in JOB_APPLICATIONS:
                if application['candidate_id'] == event['data']['entity_id']:
                    application['candidate_status'] = event['data']['status']['value']
                    break

    # We return an empty response to Connect as it will retry webhooks
    # otherwise.
    return '', 200


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

    JOB_APPLICATIONS.append({
        'candidate': candidate, 'connect_status': 'In Progress'
    })

    # Build our payload to include our candidate and a fake job_id
    payload = {'candidate': candidate, 'applications': [{'job_id': '123'}]}

    # Our application_id is just the index of the application in our list of
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

    return redirect('/')


@app.route('/')
def home():
    """
    Renders a basic HTML page with the following elements:

    - A form for making job applications
    - A table showing the current job applications and their statuses.
    - A form for triggering candidate status webhook events in Connect.
    """
    return render_template_string("""
    <html>
      <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" integrity="sha384-1q8mTJOASx8j1Au+a5WDVnPi2lkFfwwEAa8hDDdjZlpLegxhjVME1fgjWPGmkzs7" crossorigin="anonymous">
      <div class="container-fluid">
        <h2>Application Form</h2>
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
          <button type="submit" class="btn btn-default">Submit</button>
        </form>
        <h2>Applications</h2>
        <table class="table">
          <tr>
            <th>Email Address</th>
            <th>Application Status in Connect</th>
            <th>Candidate Status in ATS</th>
            <th>Candidate ID</th>
          </tr>
          {% for application in job_applications %}
            <tr>
              <td>{{ application.candidate.email }}</td>
              <td>{{ application.connect_status }}</td>
              <td>{{ application.candidate_status }}</td>
              <td>{{ application.candidate_id }}</td>
            </tr>
          {% endfor %}
        </table>
        {% if job_applications and job_applications.0.candidate_id %}
        <h2>Trigger Status Update</h2>
        <form action="trigger_status" method="post">
          <div class="form-group">
            <label for="candidate_id">Candidate</label>
            <select class="form-control" name="candidate_id" id="candidate_id">
              {% for application in job_applications %}
                {% if application.candidate_id %}
                    <option value="{{application.candidate_id}}">{{application.candidate.email}}</option>
                {% endif %}
              {% endfor %}
            </select>
          </div>
          <div class="form-group">
            <label for="status">Status</label>
            <input type="text" class="form-control" id="status" name="status" placeholder="Status">
          </div>
          <button type="submit" class="btn btn-default">Submit</button>
        </form>
        {% endif %}
      </div>
    </html>
    """, job_applications=JOB_APPLICATIONS)


@app.route('/application_processed_callback/<int:app_id>', methods=['POST'])
def application_processed_callback(app_id):
    """
    An endpoint for handling Connect application callbacks.
    Here we update our candidate application once Connect has
    processed them.
    """
    status = request.json['status']
    JOB_APPLICATIONS[app_id]['connect_status'] = status

    if status == 'complete':
        result = requests.get(request.json['result_info']['url'], auth=AUTH)
        json = result.json()
        JOB_APPLICATIONS[app_id]['candidate_id'] = json['candidate_id']

    # We return an empty response to Connect as it will retry callbacks
    # otherwise.
    return '', 200


@app.route('/trigger_status', methods=['POST'])
def trigger_status_webhook():
    """
    Requests Connect to send an example status webhook with our submitted
    details.
    """
    url = '{}/examples/send-candidate-status-event/{}/{}'.format(
        CONNECT_URL, request.form['candidate_id'], request.form['status']
    )
    requests.post(
        url, auth=AUTH,
        json={'webhook_url': url_for('status_webhook_handler', _external=True)}
    )
    return redirect('/')


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

    if 'http' in CONFIG['ngrok_url']:
        print("Include the ngrok name without 'http(s)' in the ngrok_url "
              "field.")
        sys.exit()
    app.run()
