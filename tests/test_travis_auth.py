import pytest
import mock
import trent
from trent.models import Travis, AuthenticationError


@pytest.mark.parametrize('endpoint,scopes', [('https://api.travis-ci.org', ['read:org',
                                                                            'user:email',
                                                                            'repo_deployment',
                                                                            'repo:status',
                                                                            'public_repo',
                                                                            'write:repo_hook']),

                                             ('https://api.travis-ci.com', ['user:email', 'read:org', 'repo']),
                                             ('https://example.com/api', ['user:email', 'read:org', 'repo'])
                                             ])
def test_scopes_based_on_travis_endpoint(mocker, endpoint, scopes):
    mock_create_token = mocker.patch('trent.models.Travis._create_github_token')
    mock_create_token.return_value = 'github_token', 1
    mock_delete_token = mocker.patch('trent.models.Travis._delete_github_token')
    mock_swap_token = mocker.patch('trent.models.Travis._swap_github_token_for_access_token')
    mock_swap_token.return_value = 'travis_token'

    t = Travis.auth_handshake(endpoint, 'https://api.github.com', 'username', 'password')

    mock_create_token.assert_called_with('https://api.github.com', 'username', 'password', scopes)
    assert t.access_token == 'travis_token'


def test_create_github_token(mocker):
    mock_post = mocker.patch('requests.post')
    mock_response = mock.Mock()
    mock_response.ok = True
    mock_response.json.return_value = {'id': 1234, 'token': 'github_token'}
    mock_response.__enter__ = lambda *_: mock_response
    mock_response.__exit__ = lambda *_: None
    mock_post.return_value = mock_response

    token, token_id = Travis._create_github_token('https://api.github.com', 'username', 'password', ['user:email', 'read:org', 'repo'])

    mock_post.assert_called_with('https://api.github.com/authorizations',
                                 auth=('username', 'password'),
                                 json={'scopes': ['user:email', 'read:org', 'repo'],
                                       'note': 'Temporary authentication token for trent.'},
                                 headers={'User-Agent': 'trent/' + trent.__version__,
                                          'Accept': 'application/vnd.github.v3+json'})

    assert token == 'github_token'
    assert token_id == 1234


def test_create_github_token_error(mocker):
    mock_post = mocker.patch('requests.post')
    mock_response = mock.Mock()
    mock_response.ok = False
    mock_response.__enter__ = lambda *_: mock_response
    mock_response.__exit__ = lambda *_: None
    mock_post.return_value = mock_response

    with pytest.raises(AuthenticationError):
        Travis._create_github_token('https://api.github.com',
                                    'username', 'password',
                                    ['user:email', 'read:org', 'repo'])


def test_delete_github_token(mocker):
    mock_request = mocker.patch('requests.request')

    Travis._delete_github_token('https://api.github.com', 'username', 'password', 1234)

    mock_request.assert_called_with('DELETE', 'https://api.github.com/authorizations/1234',
                                    auth=('username', 'password'),
                                    headers={'User-Agent': 'trent/' + trent.__version__,
                                             'Accept': 'application/vnd.github.v3+json'})
