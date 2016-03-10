# Get Jobs and Insert Applications

This example shows a simple application with an endpoint for recieving RolePoint Connect webhook events and making job applications.

## How to run this example

You will need to expose the example application so that RolePoint Connect can communicate with it. For this we recommend using [ngrok](https://ngrok.com). For the purposes of this guide, we will assume you are using ngrok and have successfully installed it.

Our application will by default be exposed on port 5000, so we start ngrok up to expose the local server:

    > ngrok http 5000

The output from the above command will include a line which says `Forwarding`, with a URL which looks like `https://2fb65876.ngrok.io`. Note that yours will have a different subdomain. 

You will also need a sandbox account for [RolePoint Connect](http://www.rolepoint.com/ats-crm-middleware.html).

Once you have obtained a sandbox account, you will need to edit `app.py` and change the settings on lines 27-33. `app.config['SERVER_NAME']` should be set to the ngrok URL from above, from the subdomain onwards. E.g `2fb65876.ngrok.io`. The other settings should be replaced with your RolePoint Connect username/password and ID respectively.

You will need to install the requirements for this example:

    > pip install -r requirements.txt

Now you just need to run:

    > python app.py

You can now open a browser and visit your ngrok URL. You should see a very basic HTML form. 

However you will also need to populate the Jobs dropdown on this page. Normally RolePoint Connect would automatically send you your job listings from your ATS, for this example application however we will need to push RolePoint Connect to send us an example webhook. To do this you can run the following command, (replacing the ngrok URL in the payload with your ngrok URL):

    > curl -H "Content-Type: application/json" -X POST -d '{"webhook_url": "http://2fb65876.ngrok.io/webhook_url"' http://localhost:5060/test_webhook/send_job_add_event

If you refresh the page, you should now see a job in the dropdown, you can now go ahead and make a Job Application!

Once you've made your Job Application you will be taken to a page showing all of the Job Applications made on your example application. The one you've just made should be listed here, with a status of `In Progress`. Once RolePoint Connect has finished processing your Job Application, the status will be changed to `Complete`, and `Candidate ID` and `Application Ids` should be populated! 

Congratulations, you've just made your first Job Application!
