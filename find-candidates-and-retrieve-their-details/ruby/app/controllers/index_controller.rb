require_relative '../helpers/connect'

$CREATED_CANDIDATES = Array.new
$SEARCHES = Array.new


# Generates random candidates information to be sent to Connect later on.
def populate_candidates()
  require 'namey'

  name_generator = Namey::Generator.new
  5.times do
    last_name = name_generator.surname(:rare)
    new_candidate = {
      "first_name" => name_generator.name(:rare, surname=false),
      "last_name" => last_name,
      "email" => last_name + "@example.com"
    }
    $CREATED_CANDIDATES.push(new_candidate)
  end
end


# Sends requests to connect to populate our sandbox Connector with 5 random
# candidates.
def post_candidates_to_connect()
  require 'net/http'
  require 'uri'

  url = "%s/v1/%s/candidate" % [
    Rails.application.config.connect_url,
    Rails.application.config.connector['connector_id']
  ]
  uri = URI.parse(url)

  $CREATED_CANDIDATES.each_with_index do |candidate, index|
    candidate_data = {
      "candidate" => candidate,
      "applications": [{"job_id": "101"}]
    }
    request_body = JSON.generate(candidate_data)
    callback_url = Rails.application.routes.url_for(controller: 'application_processed_callback', action: 'create', app_id: index)
    
    response = ConnectHelper.request_to_connect(
      uri, Net::HTTP::Post, callback_url: callback_url,
      request_body: request_body
    )
  end
end


class IndexController < ApplicationController

  # Our main view with a table showing the email addresses of the candidates
  # we have created, and their current creation status.
  # We also have a table showing any searches we have initiated, and their
  # status.
  # Once the creation status is "Complete" we can search for them by their
  # email using the search box.
  def index
    if $CREATED_CANDIDATES.empty?
      populate_candidates()
      post_candidates_to_connect()
    end

    @candidates = $CREATED_CANDIDATES
    @searches = $SEARCHES
  end
end
