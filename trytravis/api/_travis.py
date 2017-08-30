import requests
from trytravis import __version__


class Travis(object):
    def __init__(self, endpoint, api_token):
        if endpoint.endswith('/'):
            endpoint = endpoint.rstrip('/')
        self.endpoint = endpoint  # type: str
        self.api_token = api_token  # type: str
        self.session = requests.Session()

    @property
    def headers(self):
        return {'Travis-API-Version': '3',
                'User-Agent': 'trytravis/' + __version__,
                'Authorization': 'token ' + self.api_token}

    def request(self, method, path, **kwargs):
        headers = self.headers
        if 'headers' in kwargs:
            for key, value in kwargs['headers'].items():
                headers[key] = value
        kwargs['headers'] = headers
        return self.session.request(method, self.endpoint + path, **kwargs)

    @property
    def whoami(self):
        """
        :rtype: trytravis.api.User
        :return: Returns the current authenticated user.
        """
        raise NotImplementedError()


class Resource(object):
    def __init__(self, travis, id, data=None):
        if data is None:
            data = {}

        self.id = id
        self._travis = travis  # type: Travis
        self._data = data
