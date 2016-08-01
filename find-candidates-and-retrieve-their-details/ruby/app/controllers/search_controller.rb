class SearchController < ApplicationController
  skip_before_filter  :verify_authenticity_token

  # An endpoint for searching Connect for candidates by their email address.
  def create
    $SEARCHES.push({
      "query" => params[:query],
      "candidate_ids" => nil,
      "search_status" => "In progress",
      "get_candidate_status" => "Not Started",
      "candidate_details" => nil
    })

    # We build our query using the Connect find_candidates schema.
    # We can stack as many filters as we like here, but for this example we
    # only show filtering by email address.
    query = JSON.generate(
      {'filters': [{'field': 'email', 'operator': '==', 'value': params[:query]}]}
    )
    
    # We can choose to either include a callback header with our
    # request, or to poll until the search is complete. Here
    # we use the callback functionality.
    uri = URI.parse("%s/v1/%s/find_candidates" % [
      Rails.application.config.connect_url,
      Rails.application.config.connector['connector_id']
    ])

    search_id = $SEARCHES.length - 1
    callback_url = Rails.application.routes.url_for(
      controller: 'search_complete_callback', action: 'create', id: search_id)

    resp = ConnectHelper.request_to_connect(
      uri, Net::HTTP::Post, callback_url: callback_url, request_body: query)

    redirect_to '/'
  end
end
