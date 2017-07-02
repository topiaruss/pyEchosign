import json
import logging
from collections import namedtuple
from enum import Enum
from typing import TYPE_CHECKING, List

import arrow

import requests

from .users import UserEndpoints, Recipient

from pyEchosign.utils import endpoints
from pyEchosign.utils.request_parameters import get_headers
from pyEchosign.utils.handle_response import check_error, response_success

log = logging.getLogger('pyEchosign.' + __name__)

if TYPE_CHECKING:
    from .account import EchosignAccount


class Agreement(object):
    """ Represents a created agreement in Echosign.

    Args:
        account (EchosignAccount): An instance of :class:`EchosignAccount <pyEchosign.classes.account.EchosignAccount>`.
            All Agreement actions will be conducted under this account.

    Keyword Args:
        fully_retrieved (bool): Whether or not the agreement has all information retrieved,
            or if only the basic information was pulled (such as when getting all agreements instead
            of requesting the specific agreement)
        echosign_id (str): The ID assigned to the agreement by Echosign, used to identify the agreement via the API
        name (str): The name of the document as specified by the sender
        status (Agreement.Status): The current status of the document (OUT_FOR_SIGNATURE, SIGNED, APPROVED, etc)
        users (list[DisplayUser]): The users associated with this agreement, represented by
            :class:`EchosignAccount <pyEchosign.classes.account.EchosignAccount>`
        files (list): A list of :class:`TransientDocument <pyEchosign.classes.documents.TransientDocument>` instances
            which will become the documents within the agreement. This information is not provided when retrieving
            agreements from Echosign.
    
    Attributes:
        account (EchosignAccount): An instance of :class:`EchosignAccount <pyEchosign.classes.account.EchosignAccount>`.
            All Agreement actions will be conducted under this account.
        fully_retrieved (bool): Whether or not the agreement has all information retrieved,
            or if only the basic information was pulled (such as when getting all agreements instead
            of requesting the specific agreement)
        echosign_id (str): The ID assigned to the agreement by Echosign, used to identify the agreement via the API
        name (str): The name of the document as specified by the sender
        status (Agreement.Status): The current status of the document (OUT_FOR_SIGNATURE, SIGNED, APPROVED, etc)
        users (list[DisplayUser]): The users associated with this agreement, represented by
            :class:`EchosignAccount <pyEchosign.classes.account.EchosignAccount>`
        files (list): A list of :class:`TransientDocument <pyEchosign.classes.documents.TransientDocument>` instances
            which will become the documents within the agreement. This information is not provided when retrieving
            agreements from Echosign.
    """

    def __init__(self, account: 'EchosignAccount', **kwargs):
        self.account = account
        self.fully_retrieved = kwargs.pop('fully_retrieved', None)
        self.echosign_id = kwargs.pop('echosign_id', None)
        self.name = kwargs.pop('name', None)
        self.date = kwargs.pop('date', None)

        provided_status = kwargs.pop('provided_status', None)
        if provided_status is not None:
            self.status = self.Status[provided_status]
        else:
            self.status = None

        # Used for the creation of Agreements in Echosign
        self.files = kwargs.pop('files', [])

    class Status(Enum):
        """ Possible status of agreements 
        
        Note: 
            Echosign provides 'WAITING_FOR_FAXIN' in their API documentation, so pyEchosign has also included
            'WAITING_FOR_FAXING' in case that's just a typo in their documentation. Once it's determined
            which is used, the other will be removed.
        """
        WAITING_FOR_MY_SIGNATURE = 'WAITING_FOR_MY_SIGNATURE'
        WAITING_FOR_MY_APPROVAL = 'WAITING_FOR_MY_APPROVAL'
        WAITING_FOR_MY_DELEGATION = 'WAITING_FOR_MY_DELEGATION'
        WAITING_FOR_MY_ACKNOWLEDGEMENT = 'WAITING_FOR_MY_ACKNOWLEDGEMENT'
        WAITING_FOR_MY_ACCEPTANCE = 'WAITING_FOR_MY_ACCEPTANCE'
        WAITING_FOR_MY_FORM_FILLING = 'WAITING_FOR_MY_FORM_FILLING'
        OUT_FOR_SIGNATURE = 'OUT_FOR_SIGNATURE'
        OUT_FOR_APPROVAL = 'OUT_FOR_APPROVAL'
        OUT_FOR_DELIVERY = 'OUT_FOR_DELIVERY'
        OUT_FOR_ACCEPTANCE = 'OUT_FOR_ACCEPTANCE'
        OUT_FOR_FORM_FILLING = 'OUT_FOR_FORM_FILLING'
        SIGNED = 'SIGNED'
        APPROVED = 'APPROVED'
        DELIVERED = 'DELIVERED'
        ACCEPTED = 'ACCEPTED'
        FORM_FILLED = 'FORM_FILLED'
        RECALLED = 'RECALLED'
        # This was directly taken from Echosign
        # not sure if the typo is only in their documentation or also in response. Adding both in case.
        WAITING_FOR_FAXIN = 'WAITING_FOR_FAXIN'
        WAITING_FOR_FAXING = 'WAITING_FOR_FAXING'
        ARCHIVED = 'ARCHIVED'
        FORM = 'FORM'
        EXPIRED = 'EXPIRED'
        WIDGET = 'WIDGET'
        WAITING_FOR_AUTHORING = 'WAITING_FOR_AUTHORING'
        OTHER = 'OTHER'

    def cancel(self):
        """ Cancels the agreement on Echosign. Agreement will still be visible in the Manage page. """
        url = self.account.api_access_point + endpoints.CANCEL_AGREEMENT + self.echosign_id + '/status'
        body = dict(value='CANCEL')
        r = requests.put(url, headers=get_headers(self.account.access_token), data=json.dumps(body))

        if response_success(r):
            log.debug('Request to cancel agreement {} successful.'.format(self.echosign_id))

        else:
            try:
                log.error('Error encountered cancelling agreement {}. Received message: {}'.format(self.echosign_id,
                                                                                                   r.content))
            finally:
                check_error(r)

    def delete(self):
        """ Deletes the agreement on Echosign. Agreement will not be visible in the Manage page. 
        
        Warnings:
            This action requires the 'agreement_retention' scope, which doesn't appear
            to be actually available via OAuth
        """
        url = self.account.api_access_point + endpoints.DELETE_AGREEMENT + self.echosign_id

        r = requests.delete(url, headers=get_headers(self.account.access_token))

        if response_success(r):
            log.debug('Request to delete agreement {} successful.'.format(self.echosign_id))
        else:
            try:
                log.error('Error encountered deleting agreement {}. Received message:{}'.format(self.echosign_id,
                                                                                                r.content))
            finally:
                check_error(r)

    @staticmethod
    def _construct_agreement_request(recipients: List[Recipient]) -> List[dict]:
        recipient_info = []

        for recipient in recipients:
            recipient_info.append(dict(recipientSetMemberInfos=[{
                "fax": "",
                "securityOptions": [{
                    "authenticationMethod": "",
                    "password": "CONTENT FILTERED",
                    "phoneInfos": [{
                        "phone": "",
                        "countryCode": ""
                    }]
                }],
                "email": recipient.email
            }], securityOptions=[{
                "authenticationMethod": "",
                "password": "CONTENT FILTERED",
                "phoneInfos": [{
                    "phone": "",
                    "countryCode": ""
                }]
            }], recipientSetRole="SIGNER"))

        return recipient_info

    def send_agreement(self, agreement_name: str, recipients: List[Recipient]):
        """ Sends this agreement to Echosign for signature

        Args:
            recipients: A list of :class:`Recipients <pyEchosign.classes.users.Recipient>`. The order which they are provided
                in the list determines the order in which they sign.

        Returns: A dict representing the information received back from

        """
        recipients_data = self._construct_agreement_request(recipients)
        response = namedtuple('Response', ('agreement_id', 'embedded_code', 'expiration', 'url'))
        # TODO complete this method...


