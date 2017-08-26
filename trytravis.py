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

""" Send your local git repo changes to Travis CI without needless commits and pushes. """

import time
import datetime
import getpass
import platform
import sys
import os
import re
import colorama
import git


__title__ = 'trytravis'
__author__ = 'Seth Michael Larson'
__email__ = 'sethmichaellarson@protonmail.com'
__description__ = 'Send your local git repo changes to Travis CI without needless commits and pushes.'
__license__ = 'Apache-2.0'
__url__ = 'https://github.com/SethMichaelLarson/trytravis'
__version__ = '0.0.0.dev0'

__all__ = ['main', 'TryTravis']

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


class TryTravis(object):
    """ Object which can be used to submit jobs via `trytravis` programmatically. """
    def __init__(self, path):
        self.path = path
        self.slug = None
        self.commit = None
        self.build_id = None
        self.build_url = None
        self.build_size = None

    def start(self):
        self._load_trytravis_github_slug()
        self._submit_project_to_github()
        self._wait_for_travis_build()
        self._watch_travis_build()

    def _load_trytravis_github_slug(self):
        try:
            with open(os.path.join(config_dir, 'slug'), 'r') as f:
                self.slug = f.read()
        except (OSError, IOError):
            raise RuntimeError('Could not find your repository. Have you ran `trytravis --repo`?')

    def _submit_project_to_github(self):
        repo = git.Repo(self.path)
        commited = False
        try:
            try:
                repo.delete_remote('trytravis')
            except:
                pass
            print('Adding a temporary remote to `https://github.com/%s`...' % self.slug)
            remote = repo.create_remote('trytravis', 'https://github.com/' + self.slug)

            print('Adding all local changes...')
            repo.git.add('--all')
            try:
                print('Committing local changes...')
                repo.git.commit(m='trytravis-' + datetime.datetime.now().isoformat())
                commited = True
            except git.exc.GitCommandError as e:
                if 'nothing to commit' in str(e):
                    commited = False
                else:
                    raise
            self.commit = repo.head.commit.hexsha

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

    def _wait_for_travis_build(self):
        print('Waiting for a Travis build to appear for `%s`...' % self.commit)
        import requests

        start_time = time.time()
        while time.time() - start_time < 30:
            with requests.get('https://api.travis-ci.org/repos/%s/builds' % self.slug,
                              headers=self._travis_headers()) as r:
                if not r.ok:
                    raise RuntimeError('Could not reach the Travis API endpoint. '
                                       'Additional information: %s' % str(r.content))

                # Search through all commits and builds to find our build.
                commit_to_sha = {}
                json = r.json()
                for commit in json['commits']:
                    commit_to_sha[commit['id']] = commit['sha']
                for build in json['builds']:
                    if build['commit_id'] in commit_to_sha and commit_to_sha[build['commit_id']] == self.commit:
                        self.build_id = build['id']
                        self.build_url = 'https://travis-ci.org/%s/builds/%d' % (self.slug, self.build_id)
                        print('Travis build id: `%d`' % self.build_id)
                        print('Travis build URL: `%s`' % self.build_url)

                if self.build_id is not None:
                    break
            time.sleep(3.0)
        else:
            raise RuntimeError('Timed out while waiting for a Travis build to start. '
                               'Is Travis configured for `https://github.com/%s`?' % self.slug)

    def _watch_travis_build(self):
        import requests
        try:
            running = True
            while running:
                with requests.get('https://api.travis-ci.org/builds/%d' % self.build_id,
                                  headers=self._travis_headers()) as r:
                    json = r.json()

                    if self.build_size is not None:
                        if self.build_size > 1:
                            sys.stdout.write('\r\x1b[%dA' % (self.build_size))
                        else:
                            sys.stdout.write('\r')

                    self.build_size = len(json['jobs'])
                    running = False
                    current_number = 1
                    for job in json['jobs']:
                        if job['state'] in [None, 'queued', 'created', 'received']:
                            color, state = colorama.Fore.YELLOW, '*'
                            running = True
                        elif job['state'] in ['started', 'running']:
                            color, state = colorama.Fore.LIGHTYELLOW_EX, '*'
                            running = True
                        elif job['state'] == 'passed':
                            color, state = colorama.Fore.LIGHTGREEN_EX, 'P'
                        elif job['state'] == 'failed':
                            color, state = colorama.Fore.LIGHTRED_EX, 'X'
                        elif job['state'] == 'errored':
                            color, state = colorama.Fore.LIGHTRED_EX, '!'
                        else:
                            raise RuntimeError('unknown state: %s' % str(job['state']))

                        platform = job['config']['os']
                        if platform == 'osx':
                            platform = ' osx '

                        env = job['config']['env']
                        sudo = 's' if job['config']['sudo'] else 'c'
                        lang = job['config']['language']

                        number = str(current_number) + (' ' * (len(str(self.build_size)) - len(str(current_number))))
                        current_number += 1

                        print(color +
                              '#%s %s %s %s %s %s' % (number, state, platform, sudo, lang, env) +
                              colorama.Style.RESET_ALL)

                time.sleep(3.0)
        except KeyboardInterrupt:
            pass  # TODO: Cancel builds if we have their API token.

    def _travis_headers(self):
        return {'User-Agent': 'trytravis/%s (https://github.com/SethMichaelLarson/trytravis)' % __version__,
                'Accept': 'application/vnd.travis-ci.2+json'}


