require_relative '../helpers/connect'

class SearchCompleteCallbackController < ApplicationController
  skip_before_filter  :verify_authenticity_token

  # An endpoint for handling Connect find_candidates callbacks.
  # Here we update our Search with the status or the search, and the found
  # candidate_ids.
  def create
    $SEARCHES[params[:id].to_i]['search_status'] = params[:status]

    # We get the result of the search
    if params[:status] == 'complete'
      uri = URI(params[:result_info][:url])
      resp = ConnectHelper.request_to_connect(uri, Net::HTTP::Get)
      $SEARCHES[params[:search_id].to_i]['candidate_ids'] = JSON.parse(resp.body)['candidate_ids']
    end
  end
end
