# Load the rails application
require File.expand_path('../application', __FILE__)

# Initialize the rails application
Gamecast::Application.initialize!

Gamecast::Application.configure do
  config.my_setting = YAML.load_file(File.join(Rails.root, "config", "application.yml"))[Rails.env]
end