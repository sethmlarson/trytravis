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


def test_repo_input():
    with mock.patch('sys.exit'):
        with mock.patch('trytravis.user_input') as mock_input:
            mock_input.side_effect = ['https://www.github.com/testauthor/testname', 'yes']
            trytravis.config_dir = os.path.dirname(os.path.abspath(__file__))

            trytravis.main(['--repo'])

            assert os.path.isfile(os.path.join(trytravis.config_dir, 'slug'))
            
            with open(os.path.join(trytravis.config_dir, 'slug'), 'r') as f:
                assert f.read() == 'testauthor/testname'

            os.remove(os.path.join(trytravis.config_dir, 'slug'))


def test_repo_command_line():
    with mock.patch('sys.exit'):
        with mock.patch('trytravis.user_input') as mock_input:
            mock_input.side_effect = ['y']
            trytravis.config_dir = os.path.dirname(os.path.abspath(__file__))

            trytravis.main(['--repo', 'https://github.com/testauthor/testname'])

            assert os.path.isfile(os.path.join(trytravis.config_dir, 'slug'))

            with open(os.path.join(trytravis.config_dir, 'slug'), 'r') as f:
                assert f.read() == 'testauthor/testname'

            os.remove(os.path.join(trytravis.config_dir, 'slug'))


def test_repo_cancel():
    with mock.patch('sys.exit'):
        with mock.patch('trytravis.user_input') as mock_input:
            mock_input.side_effect = ['https://www.github.com/testauthor/testname', 'e']
            trytravis.config_dir = os.path.dirname(os.path.abspath(__file__))

            trytravis.main(['--repo'])

    assert not os.path.isfile(os.path.join(trytravis.config_dir, 'slug'))
