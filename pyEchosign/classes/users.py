class UserEndpoints(object):
    @classmethod
    def get_users_from_bulk_agreements(cls, data: dict):
        """ Takes a response from the GET /agreements call and returns a set of `DisplayUser` """
        users = []
        for user_data in data:
            email = user_data.get('email')
            name = user_data.get('fullName', None)
            company = user_data.get('company', None)
            user = DisplayUser(email, full_name=name, company=company)
            users.append(user)
        return users


class DisplayUser(object):
    """ Maps to the DisplayUserInfo provided by Echosign for agreements fetched in bulk """
    def __init__(self, email: str, **kwargs):
        self.email = email
        self.company = kwargs.pop('company', None)
        self.full_name = kwargs.pop('full_name', None)

    def __str__(self):
        if self.full_name:
            return self.full_name
        else:
            return self.email