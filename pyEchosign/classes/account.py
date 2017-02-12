import logging

import requests

from pyEchosign.classes import agreement
from pyEchosign.utils import endpoints
from pyEchosign.utils.request_parameters import get_headers

log = logging.getLogger('pyOutlook - {}'.format(__name__))


class EchosignAccount(object):
    """ Saves OAuth Information for connecting to Echosign
    
    Attributes:
        access_token: The OAuth Access token to use for authenticating to Echosign
        user_id: The ID of the user to specify as the API caller, if not provided the caller is inferred from the token
        user_email: The email of the user to specify as the API caller, if not provided the caller is inferred from the token
        api_access_point: The API endpoint used as a base for all API calls
    """
    def __init__(self, access_token: str, **kwargs):
        self.access_token = access_token
        self.user_id = kwargs.pop('user_id', None)
        self.user_email = kwargs.pop('user_email', None)

        log.debug('EchosignAccount instantiated. Requesting base_uris from API...')
        headers = {'Access-Token': access_token}
        response = requests.get(endpoints.BASE_URIS, headers=headers)
        response_body = response.json()
        log.debug('Received status code {} from Echosign API'.format(response.status_code))
        self.api_access_point = response_body.get('api_access_point') + endpoints.API_URL_EXTENSION

    access_token = None

    def get_agreements(self):
        """ Gets all agreements for the EchosignAccount 
        
        Returns: A list of :class:`Agreement <pyEchosign.classes.agreement.Agreement>` objects
        """
        return AgreementEndpoints(self).get_agreements()


class AgreementEndpoints(object):
    base_api_url = None

    def __init__(self, account: EchosignAccount):
        self.account = account
        self.api_access_point = account.api_access_point

    def get_agreements(self):
        """ Gets all agreements for the EchosignAccount """
        url = self.api_access_point + endpoints.GET_AGREEMENTS
        r = requests.get(url, headers=get_headers(self.account.access_token))
        response_body = r.json()
        json_agreements = response_body.get('userAgreementList', None)

        agreements = []
        for json_agreement in json_agreements:
            echosign_id = json_agreement.get('agreementId', None)
            name = json_agreement.get('name', None)
            status = json_agreement.get('status', None)
            new_agreement = agreement.Agreement(echosign_id=echosign_id, name=name, account=self.account, status=status)
            agreements.append(new_agreement)
        return agreements
