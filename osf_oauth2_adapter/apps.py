import os

from django.apps import AppConfig


class OsfOauth2AdapterConfig(AppConfig):
    name = 'osf_oauth2_adapter'

    api_url = 'https://localhost:8000'
    accounts_url = 'https://localhost:8080'

    if os.environ.get('BACKEND') == 'stage':
        api_url = 'https://staging-api.osf.io'
        accounts_url = 'https://staging-accounts.osf.io'
    if os.environ.get('BACKEND') == 'prod':
        api_url = 'https://api.osf.io'
        accounts_url = 'https://accounts.osf.io'

    osf_api_url = os.environ.get('OSF_API_URL', api_url).rstrip('/') + '/'
    osf_accounts_url = os.environ.get('OSF_ACCOUNTS_URL', accounts_url).rstrip('/') + '/'
    default_scopes = ['osf.full_write']
    humans_group_name = 'OSF_USERS'
