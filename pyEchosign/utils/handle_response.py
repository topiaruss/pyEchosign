from requests import Response

from pyEchosign.exceptions.internal_exceptions import ApiError


def check_error(response: Response):
    """ Takes a requests package response object and checks the error code and raises the proper exception """
    if response.status_code == 401:
        raise PermissionError('Echosign API returned a 401, your access token may be invalid if you believe your '
                              'account should have access to perform this action.')

    elif not response_success(response):
        try:
            json_response = response.json()
        except ValueError:
            json_response = ''
        raise ApiError(f'Received status code {response.status_code} from the Echosign API with the following '
                       f'JSON: "{json_response}" and content: "{response.content}""')


def response_success(response: Response):
    return 199 < response.status_code < 300
