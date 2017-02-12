from unittest import TestCase
from unittest.mock import Mock, patch

from pyEchosign.classes.agreement import Agreement
from pyEchosign.classes.account import EchosignAccount


class TestAccount(TestCase):
    @classmethod
    def setup_class(cls):
        cls.mock_get_patcher = patch('pyEchosign.classes.account.requests.get')
        cls.mock_get = cls.mock_get_patcher.start()

    def test_account_response(self):
        self.mock_get.return_value.ok = True
        e = EchosignAccount('a string')
        self.assertEqual(e.access_token, 'a string')

    def test_get_agreements(self):
        self.mock_get.return_value.ok = True
        e = EchosignAccount('a string')
        mock_response = Mock()
        expected_dict = {
            "userAgreementList": [
                {
                    "agreementId": "1",
                    "displayDate": "date",
                    "displayUserSetInfos": [
                        {
                            "displayUserSetMemberInfos": [
                                {
                                    "email": "",
                                    "company": "",
                                    "fullName": ""
                                }
                            ],
                            "displayUserSetName": ""
                        }
                    ],
                    "esign": False,
                    "latestVersionId": "",
                    "name": "Test Document",
                    "status": "WAITING_FOR_SIGNATURE"
                }
            ]
        }
        mock_response.json.return_value = expected_dict

        # Assign our mock response as the result of our patched function
        self.mock_get.return_value = mock_response

        agreements = e.get_agreements()
        self.assertIsInstance(agreements[0], Agreement)
