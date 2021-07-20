Quickstart
==========

Account Instantiation
---------------------

In order to interact with the API, you need to create an instance of
``EchosignAccount``, which will allow you to send/retrieve agreements,
documents, etc.

Note that this module does not handle the OAuth process, gaining an
access token must be done outside of this module.

.. code:: python

    from pyEchosign import *

    token = 'My Access Token'
    account = EchosignAccount(token)

    # When the access token is refreshed
    account.access_token = 'new access token'

Sending Agreements
------------------

.. code:: python

    from pyEchosign import *

    account = EchosignAccount('')

    agreement = Agreement(account, name='My Agreement')

    # MIME type is optional - it will be inferred from the file extension by Adobe if not provided
    file = TransientDocument(account, 'To be Signed.pdf', 'some bytes', 'application/pdf')
    agreement.files = [file]

    # If your document utilizes merge fields, you can specify which fields should be merged with what values.
    # If you have no idea what this is, just ignore it - it's not required :)
    merge_fields = [dict(field_name='some_field_name', default_value='some default value')]

    recipients = [RecipientInfo('dude@gmail.com'), RecipientInfo('i_sign_second@gmail.com')]

    agreement.send(recipients, merge_fields=merge_fields, ccs=['please_cc_me@gmail.com'])

Retrieving Agreements
---------------------

This method retrieves the most recent 9 agreements from the account. A
query can be specified to search through the account’s agreements.

.. code:: python

    from pyEchosign import *

    account = EchosignAccount('')

    agreements = account.get_agreements()
    agreements[0]
    >>> Some Agreement Title

    agreements = account.get_agreements('query')
    agreements[0]
    >>> 'Some Agreement Title with the Word query In It'

Manage Agreements
-----------------

You can either cancel an agreement, which will make it still visible on
the user’s Manage page, or delete it which removes it entirely.

.. code:: python

    from pyEchosign import *

    account = EchosignAccount('')

    agreements = account.get_agreements()
    agreement = agreements[0]

    print(agreement.status)
    >>> Agreement.Status.OUT_FOR_SIGNATURE

    agreement.cancel()
    # Still visible, but no longer waiting for signature

    print(agreement.status)
    >>> Agreement.Status.RECALLED

    agreement.delete()
    # and now it's gone
