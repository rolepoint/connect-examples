Rails.application.routes.draw do
  #get 'application_processed_callback/create'

  root 'index#index'
  get 'index/index'

  post '/application_processed_callback/:app_id', to: 'application_processed_callback#create', as: :application_processed_callback

  post '/search', to: 'search#create', as: :do_search
  post '/search_complete_callback/:id', to: 'search_complete_callback#create', as: :search_complete

  get '/get_candidate/:search_id/:candidate_id', to: 'get_candidate#show', as: :get_candidate
  post '/get_candidate_complete_callback/:search_id', to: 'get_candidate_complete_callback#create', as: :get_candidate_complete_callback
end
