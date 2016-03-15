"""
A simple application with endpoints for searching for candidates and
retrieving those found candidates. Creates candidates the first time the
homepage is visited.

We define:
- A view to search for candidates by email address.
- A view for showing the details of the candidates we have created, and the
  status of their creation.
- An endpoint for retrieving the candidates found.
"""
import json
from random import choice
import sys

from flask import Flask
from flask import redirect, render_template_string, request, url_for
import names
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


# We will store the candidates we create as a list of dicts of the form:
# {'email': string, 'first_name': string, 'last_name': string,
#  'status': Either 'In Progress' or 'Complete'}
CREATED_CANDIDATES = []


# A list containing the current searches we have started and their results
# will contain dicts of he form:
# {'email': email address we are searching for,
#  'search_status': 'In Progress' or 'Complete',
#  'candidate_ids': The ID's of the candidate returned from Connect,
#  'get_candidate_status': The status of getting the candidate details,
#  'candidate_details': The candidate details retrieved from Connect
#                       `get_candidate`}
SEARCHES = []


def populate_candidates():
    """
    Sends requests to connect to populate our sandbox Connector with 5 random
    candidates.
    """
    for i in range(5):
        last_name = names.get_last_name()
        candidate = {
            'first_name': names.get_first_name(),
            'last_name': last_name,
            'email': '{}{}@example.com'.format(last_name,
                                               choice(range(100)))
        }
        candidate_data = {
            # A random job_id will be fine as we are in a sandbox environment
            'candidate': candidate, 'applications': [{'job_id': '101'}]
        }

        # We can choose to either include a callback header with our
        # request, or to poll until the application is complete. Here
        # we use the callback functionality.
        headers = {
            'content-type': 'application/rolepoint.v2+json',
            'x-rolepoint-callback-url': url_for(
                'application_processed_callback',
                app_id=len(CREATED_CANDIDATES), _external=True
            )
        }

        requests.post(
            CONNECT_URL + '/v1/{}/candidate'.format(CONFIG['connector_id']),
            json=candidate_data, auth=AUTH, headers=headers
        )
        candidate['status'] = 'In Progress'
        CREATED_CANDIDATES.append(candidate)


@app.route('/application_processed_callback/<int:app_id>', methods=['POST'])
def application_processed_callback(app_id):
    """
    An endpoint for handling Connect candidate callbacks. Here we update our
    entry with the status.
    """
    CREATED_CANDIDATES[app_id]['status'] = request.json['status']

    # We return an empty response to Connect as it will retry callbacks
    # otherwise.
    return '', 200


@app.route('/')
def home():
    """
    Our main view with a table showing the email addresses of the candidates
    we have created, and their current creation status.

    We also have a table showing any searches we have initiated, and their
    status.

    Once the creation status is "Complete" we can search for them by their
    email using the search box.
    """
    if not CREATED_CANDIDATES:
        populate_candidates()

    return render_template_string("""
        <html>
          <div class="container-fluid">
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" integrity="sha384-1q8mTJOASx8j1Au+a5WDVnPi2lkFfwwEAa8hDDdjZlpLegxhjVME1fgjWPGmkzs7" crossorigin="anonymous">
            <h1>Created Candidates</h1>
            <table class="table">
              <tr>
                <th>Candidate Email</th>
                <th>Creation Status</th>
              </tr>
              {% for candidate in candidates %}
              <tr>
                <td>{{ candidate.email }}</td>
                <td>{{ candidate.status }}</td>
              </tr>
              {% endfor %}
            </table>
            <br><br><br>
            <h1>Searches</h1>
            <table class="table">
              <tr>
                <th>Search Query</th>
                <th>Search Status</th>
                <th>Candidate ID's</th>
                <th>Get Candidate Status</th>
                <th>Get Candidate Result</th>
              </tr>
              {% for search in searches %}
              <tr>
                <td>{{ search.query }}</td>
                <td>{{ search.search_status }}</td>
                <td>
                  {% set index = loop.index0 %}
                  {% for candidate_id in search.candidate_ids %}
                    <a href="{{ url_for('get_candidate', search_id=index, candidate_id=candidate_id) }}">{{candidate_id}}</a><br>
                  {% endfor %}
                </td>
                <td>{{ search.get_candidate_status }}</td>
                <td>{{ search.candidate_details }}</td>
              </tr>
              {% endfor %}
            </table>
            <br><br><br>
            <h2>Search for Candidate by email</h2>
            <form action="search" method="post" class="form-inline">
              <div class="form-group">
                <input type="text" class="form-control" name="query">
              </div>
              <button type="submit" class="btn btn-default">Submit</button>
            </form>
          </div>
        </html>
    """, candidates=CREATED_CANDIDATES, searches=SEARCHES)


