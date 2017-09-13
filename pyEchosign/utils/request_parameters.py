def get_headers(access_token, api_user_email=None, content_type='application/json'):
    """
    Generates the headers for a request to the API - can specify which user the API call should be made under.
    Args:
        access_token: The access token of the account making the request
        api_user_email: If the access token covers more than one user, enter the email of the user the call should be made under

    Returns: A dictionary to be used as the headers argument in requests

    """
    headers = {'Access-Token': access_token}

    if content_type is not None:
        headers.update({'Content-Type': content_type})
    if api_user_email is not None:
        headers.update({'x-api-user': 'email:{}'.format(api_user_email)})

    return headers


def account_headers(account, content_type='application/json'):
    """ Creates the headers automatically from the EchosignAccount details """
    return get_headers(account.access_token, api_user_email=account.user_email, content_type=content_type)
