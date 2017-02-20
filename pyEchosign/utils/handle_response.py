from requests import Response


def check_error(response: Response):
    """ Takes a requests package response object and checks the error code and raises the proper exception """
    response_json = response.json()
    code = response_json.get('code', None)
    if response.status_code == 401:
        raise PermissionError('Echosign API returned a 401, your access token may be invalid if you believe your '
                              'account should have access to perform this action.')


def response_success(response: Response):
    return 199 < response.status_code < 300