def main(argv=None):
    """ Main entry point when the user runs the `trytravis` command. """
    try:
        colorama.init()
        if argv is None:
            argv = sys.argv[1:]

        repo_input_argv = len(argv) == 2 and argv[0] in ['--repo', '-r', '-R']

        # We only support a single argv parameter.
        if len(argv) > 1 and not repo_input_argv:
            main(['--help'])

        # Parse the command and do the right thing.
        if len(argv) == 1 or repo_input_argv:
            arg = argv[0]

            # Help/usage
            if arg in ['-h', '--help', '-H']:
                print('usage: trytravis [command]?\n'
                      '\n'
                      '  [empty]               Running with no command submits your git repo to Travis.\n'
                      '  --help, -h            Prints this help string.\n'
                      '  --version, -v         Prints out the version, useful when submitting an issue.\n'
                      '  --repo, -r [repo]?    Tells the program you wish to setup your building repository.\n'
                      '\n'
                      'If you\'re still having troubles feel free to open an issue at our\n'
                      'issue tracker: https://github.com/SethMichaelLarson/trytravis/issues')

            # Version
            elif arg in ['-v', '--version', '-V']:
                platform_system = platform.system()
                if platform_system == 'Linux':
                    name, version, _ = platform.dist()
                else:
                    name = platform_system
                    version = platform.version()
                print('trytravis %s (%s %s, python %s)' % (__version__,
                                                           name.lower(),
                                                           version,
                                                           platform.python_version()))

            # Token
            elif arg in ['-r', '--repo', '-R']:
                if len(argv) == 2:
                    url = argv[1]
                else:
                    url = user_input('Input the URL of the GitHub repository to use as a `trytravis` repository: ')
                url = url.strip()
                match = re.match(r'^https://(?:www\.)?github.com/([^/]+)/([^/]+)$', url)
                if not match:
                    raise RuntimeError('That URL doesn\'t look like a valid GitHub URL. We expect something'
                                       'of the form: `https://github.com/[USERNAME]/[REPOSITORY]`')

                # Make sure that the user actually wants to use this repository.
                author, name = match.groups()
                accept = user_input('Remember that `trytravis` will make commits on your behalf to '
                                    '`https://github.com/%s/%s`. Are you sure you wish to use this '
                                    'repository? Type `y` or `yes` to accept: ' % (author, name))
                if accept.lower() not in ['y', 'yes']:
                    raise RuntimeError('Operation aborted by user.')

                if not os.path.isdir(config_dir):
                    os.makedirs(config_dir)
                with open(os.path.join(config_dir, 'slug'), 'w+') as f:
                    f.truncate()
                    f.write('%s/%s' % (author, name))
                print('Repository saved successfully.')

        # No arguments means we're trying to submit to Travis.
        elif len(argv) == 0:
            trytravis = TryTravis(os.getcwd())
            trytravis.start()
    except RuntimeError as e:
        print(colorama.Fore.RED + 'ERROR: ' + str(e) + colorama.Style.RESET_ALL)
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
