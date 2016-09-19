class ApplicationProcessedCallbackController < ApplicationController
  skip_before_filter  :verify_authenticity_token

  # An endpoint for handling Connect candidate callbacks. Here we update our
  # entry with the status.
  def create
    $CREATED_CANDIDATES[params[:app_id].to_i]['status'] = params[:status] 
  end
end
