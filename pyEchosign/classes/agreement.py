import json
import logging
from collections import namedtuple
from typing import TYPE_CHECKING, List, Dict

import arrow

import requests
from six import StringIO, BytesIO

from pyEchosign.classes.documents import AgreementDocument
from pyEchosign.exceptions.internal import ApiError
from pyEchosign.utils.utils import find_user_in_list
from .users import User

from pyEchosign.utils.request_parameters import get_headers
from pyEchosign.utils.handle_response import check_error, response_success

log = logging.getLogger('pyEchosign.' + __name__)

if TYPE_CHECKING:
    from .account import EchosignAccount

__all__ = ['Agreement']


class Agreement(object):
    """ Represents either a created agreement in Echosign, or one built in Python which can be sent through, and created
    in Echosign.

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

    def __init__(self, account, **kwargs):
        # type: (EchosignAccount) -> None
        self.account = account
        self.fully_retrieved = kwargs.pop('fully_retrieved', None)
        self.echosign_id = kwargs.pop('echosign_id', None)
        self.name = kwargs.pop('name', None)
        self.date = kwargs.pop('date', None)
        self.users = kwargs.pop('users', [])
        self.formFieldLayerTemplates = kwargs.pop('templates', [])
        status = kwargs.pop('status', None)
        if status is not None:
            self.status = self.Status.__getattribute__(self.Status, status)
            # Used for the creation of Agreements in Echosign
        self.files = kwargs.pop('files', [])

        self._documents = None
        self._signing_url = None
        self.signers = []
        self.templates = []

    def __str__(self):
        if self.name is not None:
            return 'Echosign Agreement: {}'.format(self.name)
        elif self.echosign_id is not None:
            return 'Echosign Agreement: {}'.format(self.echosign_id)
        else:
            return super(Agreement, self).__str__()

    def __repr__(self):
        return str(self)

    class Status(object):
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
        CANCELLED = 'CANCELLED'
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

    @classmethod
    def json_to_agreement(cls, account, json_data):
        echosign_id = json_data.get('id', None)
        name = json_data.get('name', None)
        status = json_data.get('status', None)
        user_set = json_data.get('displayUserSetMemberInfos', None)
        users = []
        if user_set:
            user_set = user_set[0].get('displayUserSetMemberInfos', None)
            users = User.json_to_users(user_set)
        date = json_data.get('displayDate', None)
        if date is not None:
            date = arrow.get(date)
        new_agreement = Agreement(echosign_id=echosign_id, name=name, account=account, status=status, date=date)
        new_agreement.users = users
        return new_agreement

    @classmethod
    def json_to_agreements(cls, account, json_data):
        json_data = json_data.get('userAgreementList')
        return [cls.json_to_agreement(account, agreement_data) for agreement_data in json_data]

    @property
    def documents(self):
        """ Retrieve the :class:`AgreementDocuments <pyEchosign.classes.documents.AgreementDocument>` associated with
        this agreement. If the files have not already been retrieved, this will result in an additional request to
        the API.

        Returns: A list of :class:`AgreementDocument <pyEchosign.classes.documents.AgreementDocument>`

        """
        # If _documents is None, no (successful) API call has been made to retrieve them
        if self._documents is None:
            url = self.account.api_access_point + 'agreements/{}/documents'.format(self.echosign_id)
            r = requests.get(url, headers=get_headers(self.account.access_token))
            # Raise Exception if there was an error
            check_error(r)
            try:
                data = r.json()
            except ValueError:
                raise ApiError('Unexpected response from Echosign API: Status {} - {}'.format(r.status_code, r.content))
            else:
                self._documents = []

                # Take both sections of documents from the response and turn into AgreementDocuments
                documents = self._document_data_to_document(data.get('documents', []))
                supporting_documents = self._document_data_to_document(data.get('supportingDocuments', []))
                self._documents = documents + supporting_documents

        return self._documents

    @property
    def combined_document(self):
        # type: () -> BytesIO
        """ The PDF file containing all documents within this agreement."""
        endpoint = '{}agreements/{}/combinedDocument'.format(self.account.api_access_point, self.echosign_id)

        response = requests.get(endpoint, headers=get_headers(self.account.access_token))
        check_error(response)

        return BytesIO(response.content)

    @property
    def audit_trail_file(self):
        # type: () -> BytesIO
        """ The PDF file of the audit trail."""
        endpoint = '{}agreements/{}/auditTrail'.format(self.account.api_access_point, self.echosign_id)

        response = requests.get(endpoint, headers=get_headers(self.account.access_token))
        check_error(response)

        return BytesIO(response.content)

    @property
    def form_fields(self):
        endpoint = '{}agreements/{}/formFields'.format(self.account.api_access_point, self.echosign_id)

        response = requests.get(endpoint, headers=get_headers(self.account.access_token))
        check_error(response)

        return response.json()

    @staticmethod
    def _document_data_to_document(json_data):
        # type: (dict) -> list
        """ Coverts JSON received from API into an AgreementDocument and appends to Agreement.documents """
        documents = []
        for document_data in json_data:
            # Documents and Supporting Documents are not mixed together - we could get either ID
            try:
                echosign_id = document_data.get('documentId')
            except KeyError:
                echosign_id = document_data.get('supportingDocumentId')

            mime_type = document_data.get('mimeType')
            name = document_data.get('name')
            page_count = document_data.get('numPages')
            document = AgreementDocument(echosign_id, mime_type, name, page_count)

            # If this is a supporting document, there will be a field name
            field_name = document_data.get('fieldName', None)

            if field_name is not None:
                document.field_name = field_name

            documents.append(document)

        return documents

    def add_signer(self, recipients):
        """ Adds signer(s) to this agreement.
            Each call adds another signer.
            If multiple recipients are passed in, ANY of the recipients can sign at this step.

            Example:
                add_signer([User1]) - User1 signs first
                add_signer([User2, User3]) - After User1 signs, EITHER User2 or User3 can sign.

        Args:
            recipients: A list of :class:`Users <pyEchosign.classes.users.User>` or a single User.
        """
        if not isinstance(recipients, list):
            recipients = [recipients]
        recipient_set_info = dict(memberInfos=[dict(email=recipient.email) for recipient in recipients],
                                  order=len(self.signers) + 1,
                                  role="SIGNER")
        self.signers.append(recipient_set_info)

    def add_field_layer_template(self, documents):
        """ Adds the field layer template to this agreement.
         Args:
            documents: A list of :class:`LibraryDocument <pyEchosign.classes.library_document.LibraryDocument>` or a
            single LibraryDocument.
        """
        if not isinstance(documents, list):
            documents = [documents]

        for document in documents:
            if document.form_field_layer:
                self.templates.append({'libraryDocumentId': document.echosign_id})

    def cancel(self):
        """ Cancels the agreement on Echosign. Agreement will still be visible in the Manage page. """
        url = '{}agreements/{}/state'.format(self.account.api_access_point, self.echosign_id)
        body = dict(state='CANCELLED')
        r = requests.put(url, headers=get_headers(self.account.access_token), data=json.dumps(body))

        if response_success(r):
            log.debug('Request to cancel agreement {} successful.'.format(self.echosign_id))

        else:
            try:
                log.error('Error encountered cancelling agreement {}. Received message: {}'.format(self.echosign_id,
                                                                                                   r.content))
            finally:
                check_error(r)

    def hide(self):
        """ Hides the agreement on Echosign. Agreement will not be visible in the Manage page. """
        url = self.account.api_access_point + 'agreements/' + self.echosign_id + '/me/visibility'
        payload = dict(visibility='HIDE')
        r = requests.put(url, data=json.dumps(payload), headers=get_headers(self.account.access_token))

        if response_success(r):
            log.debug('Request to delete agreement {} successful.'.format(self.echosign_id))
        else:
            try:
                log.error('Error encountered deleting agreement {}. Received message:{}'.format(self.echosign_id,
                                                                                                r.content))
            finally:
                check_error(r)

    def send(self, recipients=None, agreement_name=None, ccs=None, external_id='', message='', merge_fields=None):
        # type: (List[User], str, list, str, str, List[Dict[str, str]]) -> None
        """ Sends this agreement to Echosign for signature

        Args:
            agreement_name: A string for the document name which will appear in the Echosign Manage page, the email
                to recipients, etc. Defaults to the name for the Agreement.
            recipients: A list of :class:`Users <pyEchosign.classes.users.User>`.
                The order which they are provided in the list determines the order in which they sign.
            ccs: (optional) A list of email addresses to be CC'd on the Echosign agreement emails
                (document sent, document fully signed, etc)
            external_id: (optional) "A unique identifier for your transaction...
                You can use the ExternalID to search for your transaction through [the] API"
            merge_fields: (optional) A list of dictionaries, with each one providing the 'field_name' and
                'default_value' keys. The field name maps to the field on the document, and the default value is
                what will be placed inside.
            message: (optional) A message which will be displayed to recipients of the agreement

        Returns:
            A namedtuple representing the information received back from the API. Contains the following attributes

            `agreement_id`
                *"The unique identifier that can be used to query status and download signed documents"*

            `embedded_code`
                *"Javascript snippet suitable for an embedded page taking a user to a URL"*

            `expiration`
                *"Expiration date for autologin. This is based on the user setting, API_AUTO_LOGIN_LIFETIME"*

            `url`
             *"Standalone URL to direct end users to"*

        Raises:
            ApiError: If the API returns an error, such as a 403. The exact response from the API is provided.

        """
        if agreement_name is None:
            agreement_name = self.name

        if ccs is None:
            ccs = []

        cc_info = []
        for cc in ccs:
            cc_info.append(dict(email=cc))

        files_data = [{'transientDocumentId': file.document_id} for file in self.files]

        if merge_fields is None:
            merge_fields = []

        converted_merge_fields = [dict(fieldName=field['field_name'], defaultValue=field['default_value']) for field in
                                  merge_fields]

        if recipients:
            for recipient in recipients:
                self.add_signer(recipient)

        document_creation_info = dict(signatureType="ESIGN", name=agreement_name, state='IN_PROCESS',
                                      ccs=cc_info, externalId=external_id, fileInfos=files_data,
                                      mergeFieldInfo=converted_merge_fields, participantSetsInfo=self.signers,
                                      message=message, formFieldLayerTemplates=self.templates)
        print(document_creation_info)
        url = self.account.api_access_point + 'agreements'
        api_response = requests.post(url, headers=self.account.headers(), data=json.dumps(document_creation_info))

        if response_success(api_response):
            response = namedtuple('Response', ('agreement_id', 'embedded_code', 'expiration', 'url'))

            response_data = api_response.json()
            embedded_code = response_data.get('embeddedCode', None)
            expiration = response_data.get('expiration', None)
            url = response_data.get('url', None)

            response = response(response_data['id'], embedded_code, expiration, url)

            return response

        else:
            check_error(api_response)

    def get_signing_urls(self):
        """ Associate the signing URLs for this agreement with its
        :class:`recipients <pyEchosign.classes.users.User>` """
        endpoint = '{}agreements/{}/signingUrls'.format(self.account.api_access_point, self.echosign_id)
        headers = get_headers(self.account.access_token)
        r = requests.get(endpoint, headers=headers)

        if response_success(r):
            data = r.json()
            url_sets = data['signingUrlSetInfos']

            # Each signing set will have its own URLs
            for set in url_sets:
                urls = set['signingUrls']
                for url in urls:
                    try:
                        email = url['email']
                        # Find the user in this Agreement's list of users that has a matching email
                        matching_user = find_user_in_list(self.users, 'email', email)
                    except KeyError:
                        continue
                    # Set the signing URL for that recipient
                    matching_user._signing_url = url['esignUrl']

    def get_participant_sets(self):
        url = '{}agreements/{}/members'.format(self.account.api_access_point, self.echosign_id)
        response = requests.get(url, headers=self.account.headers())
        check_error(response)
        return response.json().get('participantSets', [])

    def send_reminder(self, comment=''):
        """ Send a reminder for an agreement to the participants.

        Args:
            comment: An optional comment that will be sent with the reminder

        """
        participant_ids = []
        participants = self.get_participant_sets()
        for participant in participants:
            if participant.get('status') == 'WAITING_FOR_MY_SIGNATURE':
                for member in participant.get('memberInfos', []):
                    participant_ids.append(member.get('id'))

        url = '{}agreements/{}/reminders'.format(self.account.api_access_point, self.echosign_id)

        payload = dict(recipientParticipantIds=participant_ids, status='ACTIVE', note=comment)

        r = requests.post(url, data=json.dumps(payload), headers=self.account.headers())

        check_error(r)

    def get_form_data(self):
        """ Retrieves the form data for this agreement as CSV.

        Returns: StringIO

        """
        url = '{}agreements/{}/formData'.format(self.account.api_access_point, self.echosign_id)

        r = requests.get(url, headers=self.account.headers())

        check_error(r)
        return StringIO(r.text)