@app.route('/search', methods=['POST'])
def search_by_email():
    """
    An endpoint for searching Connect for candidates by their email address.
    """
    email = request.form['query'].strip()
    SEARCHES.append(
        {'query': email, 'candidate_ids': [], 'search_status': 'In Progress',
         'get_candidate_status': 'Not Started', 'candidate_details': None}
    )

    # We build our query using the Connect find_candidates schema.
    # We can stack as many filters as we like here, but for this example we
    # only show filtering by email address.
    query = {'filters': [{'operator': '==', 'field': 'email', 'value': email}]}
    # We can choose to either include a callback header with our
    # request, or to poll until the search is complete. Here
    # we use the callback functionality.
    search_id = len(SEARCHES) - 1
    headers = {
        'content-type': 'application/rolepoint.v2+json',
        'x-rolepoint-callback-url': url_for(
            'search_complete_callback',
            search_id=search_id, _external=True
        )
    }
    requests.post(
        CONNECT_URL + '/v1/{}/find_candidates'.format(CONFIG['connector_id']),
        json=query, auth=AUTH, headers=headers
    )
    return redirect('/')


@app.route('/search_complete_callback/<int:search_id>', methods=['POST'])
def search_complete_callback(search_id):
    """
    An endpoint for handling Connect find_candidates callbacks.
    Here we update our Search with the status or the search, and the found
    candidate_ids.
    """
    status = request.json['status']
    SEARCHES[search_id]['search_status'] = status
    # We get the result of the search
    if status == 'complete':
        result = requests.get(request.json['result_info']['url'], auth=AUTH)
        SEARCHES[search_id]['candidate_ids'] = result.json()['candidate_ids']

    # We return an empty response to Connect as it will retry callbacks
    # otherwise.
    return '', 200


@app.route('/get_candidate/<int:search_id>/<candidate_id>')
def get_candidate(search_id, candidate_id):
    """
    An endpoint to retrieve found candidate details from Connect.
    """
    # We can choose to either include a callback header with our
    # request, or to poll until the search is complete. Here
    # we use the callback functionality.
    headers = {
        'content-type': 'application/rolepoint.v2+json',
        'x-rolepoint-callback-url': url_for(
            'get_candidate_complete_callback',
            search_id=search_id, _external=True
        )
    }

    url = '/v1/{}/candidate/{}'.format(CONFIG['connector_id'], candidate_id)
    requests.get(CONNECT_URL + url, auth=AUTH, headers=headers)

    SEARCHES[search_id]['get_candidate_status'] = 'In Progress'

    return redirect('/')


@app.route('/get_candidate_complete_callback/<int:search_id>', methods=['POST'])
def get_candidate_complete_callback(search_id):
    """
    An endpoint for handling Connect get_candidate callbacks.
    Here we update our Search with the status or the get_candidate query,
    and the final result of retireving the candidate.
    """
    status = request.json['status']
    SEARCHES[search_id]['get_candidate_status'] = status

    # We get the result of the get_candidate call.
    if status == 'complete':
        result = requests.get(request.json['result_info']['url'], auth=AUTH)
        SEARCHES[search_id]['candidate_details'] = json.dumps(result.json())

    # We return an empty response to Connect as it will retry callbacks
    # otherwise.
    return '', 200


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
