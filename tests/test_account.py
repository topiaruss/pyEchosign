from unittest import TestCase
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

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
                    "displayDate": "2017-02-19T08:22:34-08:00",
                    "displayUserSetInfos": [
                        {
                            "displayUserSetMemberInfos": [
                                {
                                    "company": "Test Company",
                                    "email": "test@pyechosign.com",
                                    "fullName": "Jens Astrup"
                                }
                            ]
                        }
                    ],
                    "esign": True,
                    "agreementId": "3AAABLblqZhzzzzwYDpSW8yUnA44scCLW0tpPZzCSLE2TStghgWFCOvIwqLm50znN_m-cHICV3fUsdsUT_41BKA-f00OgL",
                    "latestVersionId": "3AA60C0ZzCSc33wB7Ka5bQ2iuuU51eD4MMjWLE2TStghgWUycxgFTabUcAs4Pape63WTXzKMbvAVUyXSEbMwIK7",
                    "name": "test agreement",
                    "status": "RECALLED"
                },
            ]
        }
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 200
        # Assign our mock response as the result of our patched function
        self.mock_get.return_value = mock_response
