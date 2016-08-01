ENV['BUNDLE_GEMFILE'] ||= File.expand_path('../Gemfile', __dir__)

require 'bundler/setup' # Set up gems listed in the Gemfile.

require "active_model/railtie"
# require "active_record/railtie"  # Do not use ActiveRecord (no DB)
require "action_controller/railtie"
require "action_mailer/railtie"
require "action_view/railtie"
require "sprockets/railtie"
require "rails/test_unit/railtie"

# Require the gems listed in Gemfile
Bundler.require(*Rails.groups)

module Webapp
  class Application < Rails::Application
    ngrok_url = ""  # Fill in with your ngrok URL (e.g 38gbvy74.ngrok.io)
    
    config.connector = {
      "username" => "",  # Fill in with Connector username
      "password" => "",  # Fill in with Connector password
      "connector_id" => "",  # Fill in with Connector ID
      "ngrok_url" => ngrok_url
    }

    config.connect_url = 'https://api.rolepoint-connect.com'
  end
end
