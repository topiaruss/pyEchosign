from requests import Response


def check_error(response: Response):
    """ Takes a requests package response object and checks the error code and raises the proper exception """
    response_json = response.json()
    code = response_json.get('code', None)
    if 'PERMISSION_DENIED' in code:
        raise PermissionError


def response_success(response: Response):
    return 199 < response.status_code < 300
