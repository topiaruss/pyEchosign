from unittest import TestCase

from mock import patch, Mock

from pyEchosign import TransientDocument
from pyEchosign.classes.agreement import Agreement
from pyEchosign.classes.account import EchosignAccount
from pyEchosign.exceptions.internal import ApiError


class TestAccount(TestCase):
    @classmethod
    def setup_class(cls):
        cls.mock_get_patcher = patch('pyEchosign.classes.account.requests.get')
        cls.mock_get = cls.mock_get_patcher.start()

        cls.mock_put_patcher = patch('pyEchosign.classes.documents.requests.put')
        cls.mock_put = cls.mock_put_patcher.start()

        cls.mock_post_patcher = patch('pyEchosign.classes.documents.requests.post')
        cls.mock_post = cls.mock_post_patcher.start()

    def test_create_transient_document_without_mime_type(self):
        response = Mock()

        response.status_code = 200
        response.json.return_value = dict(transientDocumentId='ABC123')

        self.mock_post.return_value = response

        account = EchosignAccount('a string')
        account.api_access_point = 'http://echosign.com'

        td = TransientDocument(account, 'test.pdf', open('requirements.txt', 'r'))

        self.assertEqual(td.document_id, 'ABC123')

    def test_create_transient_document_with_invalid_response(self):
        response = Mock()

        response.status_code = 200
        response.json.return_value = dict()

        self.mock_post.return_value = response

        account = EchosignAccount('a string')
        account.api_access_point = 'http://echosign.com'

        with self.assertRaises(ApiError):
            td = TransientDocument(account, 'test.pdf', open('requirements.txt', 'r'))