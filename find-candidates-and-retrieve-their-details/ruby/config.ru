# This file is used by Rack-based servers to start the application.

require_relative 'config/boot'

Rails.application.initialize!

Rails.application.routes.default_url_options = { :host => 'http://' + Rails.application.config.connector['ngrok_url'] }

run Rails.application
