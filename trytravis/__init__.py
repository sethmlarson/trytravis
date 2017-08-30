#             Copyright (C) 2017 Seth Michael Larson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Send local git changes to Travis CI without commits or pushes. """

import time
import datetime
import getpass
import platform
import sys
import os
import re
import colorama
import git
from .__about__ import (__title__,  # noqa: F401
                        __version__,
                        __author__,
                        __description__,
                        __email__,
                        __license__,
                        __url__)

__all__ = ['main']

# Try to find the home directory for different platforms.
_home_dir = os.path.expanduser('~')
if _home_dir == '~' or not os.path.isdir(_home_dir):
    try:  # Windows
        import win32file  # noqa: F401
        from win32com.shell import shell, shellcon

        home = shell.SHGetFolderPath(0, shellcon.CSIDL_PROFILE, None, 0)
    except ImportError:  # Try common directories?
        for _home_dir in [os.environ.get('HOME', ''),
                          '/home/%s' % getpass.getuser(),
                          'C:\\Users\\%s' % getpass.getuser()]:
            if os.path.isdir(_home_dir):
                break

# Determine config directory.
if platform.system() == 'Windows':
    config_dir = os.path.join(_home_dir, 'trytravis')
else:
    config_dir = os.path.join(_home_dir, '.config', 'trytravis')
del _home_dir

try:
    user_input = raw_input
except NameError:
    user_input = input

# Usage output
_USAGE = ('usage: trytravis [command]?\n'
          '\n'
          '  [empty]               Running with no command submits '
          'your git repo to Travis.\n'
          '  --help, -h            Prints this help string.\n'
          '  --version, -v         Prints out the version, useful when '
          'submitting an issue.\n'
          '  --repo, -r [repo]?    Tells the program you wish to setup '
          'your building repository.\n'
          '\n'
          'If you\'re still having troubles feel free to open an '
          'issue at our\nissue tracker: https://github.com/SethMichaelLarson'
          '/trytravis/issues')

_HTTPS_REGEX = re.compile(r'^https://(?:www\.)?github\.com/([^/]+)/([^/]+)$')
_SSH_REGEX = re.compile(r'^ssh://git@github\.com/([^/]+)/([^/]+)$')


def _input_github_repo(url=None):
    """ Grabs input from the user and saves
    it as their trytravis target repo """
    if url is None:
        url = user_input('Input the URL of the GitHub repository '
                         'to use as a `trytravis` repository: ')
    url = url.strip()
    http_match = _HTTPS_REGEX.match(url)
    ssh_match = _SSH_REGEX.match(url)
    if not http_match and not ssh_match:
        raise RuntimeError('That URL doesn\'t look like a valid '
                           'GitHub URL. We expect something '
                           'of the form: `https://github.com/[USERNAME]/'
                           '[REPOSITORY]` or `ssh://git@github.com/'
                           '[USERNAME]/[REPOSITORY]')

    # Make sure that the user actually made a new repository on GitHub.
    if http_match:
        _, name = http_match.groups()
    else:
        _, name = ssh_match.groups()
    if 'trytravis' not in name:
        raise RuntimeError('You must have `trytravis` in the name of your '
                           'repository. This is a security feature to reduce '
                           'chances of running git push -f on a repository '
                           'you don\'t mean to.')

    # Make sure that the user actually wants to use this repository.
    accept = user_input('Remember that `trytravis` will make commits on your '
                        'behalf to `%s`. Are you sure you wish to use this '
                        'repository? Type `y` or `yes` to accept: ' % url)
    if accept.lower() not in ['y', 'yes']:
        raise RuntimeError('Operation aborted by user.')

    if not os.path.isdir(config_dir):
        os.makedirs(config_dir)
    with open(os.path.join(config_dir, 'repo'), 'w+') as f:
        f.truncate()
        f.write(url)
    print('Repository saved successfully.')


