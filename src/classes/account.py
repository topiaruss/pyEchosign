import logging

import requests

from utils.endpoints import BASE_URIS
log = logging.getLogger('pyOutlook - {}'.format(__name__))


class EchosignAccount(object):
    """ Saves OAuth Information for connecting to Echosign
    Args:
        access_token = The OAuth Access token to use for authenticating to Echosign
    Keyword Args:
        user_id: The ID of the user to specify as the API caller, if not provided the caller is inferred from the token
        user_email: The email of the user to specify as the API caller, if not provided the caller is inferred from the token
    """
    def __init__(self, access_token: str, **kwargs):
        self.access_token = access_token
        self.user_id = kwargs.pop('user_id', None)
        self.user_email = kwargs.pop('user_email', None)

        log.debug('EchosignAccount instantiated. Requesting base_uris from API...')
        headers = {'Access-Token': access_token}
        response = requests.get(BASE_URIS, headers=headers)
        response_body = response.json()
        log.debug('Received status code {} from Echosign API'.format(response.status_code))
        self.api_access_point = response_body.get('api_access_point')

    access_token = None
