from unittest.mock import Mock, patch

import requests
from nose.tools import assert_true

from src.utils.endpoints import BASE_URIS


@patch('src.classes.account.EchosignAccount')
def test_account_response():
    response = requests.get(BASE_URIS, '3AAABLblqZhBWbz3nSrgyuVwQsBqSQ42mG5THFMZwKE-OVxGDksmFJhG_yKNmZNItSjLrH4Zq5zen6b08VwNQaez1cWEWMBgJ')
    assert_true(response.ok)