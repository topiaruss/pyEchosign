from unittest import TestCase

from six import StringIO

from pyEchosign.exceptions.echosign import PermissionDenied

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

from pyEchosign.classes.agreement import Agreement
from pyEchosign.classes.account import EchosignAccount
from pyEchosign.exceptions.internal import ApiError


class TestAccount(TestCase):
    @classmethod
    def setup_class(cls):
        cls.mock_get_patcher = patch('pyEchosign.classes.account.requests.get')
        cls.mock_get = cls.mock_get_patcher.start()

        cls.mock_put_patcher = patch('pyEchosign.classes.agreement.requests.put')
        cls.mock_put = cls.mock_put_patcher.start()

        cls.mock_post_patcher = patch('pyEchosign.classes.agreement.requests.post')
        cls.mock_post = cls.mock_post_patcher.start()
        
    def test_cancel_agreement_passes(self):
        mock_response = Mock()

        self.mock_get_patcher = patch('pyEchosign.classes.account.requests.get')
        self.mock_get = self.mock_get_patcher.start()

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

        self.mock_get_patcher = patch('pyEchosign.classes.account.requests.get')
        self.mock_get = self.mock_get_patcher.start()

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

        with self.assertRaises(PermissionDenied):
            agreement.cancel()

    def test_cancel_agreement_500_raises_error(self):
        """ Test that an invalid response due to an issue with the API, not the package, raises an Exception """
        mock_response = Mock()

        self.mock_get_patcher = patch('pyEchosign.classes.account.requests.get')
        self.mock_get = self.mock_get_patcher.start()

        account = EchosignAccount('an invalid string')
        account.api_access_point = 'http://echosign.com'

        agreement = Agreement(account=account)
        agreement.name = 'Test Agreement'
        agreement.fully_retrieved = False
        agreement.echosign_id = '123'
        agreement.date = '2017-02-19T08:22:34-08:00'

        mock_response.status_code = 500
        # Assign our mock response as the result of our patched function
        self.mock_put.return_value = mock_response

        with self.assertRaises(ApiError):
            agreement.cancel()

    def test_delete_agreement_passes(self):
        mock_response = Mock()

        self.mock_get_patcher = patch('pyEchosign.classes.account.requests.get')
        self.mock_get = self.mock_get_patcher.start()

        account = EchosignAccount('an invalid string')
        account.api_access_point = 'http://echosign.com'

        agreement = Agreement(account=account)
        agreement.name = 'Test Agreement'
        agreement.fully_retrieved = False
        agreement.echosign_id = '123'
        agreement.date = '2017-02-19T08:22:34-08:00'

        mock_response.status_code = 200
        # Assign our mock response as the result of our patched function
        self.mock_put.return_value = mock_response

        agreement.cancel()

    def test_delete_agreement_401_raises_error(self):
        mock_response = Mock()

        self.mock_get_patcher = patch('pyEchosign.classes.account.requests.get')
        self.mock_get = self.mock_get_patcher.start()

        account = EchosignAccount('an invalid string')
        account.api_access_point = 'http://echosign.com'

        agreement = Agreement(account=account)
        agreement.name = 'Test Agreement'
        agreement.fully_retrieved = False
        agreement.echosign_id = '123'
        agreement.date = '2017-02-19T08:22:34-08:00'

        mock_response.status_code = 401
        # Assign our mock response as the result of our patched function
        self.mock_put.return_value = mock_response

        with self.assertRaises(PermissionDenied):
            agreement.cancel()

    def test_create_agreement(self):
        json_response = dict(userAgreementList=[dict(displayDate='2017-09-09T09:33:53-07:00', esign=True, displayUserSetInfos=[
            {'displayUserSetMemberInfos': [{'email': 'test@email.com'}]}], agreementId='123', name='test_agreement',
                             latestVersionId='v1', status='WAITING_FOR_MY_SIGNATURE')])

        mock_response = Mock()

        self.mock_get_patcher = patch('pyEchosign.classes.account.requests.get')
        self.mock_get = self.mock_get_patcher.start()

        account = EchosignAccount('account')
        account.api_access_point = 'http://echosign.com'
        mock_response.json.return_value = json_response
        mock_response.status_code = 200

        mock_agreement_get_patcher = patch('pyEchosign.classes.agreement.requests.get')
        mock_agreement_get = mock_agreement_get_patcher.start()

        mock_agreement_get.return_value = mock_response

        agreements = account.get_agreements()
        agreements = list(agreements)

        self.assertEqual(len(agreements), 1)
        self.assertEqual(agreements[0].name, 'test_agreement')

        # Reset the patch for the Account - otherwise exceptions will ensue

        self.mock_get_patcher = patch('pyEchosign.classes.account.requests.get')
        self.mock_get = self.mock_get_patcher.start()
        
    def test_send_reminder(self):
        """ Test that reminders are sent without exceptions """
        mock_response = Mock()
        
        account = EchosignAccount('account')
        account.api_access_point = 'http://echosign.com'
        mock_response.status_code = 200

        self.mock_post.return_value = mock_response

        agreement = Agreement(account=account)
        agreement.name = 'Test Agreement'
        agreement.fully_retrieved = False
        agreement.echosign_id = '123'
        agreement.date = '2017-02-19T08:22:34-08:00'

        agreement.send_reminder()

        agreement.send_reminder('Test')

        agreement.send_reminder(None)

    def test_get_form_data(self):
        """ Test that form data is retrieved and returned correctly """
        mock_response = Mock()

        account = EchosignAccount('account')
        account.api_access_point = 'http://echosign.com'
        mock_response.status_code = 200

        agreement = Agreement(account=account)
        agreement.name = 'Test Agreement'
        agreement.fully_retrieved = False
        agreement.echosign_id = '123'
        agreement.date = '2017-02-19T08:22:34-08:00'

        mock_response.text = 'Column,Column2,Column3'
        mock_response.status_code = 200

        mock_get_patcher = patch('pyEchosign.classes.agreement.requests.get')
        mock_get = mock_get_patcher.start()

        mock_get.return_value = mock_response

        form_data = agreement.get_form_data()

        self.assertIsInstance(form_data, StringIO)

        data = form_data.read()
        self.assertEqual(data, mock_response.text)

        mock_get_patcher.stop()