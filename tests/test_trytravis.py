import os
import trytravis
import pytest
import mock


def test_help():
    with mock.patch('sys.exit'):
        trytravis.main(['--help'])


def test_too_many_parameters():
    with mock.patch('sys.exit'):
        trytravis.main(['a', 'b', 'c'])


def test_version():
    with mock.patch('sys.exit'):
        trytravis.main(['--version'])


def test_token_input():
    with mock.patch('sys.exit'):
        with mock.patch('getpass.getpass') as mock_getpass:
            mock_getpass.return_value = 'abc123'
            trytravis.config_dir = os.path.dirname(os.path.abspath(__file__))

            trytravis.main(['--token'])

            assert os.path.isfile(os.path.join(trytravis.config_dir, 'personal_access_token'))
            
            with open(os.path.join(trytravis.config_dir, 'personal_access_token'), 'r') as f:
                assert f.read() == 'abc123'

            os.remove(os.path.join(trytravis.config_dir, 'personal_access_token'))


def test_token_command_line():
    with mock.patch('sys.exit'):
        trytravis.config_dir = os.path.dirname(os.path.abspath(__file__))
        trytravis.main(['--token', 'abc123'])

        assert os.path.isfile(os.path.join(trytravis.config_dir, 'personal_access_token'))

        with open(os.path.join(trytravis.config_dir, 'personal_access_token'), 'r') as f:
            assert f.read() == 'abc123'

        os.remove(os.path.join(trytravis.config_dir, 'personal_access_token'))
