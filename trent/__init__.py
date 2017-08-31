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
    config_dir = os.path.join(_home_dir, 'trent')
else:
    config_dir = os.path.join(_home_dir, '.config', 'trent')
del _home_dir

# User-Agent for all HTTP requests.
user_agent = '%s/%s' % (__title__, __version__)
