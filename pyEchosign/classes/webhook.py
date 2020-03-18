import logging
import json

from typing import TYPE_CHECKING
from enum import Enum

import requests

from pyEchosign.utils.request_parameters import get_headers
from pyEchosign.utils.handle_response import check_error, response_success

log = logging.getLogger('pyEchosign.' + __name__)

if TYPE_CHECKING:
    from .account import EchosignAccount

__all__ = ['Webhook']


class Webhook(object):
    """ Represents either a created webhook in Echosign, or one built in Python which can be created in Echosign.

    Args:
        account (EchosignAccount): An instance of :class:`EchosignAccount <pyEchosign.classes.account.EchosignAccount>`.
            All Webhook actions will be conducted under this account.

    Keyword Args:
        name (str): Name of this webhook
        applicationName (str): Name of the application
        applicationDisplayName (str): Display name of the application
        status (WebhookStatus | str): ACTIVE or INACTIVE
        webhookSubscriptionEvents (list[WebhookEvent | str]): A list of webhook events to subscribe to.
        lastModified (date): Last modified date
        webhookUrlInfo (dict(url=(str))): The VALID URL of the webhook that properly response with the client id.
        scope (WebhookScore | str): The scope at which this webhook will operate, 'USER', 'GROUP', 'ACCOUNT', etc.
        id (str): The echosign ID of this webhook

    Attributes:
        account (EchosignAccount): An instance of :class:`EchosignAccount <pyEchosign.classes.account.EchosignAccount>`.
            All Webhook actions will be conducted under this account.
        name (str): Name of this webhook
        application_name (str): Name of the application
        application_display_name (str): Display name of the application
        status (WebhookStatus | str): ACTIVE or INACTIVE
        webhook_events (list[WebhookEvent | str]): A list of webhook events to subscribe to.
        last_modified (date): Last modified date
        webhook_url (str): The VALID URL of the webhook that properly response with the client id.
        scope (WebhookScore | str): The scope at which this webhook will operate, 'USER', 'GROUP', 'ACCOUNT', etc.
        id (str): The echosign ID of this webhook
    """

    def __init__(self, account, **kwargs):
        # type: (EchosignAccount) -> None
        self.account = account
        self.name = kwargs.pop('name', None)
        self.application_name = kwargs.pop('applicationName', None)
        self.application_display_name = kwargs.pop('applicationDisplayName', None)
        self.status = kwargs.pop('status', WebhookStatus.ACTIVE)
        self.webhook_events = kwargs.pop('webhookSubscriptionEvents', [])
        self.last_modified = kwargs.pop('lastModified', None)

        self.webhook_url = kwargs.pop('webhookUrlInfo', {}).get('url')
        self.scope = kwargs.pop('scope', None)
        self.id = kwargs.pop('id', None)

    def create_webhook(self, name, scope, webhook_events, webhook_url, app_name=None, app_display_name=None):
        """ Creates a new webhook to notify when documents change.
        Args:
           name (str): The name of the webhook,
           scope (WebhookScope | str) = ['ACCOUNT' or 'GROUP' or 'USER' or 'RESOURCE']: Scope of webhook.
           webhook_events (WebhookEvent[] || str[]): Determines events for which the webhook is triggered.
           webhook_url (str): URL of your webhook.  This must be valid, active, and properly return the client ID.
           app_name (str): Application Name
           app_display_name (str): Application Display Name
        """
        payload = {
            'name': name,
            'scope': scope,
            'state': 'ACTIVE',
            'applicationDisplayName': app_display_name,
            'applicationName': app_name,
            'webhookSubscriptionEvents': webhook_events,
            'webhookUrlInfo': dict(url=webhook_url)
        }
        self.name = name
        self.scope = scope
        self.webhook_events = webhook_events
        self.webhook_url = webhook_url
        self.application_display_name = app_display_name
        self.application_name = app_name
        api_url = self.account.api_access_point + 'webhooks'
        r = requests.post(api_url, headers=get_headers(self.account.access_token), data=json.dumps(payload))
        check_error(r)
        self.id = r.json().get('id')

    def delete(self):
        """ Deletes this webhook.  The webhook ID must be set """
        url = self.account.api_access_point + 'webhooks/' + self.id
        response = requests.delete(url, headers=get_headers(self.account.access_token))
        check_error(response)


