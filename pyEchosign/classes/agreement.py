import json
import logging
from typing import TYPE_CHECKING
import requests

from pyEchosign.utils import endpoints
from pyEchosign.utils.request_parameters import get_headers
from pyEchosign.utils.handle_response import check_error, response_success

log = logging.getLogger('pyEchosign.' + __name__)
if TYPE_CHECKING:
    from pyEchosign.classes.account import EchosignAccount


class Agreement(object):
    """
    Attributes:
        fully_retrieved: Whether or not the agreement has all information retrieved, or if only the basic information was pulled (such as when getting all agreements instead of requesting the specific agreement)
        id: The ID assigned to the agreement by Echosign, used to identify the agreement via the API
        name: The name of the document as specified by the sender
        status: The current status of the document (OUT_FOR_SIGNATURE, SIGNED, APPROVED, etc)
    """

    def __init__(self, account: 'EchosignAccount', fully_retrieved: bool = False, echosign_id: str = None, name: str = None,
                 status: str = None, *args, **kwargs):
        self.account = account
        self.fully_retrieved = fully_retrieved
        self.id = echosign_id
        self.name = name
        self.status = status

        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])

    def cancel(self):
        """ Cancels the agreement on Echosign. """
        url = self.account.api_access_point + endpoints.CANCEL_AGREEMENT + self.id + '/status'
        body = dict(value='CANCEL')
        r = requests.put(url, headers=get_headers(self.account.access_token), data=json.dumps(body))

        if response_success(r):
            log.debug('Request to cancel agreement {} successful.'.format(self.id))

        else:
            try:
                log.error('Request to cancel agreement {} unsuccessful. Received message: {}'.
                          format(self.id, r.content))
            finally:
                check_error(r)
