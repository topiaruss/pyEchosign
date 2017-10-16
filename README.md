[![PyPI](https://img.shields.io/pypi/v/pyEchosign.svg)](https://pypi.python.org/pypi/pyEchosign)
[![PyPI](https://img.shields.io/pypi/pyversions/pyEchosign.svg)](https://pypi.python.org/pypi/pyEchosign)
[![Documentation Status](https://readthedocs.org/projects/pyechosign/badge/?version=stable)](http://pyechosign.readthedocs.io/en/stable/?badge=stable)

# Maintained on GitLab
This project is maintained on [GitLab](https://gitlab.com/jensastrup/pyEchosign) and mirrored to [GitHub](https://github.com/JensAstrup/pyEchosign). Issues opened on the latter are still addressed.

# pyEchosign
A Python module for connecting to the Adobe Echosign REST API, without the hassle of dealing with the JSON formatting for requests/responses and the REST endpoints and their varying requirements

The most up to date documentation can be found on [pyEchosign's RTD page](http://pyEchosign.readthedocs.io/en/latest/).

# Quickstart

## Account Instantiation
In order to interact with the API, you need to create an instance of `EchosignAccount`, which will allow you to send/retrieve
agreements, documents, etc.

Note that this module does not handle the OAuth process, gaining an access token must be done outside of this module.

```python 
from pyEchosign import *

token = 'My Access Token'
account = EchosignAccount(token)

# When the access token is refreshed
account.access_token = 'new access token'
```

## Sending Agreements

```python 
from pyEchosign import *

account = EchosignAccount('')

agreement = Agreement(account, name='My Agreement')

# MIME type is optional - it will be inferred from the file extension by Adobe if not provided
file = TransientDocument(account, 'To be Signed.pdf', 'some bytes', 'application/pdf')
agreement.files = [file]

# If your document utilizes merge fields, you can specify which fields should be merged with what values. 
# If you have no idea what this is, just ignore it - it's not required :)
merge_fields = [dict(fieldName='some_field_name', defaultValue='some default value')]

recipients = [Recipient('dude@gmail.com'), Recipient('i_sign_second@gmail.com')]

agreement.send(recipients, merge_fields=merge_fields, ccs=['please_cc_me@gmail.com'])

```

### get_agreements()
This method retrieves the most recent 9 agreements from the account. A query can be specified to search through the 
account's agreements.

```python 
from pyEchosign import *

account = EchosignAccount('')

agreements = account.get_agreements()
agreements[0]
>>> Some Agreement Title

agreements = account.get_agreements('query')
agreements[0]
>>> 'Some Agreement Title with the Word query In It'
```

### Manage Agreements
You can either cancel an agreement, which will make it still visible on the user's Manage page, or delete it which 
removes it entirely.

```python
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

```

# Notes

## JSON Deserialization
Most classes contain two methods to facilitate the process of receiving JSON from the REST API and turning that into 
Python classes. One, `json_to_X()` will handle the JSON formatting for a single instance, while the second - 
`json_to_Xs()` processes JSON for multiple instances. Generally, the latter is simply returning a list comprehension that
calls the former.

While this is primarily useful for internal purposes - every method retrieving an `Agreement` from the API will call
`Agreement.json_to_agreement()` for example - the methods are not private and available for use. Any changes to their 
interface will only be made following deprecation warnings.

## Internal Methods and Classes
All protected and private methods; and any classes, functions, or methods found under `pyEchosign.utils` are subject to 
change without deprecation warnings however.  