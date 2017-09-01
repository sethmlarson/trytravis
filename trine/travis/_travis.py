import time
import requests
import trent


class AuthenticationError(Exception):
    pass


class Travis(object):
    """The central object within the Travis API model that handles the
    access token along with HTTP requests to the API endpoint of choice.
    
    Also handles the authentication handshake between GitHub and Travis.
    """

    def __init__(self, endpoint, access_token):
        endpoint = endpoint.rstrip('/')
        self.endpoint = endpoint  # type: str
        self.access_token = access_token  # type: str
        self.session = requests.Session()

    @staticmethod
    def auth_handshake(travis_endpoint,
                       github_endpoint,
                       github_username,
                       github_password):

        """Attempt to authenticate with a Travis endpoint and either
        raise an error if no access token is returned or return
        an instance of Travis for that endpoint.
        
        We actually use the Travis API v2 for all of this because
        API v3 doesn't provide authentication options?
        
        We don't store the GitHub username or password locally, we only
        store the Travis API token.
        
        :param travis_endpoint: Travis API endpoint to authenticate for.
        :param github_endpoint: GitHub API endpoint to authenticate against.
        :param github_username: GitHub username to authenticate for.
        :param github_password: GitHub password to authenticate with.
        """
        travis_endpoint = travis_endpoint.rstrip('/')
        github_endpoint = github_endpoint.rstrip('/')

        # travis-ci.org requires fewer scopes than travis-ci.com.
        if travis_endpoint == 'https://api.travis-ci.org':
            scopes = ['read:org', 'user:email', 'repo_deployment',
                      'repo:status', 'public_repo', 'write:repo_hook']
        else:
            scopes = ['user:email', 'read:org', 'repo']

        args = (github_endpoint, github_username, github_password, scopes)
        github_token, token_id = Travis._create_github_token(*args)

        # Make sure we attempt to delete the token after use.
        try:
            access_token = Travis._swap_github_token_for_access_token(
                travis_endpoint, github_token)
        finally:
            args = (github_endpoint, github_username,
                    github_password, token_id)
            Travis._delete_github_token(*args)

        return Travis(travis_endpoint, access_token)

    @staticmethod
    def _create_github_token(endpoint, username, password, scopes):
        """Create a temporary GitHub Personal Access Token with the given
        scopes using a username and password supplied by the user.
        
        :param endpoint: GitHub API endpoint to authenticate with.
        :param username: GitHub username.
        :param password: GitHub password.
        :param scopes: List of scopes to add to the Personal Access Token.
        :returns: A tuple containing the token along with the id of the token
                  so it may be deleted after creation.
        :rtype: typing.Tuple[str, int]"""

        headers = {'User-Agent': trent.user_agent,
                   'Accept': 'application/vnd.github.v3+json'}
        data = {'scopes': scopes,
                'note': 'Temporary authentication token for trent.'}

        # First we contant GitHub and attempt to authenticate with
        # them to create a Personal Access token with the proper scopes.
        with requests.post(endpoint + '/authorizations',
                           headers=headers,
                           auth=(username, password),
                           json=data) as r:
            if not r.ok:
                raise AuthenticationError('Could not create a personal '
                                          'access token on GitHub. Bad '
                                          'credentials?')

            data = r.json()
            return data['token'], data['id']

    @staticmethod
    def _delete_github_token(endpoint, username, password, token_id):
        """Delete a GitHub Personal Access Token that was created previously.
        
        :param endpoint: GitHub API endpoint.
        :param username: GitHub username.
        :param password: GitHub password.
        :param token_id: ID of the token received from _create_github_token()
        """
        headers = {'User-Agent': trent.user_agent,
                   'Accept': 'application/vnd.github.v3+json'}

        requests.request('DELETE', endpoint + '/authorizations/%d' % token_id,
                         headers=headers,
                         auth=(username, password))

    @staticmethod
    def _swap_github_token_for_access_token(endpoint, github_token):
        """Swaps a GitHub Personal Access token for a Travis Access Token.
        
        :param endpoint: Travis API endpoint to authenticate with.
        :param github_token: GitHub Personal Access token.
        :returns: Travis Access Token.
        """
        headers = {'User-Agent': trent.user_agent,
                   'Accept': 'application/vnd.travis-ci.2+json'}

        with requests.post(endpoint + '/auth/github',
                           headers=headers,
                           json={'github_token': github_token}) as r:
            if not r.ok:
                raise AuthenticationError('Could not swap a GitHub personal '
                                          'access token for a Travis Access '
                                          'token.')

            return r.json()['access_token']

    @property
    def headers(self):
        headers = {'Travis-API-Version': '3',
                   'User-Agent': trent.user_agent,
                   'Accept': 'application/json'}
        if self.access_token is not None:
            headers['Authorization'] = 'token ' + self.access_token
        return headers

    def request(self, method, path, **kwargs):
        """Make a request to the Travis API.
        
        :param method: HTTP method to use. (ie 'GET', 'POST'...)
        :param path: URL path to request. (ie '/user')
        :param kwargs: Arguments to pass to requests.
        :return: Request response.
        """
        print(method, path)
        headers = self.headers
        if 'headers' in kwargs:
            for key, value in kwargs['headers'].items():
                headers[key] = value
        kwargs['headers'] = headers
        return self.session.request(method, self.endpoint + path, **kwargs)

    def request_paginated(self, path, get_list_func):
        """Make a request and return a Paginator to lazily
        evaluate the paginated responses.
        
        :param method: HTTP method to use. (ie 'GET', 'POST'...)
        :param path: URL path to request. (ie '/user')
        :param get_list_func: Function that converts the responses into
                              entries that are returned by the iterator.
        :return: Request response.
        """
        return Paginator(self, path, get_list_func)

    def get_owner(self, login):
        """Get an Owner by their login information.
        
        :param login: GitHub login of either the Organization or User
        :rtype: trent.api.Owner
        """
        from ._owner import User, Organization
        path = '/owner/%s' % login
        with self.request('GET', path) as r:
            data = r.json()
            if data['@type'] == 'user':
                return User(self, data['id'], data={'login': data['login']})
            else:
                return Organization(self, data['id'], data={'login': data['login']})

    @property
    def current_user(self):
        """Gets the currently authenticated User.
        
        :rtype: trent.api.User
        :return: Returns the current authenticated user.
        """
        raise NotImplementedError()


