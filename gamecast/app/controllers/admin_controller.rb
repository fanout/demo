require "json"
require "net/http"
require "uri"

class AdminController < ApplicationController
  respond_to :html, :xml, :json

  def index
  end

  def create
    data = { 'team' => params[:team], 'score' => params[:score] }
    realm = Rails.application.config.my_setting['fanout']['realm']

    uri = URI.parse("http://api.fanout.io/realm/%{realm}/publish/%{channel}/" % 
        { :realm => realm, :channel => 'gamecast-score' })

    http = Net::HTTP.new(uri.host, uri.port)
    request = Net::HTTP::Post.new(uri.request_uri)
    request["Authorization"] = "Bearer #{AdminHelper.make_token()}"
    request.body = JSON.dump({"items" => [{"fpp" => data}]})
    request["Content-Type"] = "application/json"
    response = http.request(request)

    puts '********'
    puts response
    puts response.body

    # Send the response
    respond_to do |format|
      format.html # create.html.erb
      format.json { render json: {} }
    end
  end
end