class WebhookScope (Enum):
    ACCOUNT = 'ACCOUNT'
    GROUP = 'GROUP'
    USER = 'USER'
    RESOURCE = 'RESOURCE'


class WebhookStatus (Enum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'


class WebhookEvent (Enum):
    AGREEMENT_CREATED = 'AGREEMENT_CREATED'
    AGREEMENT_ACTION_DELEGATED = 'AGREEMENT_ACTION_DELEGATED'
    AGREEMENT_RECALLED = 'AGREEMENT_RECALLED'
    AGREEMENT_REJECTED = 'AGREEMENT_REJECTED'
    AGREEMENT_EXPIRED = 'AGREEMENT_EXPIRED'
    AGREEMENT_ACTION_COMPLETED = 'AGREEMENT_ACTION_COMPLETED'
    AGREEMENT_WORKFLOW_COMPLETED = 'AGREEMENT_WORKFLOW_COMPLETED'
    AGREEMENT_EMAIL_VIEWED = 'AGREEMENT_EMAIL_VIEWED'
    AGREEMENT_MODIFIED = 'AGREEMENT_MODIFIED'
    AGREEMENT_SHARED = 'AGREEMENT_SHARED'
    AGREEMENT_READY_TO_VAULT = 'AGREEMENT_READY_TO_VAULT'
    AGREEMENT_VAULTED = 'AGREEMENT_VAULTED'
    AGREEMENT_ACTION_REQUESTED = 'AGREEMENT_ACTION_REQUESTED'
    AGREEMENT_ACTION_REPLACED_SIGNER = 'AGREEMENT_ACTION_REPLACED_SIGNER'
    AGREEMENT_AUTO_CANCELLED_CONVERSION_PROBLEM = 'AGREEMENT_AUTO_CANCELLED_CONVERSION_PROBLEM'
    AGREEMENT_DOCUMENTS_DELETED = 'AGREEMENT_DOCUMENTS_DELETED'
    AGREEMENT_EMAIL_BOUNCED = 'AGREEMENT_EMAIL_BOUNCED'
    AGREEMENT_KBA_AUTHENTICATED = 'AGREEMENT_KBA_AUTHENTICATED'
    AGREEMENT_OFFLINE_SYNC = 'AGREEMENT_OFFLINE_SYNC'
    AGREEMENT_USER_ACK_AGREEMENT_MODIFIED = 'AGREEMENT_USER_ACK_AGREEMENT_MODIFIED'
    AGREEMENT_UPLOADED_BY_SENDER = 'AGREEMENT_UPLOADED_BY_SENDER'
    AGREEMENT_WEB_IDENTITY_AUTHENTICATED = 'AGREEMENT_WEB_IDENTITY_AUTHENTICATED'
    AGREEMENT_ALL = 'AGREEMENT_ALL'
    MEGASIGN_CREATED = 'MEGASIGN_CREATED'
    MEGASIGN_RECALLED = 'MEGASIGN_RECALLED'
    MEGASIGN_SHARED = 'MEGASIGN_SHARED'
    MEGASIGN_ALL = 'MEGASIGN_ALL'
    WIDGET_CREATED = 'WIDGET_CREATED'
    WIDGET_MODIFIED = 'WIDGET_MODIFIED'
    WIDGET_SHARED = 'WIDGET_SHARED'
    WIDGET_ENABLED = 'WIDGET_ENABLED'
    WIDGET_DISABLED = 'WIDGET_DISABLED'
    WIDGET_AUTO_CANCELLED_CONVERSION_PROBLEM = 'WIDGET_AUTO_CANCELLED_CONVERSION_PROBLEM'
    WIDGET_ALL = 'WIDGET_ALL'
    LIBRARY_DOCUMENT_CREATED = 'LIBRARY_DOCUMENT_CREATED'
    LIBRARY_DOCUMENT_AUTO_CANCELLED_CONVERSION_PROBLEM = 'LIBRARY_DOCUMENT_AUTO_CANCELLED_CONVERSION_PROBLEM'
    LIBRARY_DOCUMENT_MODIFIED = 'LIBRARY_DOCUMENT_MODIFIED'
    LIBRARY_DOCUMENT_ALL = 'LIBRARY_DOCUMENT_ALL'
