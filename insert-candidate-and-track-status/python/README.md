# Insert Candidate then track Status

This example shows how to insert a candidate into Connect, then track the status
of that candidate.

It is a fully working application of the example shown at
https://rolepoint-connect.readme.io/docs/insert-candidate-and-track-status.

## How to run this example

Connect sends candidate status updates to client applications using webhooks.
For the example to receive these webhooks it will need to be exposed to the
internet. We recommend using [ngrok](https://ngrok.com) for this - it can expose
a port on your local machine to the internet, allowing you to receive the
webhooks sent from connect. For the purposes of this guide, we will assume you
are using ngrok and have successfully installed it.

The example will be exposed on port 5000, so we start ngrok up to expose the
local server:

    > ngrok http 5000

The output from the above command will include a line which says `Forwarding`,
with a URL which looks like `https://2fb65876.ngrok.io`. Note that yours will
have a different subdomain.

Now you can get a sandbox account for Connect, using
`https://<subdomain>.ngrok.io/webhook_url` as your webhook URL.
[Steps to get one here](https://rolepoint-connect.readme.io/docs/sandbox-connector).

You will need to edit `app.py` and change the settings on lines 27-30.

- `username` should be set to your Connect username
- `password` should be set to your Connect password
- `connector_id` should be set to your Connect connector ID
- `ngrok_url` should be set to the ngrok URL from above, from the subdomain
  onwards. E.g `2fb65876.ngrok.io`

You will need to install the requirements for this example, we recommend using
[virtualenv](http://virtualenv.readthedocs.org/en/latest/) when installing
dependencies. Then:

    > pip install -r requirements.txt

Now you just need to run:

    > python app.py

You can now open a browser and visit your ngrok URL. You should see a very basic
HTML form, with the title `Application Form` asking for first name, last name
and email address. This is our job application form, so fill it out and click
submit.

You should now see in the `Applications` table the email address of the
candidate you just submitted, and an `Application Status in Connect` of `In
Progress`. Refresh the page until that becomes `Complete`. As this point our
candidate has made it into the ATS, and you should see the `Candidate ID` has
also been populated.

There should also now be another form at the bottom of the page, titled `Trigger
Status Update`. This form is needed to trigger a `candidate_status_update`
webhook event from Connect, as this is an example application. If this was a
real candidate you would receive these `candidate_status_update` webhook events
automatically.

You can now fill out this form, selecting the candidate you wish to update the
status for, and any status you wish. Clicking submit will send these details on
to Connect, which will in turn send a webhook event back. You should now see in
the `Candidate Status in ATS` column of the `Applications` table, that your
candidate has a value which corresponds to the status you just set! If the value
isn't populated, refresh the page and it should be there.

