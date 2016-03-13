# Find Candidates and Retrieve their details.

This example shows how we can search for Candidates using Connect, then retrieve their details from the remote ATS.

## How to run this example

You will need a sandbox account for [Connect](http://www.rolepoint.com/ats-crm-middleware.html).

for this example to run it will need to be exposed to the internet. This is because it takes advantage of the callback functionality of Connect, so Connect needs to be ale to communicate back to the example application. We recommend using [ngrok](https://ngrok.com) for this - it can expose a port on your local machine to the internet, allowing you to receive the webhooks sent from connect. For the purposes of this guide, we will assume you are using ngrok and have successfully installed it.

The example will be exposed on port 5000, so we start ngrok up to expose the local server:

    > ngrok http 5000

The output from the above command will include a line which says `Forwarding`, with a URL which looks like `https://2fb65876.ngrok.io`. Note that yours will have a different subdomain. 

You will need to edit `app.py` and change the settings on lines 27-30. 

- `username` should be set to your Connect username
- `password` should be set to your Connect password
- `connector_id` should be set to your Connect connector ID
- `ngrok_url` should be set to the ngrok URL from above, from the subdomain onwards. E.g `2fb65876.ngrok.io`

You will need to install the requirements for this example, we recommend using [virtualenv](http://virtualenv.readthedocs.org/en/latest/) when installing dependencies. Then:

    > pip install -r requirements.txt

Now you just need to run:

    > python app.py

You can now open a browser and visit your ngrok URL. On the first visit to this URL the example application is seeded with 5 candidates, so it may take a few seconds to load.

Once the page has loaded you should see 3 sections, the first section is `Created Candidates`, which is a table containing the 5 candidates we have just created. All should show their creation status as being `In Progress`. We have asked Connect to create these Candidates, and are just waiting to hear back. You can refresh the page until they show as `Complete`, which means they have been created in Connect, and we can now search for them by the shown email address.

The next section is `Searches`, which is a table showing any searches we have initiated in Connect using the `find_candidates` funtionailty. The final section is `Search for Candidate by email`, which shows a text box and a button. Any of the candidates who have been created in your sandbox Connector can be searched for here. 

Try copy and pasting one of the example email addresses from the top of the page into the text box then clicking `Submit`. The page should refresh and the email address you are searching for should have an entry in the `Searches` table, with a `Search Status` of `In Progress`. We are waiting for Connect to call back to us with the result of the search. 

Try refreshing the page until the `Search Status` shows as `Complete`. You should now see an entry in the `Candidate ID's` column for our search. This will be an integer of the Candidate ID in Connect. If you click the entry, we initiate a `get_candidate` query to Connect and the page should refresh. You will now see that the `Get Candidate Status` column is showing as `In Progress`. 

We are again waiting for a callback for Connect, so you can refresh the page until the `Get Candidate Status` column shows as `Complete`. At this stage you should see some JSON data populating the `Get Candidate Result` column, containing the details of our queried for Candidate.
