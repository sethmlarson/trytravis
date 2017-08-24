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

""" Send your local git repo changes to Travis CIwithout needless commits and pushes. """

import argparse
import sys
import colorama
import requests

__title__ = 'trytravis'
__author__ = 'Seth Michael Larson'
__email__ = 'sethmichaellarson@protonmail.com'
__description__ = ('Send your local git repo changes to Travis CI '
                   'without needless commits and pushes.')
__license__ = 'Apache-2.0'
__url__ = 'https://github.com/SethMichaelLarson/trytravis'
__version__ = '0.0.0.dev0'

__all__ = ['main', 'TryTravis']


class TryTravis(object):
    """ Object which can be used to submit jobs via `trytravis` programmatically. """
    def __init__(self, path, output=False):
        self.path = path
        self.output = output
        self.token = None
        self.remote = None
        self.build = None
        self.build_url = None
        
    def start(self, watch=False):
        self._load_personal_access_token()
        self._check_personal_access_token()
        self._load_trytravis_github_repo()
        self._submit_project_to_github()
        self._wait_for_travis_build()
        if watch:
            self._watch_travis_build()
        
    def _load_personal_access_token(self)
        raise NotImplementedError()

    def _check_personal_access_token(self):
        raise NotImplementedError()

    def _load_trytravis_github_repo(self):
        raise NotImplementedError()

    def _submit_project_to_github(self):
        raise NotImplementedError()

    def _wait_for_travis_build(self):
        raise NotImplementedError()

    def watch_travis_build(self):
        raise NotImplementedError()


def main(argv=None):
    """ Main entry point when the user runs the `trytravis` command. """
    if argv is None:
        argv = sys.argv[1:]

    trytravis = TryTravis(os.getcwd(), output=True)
    trytravis.start(watch=True)
    sys.exit(0)
