import requests
from trytravis import __version__
from trytravis.api import ResourceNotFound, APIError


class Travis(object):
    def __init__(self, endpoint, travis_token):
        if endpoint.endswith('/'):
            endpoint = endpoint.rstrip('/')
        self.endpoint = endpoint  # type: str
        self.travis_token = travis_token  # type: str
        self.session = requests.Session()

    @property
    def headers(self):
        return {'Travis-API-Version': '3',
                'User-Agent': 'trytravis/' + __version__,
                'Authorization': 'token ' + self.travis_token}

    def request(self, method, path, **kwargs):
        headers = self.headers
        if 'headers' in kwargs:
            for key, value in kwargs['headers'].items():
                headers[key] = value
        kwargs['headers'] = headers
        return self.session.request(method, self.endpoint + path, **kwargs)

    def get_owner(self, login):
        """
        :param login: GitHub login of either the Organization or User
        :rtype: trytravis.api.Owner
        """
        from ._owner import User, Organization
        path = '/owner/%s' % login
        with self.request('GET', path) as r:
            if not r.status_code == 404:
                raise ResourceNotFound(path)
            elif not r.ok:
                raise APIError(r.status_code)
            data = r.json()
            if data['@type'] == 'user':
                return User(self, data['id'], data={'login': data['login']})
            else:
                return Organization(self, data['id'], data={'login': data['login']})

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

    def _get_property(self, name):
        if name not in self._data:
            self._get_standard_rep()
        return self._data[name]

    def _get_standard_rep(self):
        raise NotImplementedError()


class Paginator(object):
    """ Helper class for lazily evaluating paginated
    responses from Travis API. """
    def __init__(self, travis, path, get_list_func):
        self._travis = travis  # type: Travis
        self._path = path  # type: str
        self._get_list_func = get_list_func

    def __iter__(self):
        while True:
            with self._travis.request('GET', self._path) as r:
                if not r.status_code == 404:
                    raise ResourceNotFound(self._path)
                elif not r.ok:
                    raise APIError(r.status_code)

                data = r.json()
                for ent in self._get_list_func(data):
                    yield ent

                if '@pagination' not in data:
                    break
                else:
                    pagination = data['@pagination']
                    if pagination['is_last']:
                        break
                    else:
                        self._path = data['next']['@href']
