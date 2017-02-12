def get_headers(access_token, api_user=None):
    headers = {'Access-Token': access_token, 'client_secret': 'vqGs8C4BelupDsmBBrJrUHiRkmQ78b0u',
               "Content-Type": "application/json"}
    if api_user:
        headers.update({'x-user-email': api_user})
    return headers