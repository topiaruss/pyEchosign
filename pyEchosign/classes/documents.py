from io import IOBase

import logging
from typing import TYPE_CHECKING

import requests
import arrow

from pyEchosign.utils.endpoints import CREATE_TRANSIENT_DOCUMENT
from pyEchosign.utils.request_parameters import get_headers
from pyEchosign.utils.handle_response import check_error, response_success

log = logging.getLogger('pyEchosign.' + __name__)
if TYPE_CHECKING:
    from .account import EchosignAccount


class TransientDocument(object):
    """
    A document which can be used in Agreements - is deleted by Echosign after 7 days.
    
    Attributes:
        file_name: The name of the file
        file: The actual file object to upload to Echosign
        mime_type: The MIME type of the file
        document_id: The ID provided by Echosign, used to reference it in creating agreements
        expiration_date: The date Echosign will delete this document (not provided by Echosign, calculated for convenience
    """
    def __init__(self, account: 'EchosignAccount', file_name: str, file: IOBase, mime_type: str):
        self.file_name = file_name
        self.file = file
        self.mime_type = mime_type

        self.document_id = None
        self.expiration_date = None

        # With file data provided, make request to Echosign API for transient document
        url = account.api_access_point + CREATE_TRANSIENT_DOCUMENT
        # Create post_data
        files = dict(File=(file_name, file, mime_type))
        r = requests.post(url, headers=get_headers(account.access_token), files=files)

        if response_success(r):
            log.debug('Request to create document {} successful.'.format(self.file_name))
            response_data = r.json()
            self.document_id = response_data.get('transientDocumentId', None)
            # If there was no document ID, something went wrong
            if self.document_id is None:
                log.error('Did not receive a transientDocumentId from Echosign. Received: {}'.format(r.content))
                # TODO raise an exception here?
            else:
                today = arrow.now()
                # Document will expire in 7 days from creation
                self.expiration_date = today.replace(days=+7).datetime
        else:
            try:
                log.error('Error encountered creating document {}. Received message: {}'.
                          format(self.file_name, r.content))
            finally:
                check_error(r)

    def __str__(self):
        return self.file_name


class RecipientInfo(object):
    email: str = None
    fax: str = None
    role = None
    private_message: str = None
    signing_order: int = None

    # Acceptable Options for role
    SIGNER = 'SIGNER'
    APPROVER = 'APPROVER'
    ACCEPTOR = 'ACCEPTOR'
    FORM_FILLER = 'FORM_FILLER'
    CERTIFIED_RECIPIENT = 'CERTIFIED_RECIPIENT'
    DELEGATE_TO_SIGNER = 'DELEGATE_TO_SIGNER'
    DELEGATE_TO_APPROVER = 'DELEGATE_TO_APPROVER'
    DELEGATE_TO_ACCEPTOR = 'DELEGATE_TO_ACCEPTOR'
    DELEGATE_TO_FORM_FILLER = 'DELEGATE_TO_FORM_FILLER'
    DELEGATE_TO_CERTIFIED_RECIPIENT = 'DELEGATE_TO_CERTIFIED_RECIPIENT'


class FileInfo(object):
    """ Used with DocumentCreationInfo to specify which documents should be used in an agreement. One of the following
    arguments must be provided.

    Attributes:
        library_document_id: "The ID for a library document that is available to the sender"
        library_document_name: "The name of a library document that is available to the sender"
        transient_document: A :class:`TransientDocument` (or ID) to use in the agreement

    """
    library_document_id: str = None
    library_document_name: str = None
    transient_document = None
    web_file: dict = None

    def __init__(self, *args, **kwargs):
        self.library_document_id = kwargs.pop('library_document_id', None)
        self.library_document_name = kwargs.pop('library_document_name', None)
        self.transient_document = kwargs.pop('transient_document', None)
        self.web_file = kwargs.pop('web_file', None)


class DocumentCreationInfo(object):
    files_info: list = []
    name: str = None
    signature_type: str = 'ESIGN'
    callback_info: str = None
    cc: list = []
    days_until_signing_deadline: int = None
    external_id: str = None
    locale: str = None
    message: str = None
    reminder_frequency: str = None
    signature_flow: str = None


class AgreementCreator(object):
    pass
