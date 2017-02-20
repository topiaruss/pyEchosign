from unittest import TestCase
from unittest.mock import Mock, patch

from pyEchosign.classes.agreement import Agreement
from pyEchosign.classes.account import EchosignAccount


class TestAccount(TestCase):
    @classmethod
    def setup_class(cls):
        cls.mock_get_patcher = patch('pyEchosign.classes.account.requests.get')
        cls.mock_get = cls.mock_get_patcher.start()

        cls.mock_put_patcher = patch('pyEchosign.classes.agreement.requests.put')
        cls.mock_put = cls.mock_put_patcher.start()

    def test_cancel_agreement_passes(self):
        mock_response = Mock()

        e = EchosignAccount('a string')
        e.api_access_point = 'http://echosign.com'
        agreement = Agreement(account=e)
        agreement.name = 'Test Agreement'
        agreement.fully_retrieved = False
        agreement.echosign_id = '123'
        agreement.date = '2017-02-19T08:22:34-08:00'

        mock_response.status_code = 200
        # Assign our mock response as the result of our patched function
        self.mock_put.return_value = mock_response

        agreement.cancel()

    def test_cancel_agreement_401_raises_error(self):
        mock_response = Mock()

        e = EchosignAccount('an invalid string')
        e.api_access_point = 'http://echosign.com'
        agreement = Agreement(account=e)
        agreement.name = 'Test Agreement'
        agreement.fully_retrieved = False
        agreement.echosign_id = '123'
        agreement.date = '2017-02-19T08:22:34-08:00'

        mock_response.status_code = 401
        # Assign our mock response as the result of our patched function
        self.mock_put.return_value = mock_response

        with self.assertRaises(PermissionError):
            agreement.cancel()