class Resource(object):
    """Base class for a resource in the Travis API."""

    def __init__(self, travis, id, data=None):
        if data is None:
            data = {}

        self.id = id
        self._travis = travis  # type: Travis
        self._data = data
        self._cache_time = None

    def refresh(self):
        """Refreshes all remote properties for the resource."""
        self._get_standard_rep()

    def _get_property(self, name, cache_time=10):
        """Get a basic property from the JSON
        representation of the object. If needed
        will refresh the object property. """
        current_time = time.time()

        # If we're using a cached property we might need
        # to get values again.
        if (self._cache_time is not None and
                self._cache_time + cache_time > current_time):
            del self._data[name]

        if name not in self._data:
            self._get_standard_rep()
            self._cache_time = time.time()
        return self._data[name]

    def _del_property(self, name):
        """Invalidate a property if it is defined within `_data`
        in order to force a request on next usage."""
        if name in self._data:
            del self._data[name]

    def _get_standard_rep(self):
        """Implement this function per-model to fill the
        `_data` property with JSON values for the model. """
        raise NotImplementedError()


class Paginator(object):
    """Helper class for lazily evaluating paginated
    responses from Travis API."""

    def __init__(self, travis, path, get_list_func):
        self._travis = travis  # type: Travis
        self._path = path  # type: str
        self._get_list_func = get_list_func

    def __iter__(self):
        while True:
            with self._travis.request('GET', self._path) as r:
                print(r.content)
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
