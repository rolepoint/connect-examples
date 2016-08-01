require_relative '../helpers/connect'

class GetCandidateController < ApplicationController

  # An endpoint to retrieve found candidate details from Connect.
  def show
    # We can choose to either include a callback header with our
    # request, or to poll until the search is complete. Here
    # we use the callback functionality.
    
    uri = URI.parse("%s/v1/%s/candidate/%s" % [
      Rails.application.config.connect_url,
      Rails.application.config.connector['connector_id'],
      params[:candidate_id]
    ])

    callback_url = Rails.application.routes.url_for(controller: 'get_candidate_complete_callback',action: 'create', search_id: params[:search_id])

    resp = ConnectHelper.request_to_connect(uri, Net::HTTP::Get, callback_url: callback_url)
    
    $SEARCHES[params[:search_id].to_i]['get_candidate_status'] = 'In Progress'

    redirect_to '/'
  end
end