def _load_github_repo():
    """ Loads the GitHub repository from the users config. """
    if 'TRAVIS' in os.environ:
        raise RuntimeError('Detected that we are running in Travis. '
                           'Stopping to prevent infinite loops.')
    try:
        with open(os.path.join(config_dir, 'repo'), 'r') as f:
            return f.read()
    except (OSError, IOError):
        raise RuntimeError('Could not find your repository. '
                           'Have you ran `trytravis --repo`?')


def _submit_changes_to_github_repo(path, url):
    """ Temporarily commits local changes and submits them to
    the GitHub repository that the user has specified. Then
    reverts the changes to the git repository if a commit was
    necessary. """
    try:
        repo = git.Repo(path)
    except Exception:
        raise RuntimeError('Couldn\'t locate a repository at `%s`.' % path)
    commited = False
    try:
        try:
            repo.delete_remote('trytravis')
        except:
            pass
        print('Adding a temporary remote to '
              '`%s`...' % url)
        remote = repo.create_remote('trytravis', url)

        print('Adding all local changes...')
        repo.git.add('--all')
        try:
            print('Committing local changes...')
            timestamp = datetime.datetime.now().isoformat()
            repo.git.commit(m='trytravis-' + timestamp)
            commited = True
        except git.exc.GitCommandError as e:
            if 'nothing to commit' in str(e):
                commited = False
            else:
                raise
        commit = repo.head.commit.hexsha
        committed_at = repo.head.commit.committed_datetime.isoformat()

        print('Pushing to `trytravis` remote...')
        remote.push(force=True)
    finally:
        if commited:
            print('Reverting to old state...')
            repo.git.reset('HEAD^')
        try:
            repo.delete_remote('trytravis')
        except:
            pass
    return commit, committed_at


def _wait_for_travis_build(url, commit, committed_at):
    """ Waits for a Travis build to appear with the given commit SHA """
    print('Waiting for a Travis build to appear '
          'for `%s` after `%s`...' % (commit, committed_at))
    import requests

    slug = _slug_from_url(url)
    start_time = time.time()
    build_id = None

    while time.time() - start_time < 60:
        with requests.get('https://api.travis-ci.org/repos/%s/builds' % slug,
                          headers=_travis_headers()) as r:
            if not r.ok:
                raise RuntimeError('Could not reach the Travis API '
                                   'endpoint. Additional information: '
                                   '%s' % str(r.content))

            # Search through all commits and builds to find our build.
            commit_to_sha = {}
            json = r.json()
            for travis_commit in sorted(json['commits'],
                                        key=lambda x: x['committed_at']):
                if travis_commit['committed_at'] < committed_at:
                    continue
                commit_to_sha[travis_commit['id']] = travis_commit['sha']

            for build in json['builds']:
                if (build['commit_id'] in commit_to_sha and
                            commit_to_sha[build['commit_id']] == commit):
                    build_id = build['id']
                    print('Travis build id: `%d`' % build_id)
                    print('Travis build URL: `https://travis-ci.org/'
                          '%s/builds/%d`' % (slug, build_id))

            if build_id is not None:
                break

        time.sleep(3.0)
    else:
        raise RuntimeError('Timed out while waiting for a Travis build '
                           'to start. Is Travis configured for `%s`?' % url)
    return build_id


def _watch_travis_build(build_id):
    """ Watches and progressively outputs information
    about a given Travis build """
    import requests
    try:
        build_size = None  # type: int
        running = True
        while running:
            with requests.get('https://api.travis-ci.org/builds/%d' % build_id,
                              headers=_travis_headers()) as r:
                json = r.json()

                if build_size is not None:
                    if build_size > 1:
                        sys.stdout.write('\r\x1b[%dA' % build_size)
                    else:
                        sys.stdout.write('\r')

                build_size = len(json['jobs'])
                running = False
                current_number = 1
                for job in json['jobs']:  # pragma: no coverage
                    color, state, is_running = _travis_job_state(job['state'])
                    if is_running:
                        running = True

                    platform = job['config']['os']
                    if platform == 'osx':
                        platform = ' osx '

                    env = job['config'].get('env', '')
                    sudo = 's' if job['config'].get('sudo', True) else 'c'
                    lang = job['config'].get('language', 'generic')

                    padding = ' ' * (len(str(build_size)) -
                                     len(str(current_number)))
                    number = str(current_number) + padding
                    current_number += 1
                    job_display = '#' + ' '.join([number,
                                                  state,
                                                  platform,
                                                  sudo,
                                                  lang,
                                                  env])

                    print(color + job_display + colorama.Style.RESET_ALL)

            time.sleep(3.0)
    except KeyboardInterrupt:
        pass


