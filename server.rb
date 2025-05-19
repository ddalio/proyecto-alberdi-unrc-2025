require 'bundler/setup'
require 'sinatra'
require 'sinatra/activerecord'
require 'sinatra/reloader' if Sinatra::Base.environment == :development
require_relative 'models/user'
require_relative 'models/transaction'

set :views, File.expand_path('../views', __FILE__)
set :public_folder, File.expand_path('../public', __FILE__)

class App < Sinatra::Application
  configure :development do
    enable :logging
    logger = Logger.new(STDOUT)
    logger.level = Logger::DEBUG if development?
    set :logger, logger

    register Sinatra::Reloader
    after_reload do
      logger.info 'Reloaded!!!'
    end
  end

  get '/' do
    erb :landing
  end

  get '/login' do
    erb :login
  end

  get '/register' do
    erb :register
  end
end
