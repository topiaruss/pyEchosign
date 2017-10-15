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

## Agreements
Agreements represent one agreement in Echosign, which can be composed of multiple documents.

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
>>> Some Agreement Title with the Word query In It
```
