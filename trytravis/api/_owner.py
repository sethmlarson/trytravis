from ._travis import Resource


class Owner(Resource):
    @property
    def login(self):
        """ :rtype: str """
        return self._get_property('login')

    @property
    def name(self):
        """ :rtype: str """
        return self._get_property('name')

    @property
    def avatar_url(self):
        """ :rtype: str """
        return self._get_property('avatar_url')

    @property
    def github_id(self):
        """ :rtype: int """
        return self._get_property('github_id')


class User(Owner):
    pass


class Organization(Owner):
    pass
