require 'sinatra'
require 'json'


CONFIG = {
  :username => "example_taleo_enterpise_QZVqoO",  # Fill in with Connector username
  :password => "MgNpAOrKWeowIeex",  # Fill in with Connector password
  :connector_id => "2190",  # Fill in with Connector ID
  :ngrok_url => "21b8cf5a.ngrok.io",  # Fill in with your ngrok URL (eg. 38gbvy74.ngrok.io)
}

JOBS = {}


get '/' do
  JOBS.to_json
end


post '/webhook_url' do
  data = JSON.parse request.body.read
  data.each do |event|
    if event["event"] == "job_add"
      JOBS[event["data"]["ats_id"]] = event["data"]["title"]
    end
  end
end


def main
  if CONFIG[:username] == "" || CONFIG[:password] == "" || CONFIG[:connector_id] == "" || CONFIG[:ngrok_url] == ""
    puts "You must configure the CONFIG with your settings to run the example."
    Kernel.exit(1)
  end

  set :port, 8080
end


if __FILE__ == $0
  main
end
