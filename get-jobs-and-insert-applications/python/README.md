# Get Jobs and Insert Applications

This example receives job postings & submits candidates using Connect.

## How to run this example

You will need a sandbox account for [Connect](http://www.rolepoint.com/ats-crm-middleware.html).

Connect sends jobs to client applications using webhooks. For the example to receive these webhooks it will need to be exposed to the internet. We recommend using [ngrok](https://ngrok.com) for this - it can expose a port on your local machine to the internet, allowing you to receive the webhooks sent from connect. For the purposes of this guide, we will assume you are using ngrok and have successfully installed it.

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

You can now open a browser and visit your ngrok URL. You should see a very basic HTML form, but the job listing is empty. When you load the page for the first time you sent a request to Connect asking it to send a webhook containing job listings, so hopefully if you refresh the page you should see a job listing in the dropdown!

Normally connect would send us jobs automatically, but as you're using a sandbox account this doesn't happen.

If you refresh the page, you should now see a job in the dropdown, you can now go ahead and make a Job Application!

Once you've made your Job Application you will be taken to a page showing all of the Job Applications made on your example application. The one you've just made should be listed here, with a status of `In Progress`. Once Connect has finished processing your Job Application, the status will be changed to `Complete`, and `Candidate ID` and `Application Ids` should be populated! 

Congratulations, you've just made your first job application!
