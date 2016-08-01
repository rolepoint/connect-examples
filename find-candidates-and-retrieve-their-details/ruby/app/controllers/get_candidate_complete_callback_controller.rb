require_relative '../helpers/connect'

class GetCandidateCompleteCallbackController < ApplicationController
  skip_before_filter  :verify_authenticity_token

  # An endpoint for handling Connect get_candidate callbacks.
  #  Here we update our Search with the status or the get_candidate query,
  #  and the final result of retireving the candidate.
  def create
    search_id = params[:search_id].to_i
    $SEARCHES[search_id]['get_candidate_status'] = params[:status]

    # We get the result of the get_candidate call.
    if params[:status] == 'complete'
      uri = URI(params[:result_info][:url])
      response = ConnectHelper.request_to_connect(uri, Net::HTTP::Get)
      $SEARCHES[search_id]['candidate_details'] = JSON.parse(response.body)
    end
  end
end
