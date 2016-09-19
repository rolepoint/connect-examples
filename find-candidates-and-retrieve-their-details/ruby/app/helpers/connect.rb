module ConnectHelper
  def ConnectHelper.request_to_connect(uri, http_class, callback_url: nil, request_body: nil)
    puts 'request_to_connect() with request_body %s and callback_url %s' % [request_body, callback_url]
    response = Net::HTTP.start(uri.host, uri.port, :use_ssl => true) do |http|
      request = http_class.new(uri)
      request.basic_auth(
        Rails.application.config.connector["username"],
        Rails.application.config.connector["password"]
      )

      request.add_field('content-type', 'application/rolepoint.v2+json')
      if callback_url
        request.add_field('x-rolepoint-callback-url', callback_url)
      end

      if request_body
        request.body = request_body
      end

      http.request(request)
    end

    return response
  end
end