class AgreementEndpoints(object):
    """ An internal class to handle making calls to the endpoints associated with Agreements.

    Args:
        account: An instance of :class:`EchosignAccount <pyEchosign.classes.account.EchosignAccount>` to be used for all
            API calls
    """
    base_api_url = None

    def __init__(self, account: 'EchosignAccount'):
        self.account = account
        self.api_access_point = account.api_access_point

    def get_agreements(self):
        """ Gets all agreements for the EchosignAccount - making the API call from the first iteration, and
        then yielding each agreement thereafter."""

        json_agreement = None
        if not json_agreement:
            url = self.api_access_point + endpoints.GET_AGREEMENTS
            r = requests.get(url, headers=get_headers(self.account.access_token))
            response_body = r.json()
            json_agreements = response_body.get('userAgreementList', [])

            # Check if there are errors before proceeding
            if not response_success(r):
                check_error(r)

        for json_agreement in json_agreements:
            echosign_id = json_agreement.get('agreementId', None)
            name = json_agreement.get('name', None)
            status = json_agreement.get('status', None)
            user_set = json_agreement.get('displayUserSetInfos', None)[0]
            user_set = user_set.get('displayUserSetMemberInfos', None)
            users = UserEndpoints.get_users_from_bulk_agreements(user_set)
            date = json_agreement.get('displayDate', None)
            if date is not None:
                date = arrow.get(date)
            new_agreement = Agreement(echosign_id=echosign_id, name=name, account=self.account, status=status,
                                      date=date)
            new_agreement.users = users
            yield new_agreement
