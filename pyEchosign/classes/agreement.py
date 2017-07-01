import json
import logging
from enum import Enum
from typing import TYPE_CHECKING


import arrow

import requests

from .users import UserEndpoints

from pyEchosign.utils import endpoints
from pyEchosign.utils.request_parameters import get_headers
from pyEchosign.utils.handle_response import check_error, response_success

log = logging.getLogger('pyEchosign.' + __name__)

if TYPE_CHECKING:
    from .account import EchosignAccount


class Agreement(object):
    """ Represents a created agreement in Echosign.
    
    Attributes:
        account (EchosignAccount): An instance of :class:`EchosignAccount <pyEchosign.classes.account.EchosignAccount>`. All Agreement actions will be conducted under this account.
        fully_retrieved (bool): Whether or not the agreement has all information retrieved, or if only the basic information was pulled (such as when getting all agreements instead of requesting the specific agreement)
        echosign_id (str): The ID assigned to the agreement by Echosign, used to identify the agreement via the API
        name (str): The name of the document as specified by the sender
        status (Agreement.Status): The current status of the document (OUT_FOR_SIGNATURE, SIGNED, APPROVED, etc)
        users (list[DisplayUser]): The users associated with this agreement, represented by :class:`DisplayUser <pyEchosign.classes.users.DisplayUser>`
        
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

        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])

    class Status(Enum):
        """ Possible status of agreements 
        
        Note: 
            Echosign provides 'WAITING_FOR_FAXIN' in their API documentation, so pyEchosign has also included 'WAITING_FOR_FAXING' in case that's just a typo in their documentation. Once it's determined which is used, the other will be removed.
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
            This action requires the 'agreement_retention' scope, which doesn't appear to be actually available via OAuth
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


class AgreementEndpoints(object):
    base_api_url = None

    def __init__(self, account: 'EchosignAccount'):
        self.account = account
        self.api_access_point = account.api_access_point

    def get_agreements(self):
        """ Gets all agreements for the EchosignAccount """
        url = self.api_access_point + endpoints.GET_AGREEMENTS
        r = requests.get(url, headers=get_headers(self.account.access_token))
        response_body = r.json()
        json_agreements = response_body.get('userAgreementList', None)
        # Check if there are errors before proceeding
        if not response_success(r):
            check_error(r)
        agreements = []
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
            agreements.append(new_agreement)
        return agreements
