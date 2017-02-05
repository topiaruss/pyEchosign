from unittest import TestCase
from unittest.mock import Mock, patch

from src.classes.account import EchosignAccount


class TestAccount(TestCase):
    @classmethod
    def setup_class(cls):
        cls.mock_get_patcher = patch('src.classes.account.requests.get')
        cls.mock_get = cls.mock_get_patcher.start()

    def test_account_response(self):
        self.mock_get.return_value.ok = True
        e = EchosignAccount('a string')
        self.assertEqual(e.access_token, 'a string')
