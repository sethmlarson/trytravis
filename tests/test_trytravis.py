import os
import trytravis
import pytest
import mock


def test_help():
    trytravis._main(['--help'])


def test_too_many_parameters():
    trytravis._main(['a', 'b', 'c'])


def test_version():
    assert trytravis.__version__ in trytravis._version_string()


def test_repo_input():
    with mock.patch('trytravis.user_input') as mock_input:
        mock_input.side_effect = ['https://www.github.com/testauthor/testname', 'yes']
        trytravis.config_dir = os.path.dirname(os.path.abspath(__file__))

        trytravis._main(['--repo'])

        assert os.path.isfile(os.path.join(trytravis.config_dir, 'repo'))

        with open(os.path.join(trytravis.config_dir, 'repo'), 'r') as f:
            assert f.read() == 'https://www.github.com/testauthor/testname'

        os.remove(os.path.join(trytravis.config_dir, 'repo'))


def test_repo_command_line():
    with mock.patch('trytravis.user_input') as mock_input:
        mock_input.side_effect = ['y']
        trytravis.config_dir = os.path.dirname(os.path.abspath(__file__))

        trytravis._main(['--repo', 'https://github.com/testauthor/testname'])

        assert os.path.isfile(os.path.join(trytravis.config_dir, 'repo'))

        with open(os.path.join(trytravis.config_dir, 'repo'), 'r') as f:
            assert f.read() == 'https://github.com/testauthor/testname'

        os.remove(os.path.join(trytravis.config_dir, 'repo'))


def test_repo_ssh():
    with mock.patch('trytravis.user_input') as mock_input:
        mock_input.side_effect = ['y']
        trytravis.config_dir = os.path.dirname(os.path.abspath(__file__))

        trytravis._main(['--repo', 'ssh://git@github.com/testauthor/testname'])

        assert os.path.isfile(os.path.join(trytravis.config_dir, 'repo'))

        with open(os.path.join(trytravis.config_dir, 'repo'), 'r') as f:
            assert f.read() == 'ssh://git@github.com/testauthor/testname'

        os.remove(os.path.join(trytravis.config_dir, 'repo'))


def test_repo_cancel():
    with pytest.raises(RuntimeError):
        with mock.patch('trytravis.user_input') as mock_input:
            mock_input.side_effect = ['https://www.github.com/testauthor/testname', 'e']
            trytravis.config_dir = os.path.dirname(os.path.abspath(__file__))

            trytravis._main(['--repo'])

    assert not os.path.isfile(os.path.join(trytravis.config_dir, 'repo'))


def test_repo_invalid_url():
    with pytest.raises(RuntimeError):
        with mock.patch('trytravis.user_input') as mock_input:
            mock_input.side_effect = ['https://www.github.com/testauthor', 'y']
            trytravis.config_dir = os.path.dirname(os.path.abspath(__file__))

            trytravis._main(['--repo'])

    assert not os.path.isfile(os.path.join(trytravis.config_dir, 'repo'))
