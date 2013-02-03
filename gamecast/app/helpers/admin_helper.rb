require "base64"
require "jwt"
require "Time"

module AdminHelper

  # Make a JWT token to connect to Fanout
  def self.make_token
    # Get environment data
    realm = Rails.application.config.my_setting['fanout']['realm']
    realm_key = Rails.application.config.my_setting['fanout']['realm_key']
    # Build and return the token
    claim = { "iss" => realm, "exp" => Time.now.to_i + 3600 }
    key = Base64.decode64(realm_key)
    return JWT.encode(claim, key)
  end

end
