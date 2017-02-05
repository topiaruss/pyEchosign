from io import IOBase


class TransientDocument(object):
    def __init__(self, file_name: str, file: IOBase):
        self.file_name = file_name
        self.file = file

    def __str__(self):
        return self.file_name

    document_id = None


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
    Kwargs:
        library_document_id: "The ID for a library document that is available to the sender"
        library_document_name: "The name of a library document that is available to the sender"
        transient_document: A ::class::TransientDocument (or ID) to use in the agreement
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