def _travis_job_state(state):
    """ Converts a Travis state into a state character, color,
    and whether it's still running or a stopped state. """
    if state in [None, 'queued', 'created', 'received']:
        return colorama.Fore.YELLOW, '*', True
    elif state in ['started', 'running']:
        return colorama.Fore.LIGHTYELLOW_EX, '*', True
    elif state == 'passed':
        return colorama.Fore.LIGHTGREEN_EX, 'P', False
    elif state == 'failed':
        return colorama.Fore.LIGHTRED_EX, 'X', False
    elif state == 'errored':
        return colorama.Fore.LIGHTRED_EX, '!', False
    elif state == 'canceled':
        return colorama.Fore.LIGHTBLACK_EX, 'X', False
    else:
        raise RuntimeError('unknown state: %s' % str(state))


def _slug_from_url(url):
    """ Parses a project slug out of either an HTTPS or SSH URL. """
    http_match = _HTTPS_REGEX.match(url)
    ssh_match = _SSH_REGEX.match(url)
    if not http_match and not ssh_match:
        raise RuntimeError('Could not parse the URL (`%s`) '
                           'for your repository.' % url)
    if http_match:
        return '/'.join(http_match.groups())
    else:
        return '/'.join(ssh_match.groups())


def _version_string():
    """ Gets the output for `trytravis --version`. """
    platform_system = platform.system()
    if platform_system == 'Linux':
        os_name, os_version, _ = platform.dist()
    else:
        os_name = platform_system
        os_version = platform.version()
    python_version = platform.python_version()
    return 'trytravis %s (%s %s, python %s)' % (__version__,
                                                os_name.lower(),
                                                os_version,
                                                python_version)


def _travis_headers():
    """ Returns the headers that the Travis API expects from clients. """
    return {'User-Agent': ('trytravis/%s (https://github.com/'
                           'SethMichaelLarson/trytravis)') % __version__,
            'Accept': 'application/vnd.travis-ci.2+json'}


def _main(argv):
    """ Function that acts just like main() except
    doesn't catch exceptions. """
    repo_input_argv = len(argv) == 2 and argv[0] in ['--repo', '-r', '-R']

    # We only support a single argv parameter.
    if len(argv) > 1 and not repo_input_argv:
        _main(['--help'])

    # Parse the command and do the right thing.
    if len(argv) == 1 or repo_input_argv:
        arg = argv[0]

        # Help/usage
        if arg in ['-h', '--help', '-H']:
            print(_USAGE)

        # Version
        elif arg in ['-v', '--version', '-V']:
            print(_version_string())

        # Token
        elif arg in ['-r', '--repo', '-R']:
            if len(argv) == 2:
                url = argv[1]
            else:
                url = None
            _input_github_repo(url)

        # Help string
        else:
            _main(['--help'])

    # No arguments means we're trying to submit to Travis.
    elif len(argv) == 0:
        url = _load_github_repo()
        commit, committed = _submit_changes_to_github_repo(os.getcwd(), url)
        build_id = _wait_for_travis_build(url, commit, committed)
        _watch_travis_build(build_id)


def main(argv=None):  # pragma: no coverage
    """ Main entry point when the user runs the `trytravis` command. """
    try:
        colorama.init()
        if argv is None:
            argv = sys.argv[1:]
        _main(argv)
    except RuntimeError as e:
        print(colorama.Fore.RED + 'ERROR: ' +
              str(e) + colorama.Style.RESET_ALL)
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
