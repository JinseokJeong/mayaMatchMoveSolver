# Copyright (C) 2019 David Cattermole.
#
# This file is part of mmSolver.
#
# mmSolver is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# mmSolver is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
#
"""
Download and unpack external dependencies for Maya MatchMove Solver.

This script is designed to run on any operating system with Python
installed. We can even use 'mayapy' (installed with Maya), rather
than a standalone Python install.
"""

from __future__ import print_function

import sys
import os
import shutil
import zipfile
import tarfile

if sys.version_info[0] == 2:
    import urllib2
elif sys.version_info[0] == 3:
    import urllib.request as urllib2

def download_file(url, out_file, user_agent=None):
    print('Downloading: {}'.format(url))
    filedata = None
    if user_agent is None:
        filedata = urllib2.urlopen(url)
    else:
        req = urllib2.Request(url)
        req.add_header('User-Agent', user_agent)
        filedata = urllib2.urlopen(req)
    data = filedata.read()
    print('Saving Archive: {}'.format(out_file))
    with open(out_file, 'wb') as f:
        f.write(data)
    return out_file


def unpack_zip_archive(input_file, output_dir):
    with zipfile.ZipFile(input_file, 'r') as f:
        print('Extracting: {}'.format(output_dir))
        f.extractall(output_dir)
    return


def unpack_tarball_archive(input_file, output_dir):
    with tarfile.open(input_file, 'r') as f:
        print('Extracting: {}'.format(output_dir)
        f.extractall(output_dir)
    return


def unpack_archive(input_file, output_dir):
    print('Unpacking: {}'.format(input_file))
    if input_file.endswith('.zip'):
        unpack_zip_archive(input_file, output_dir)
    else:
        unpack_tarball_archive(input_file, output_dir)
    return output_dir


def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    # else:
    #     raise


def add_package(name, archive_name, url, archives_dir, working_dir, user_agent=None):
    print('Adding Package: {}'.format(name))
    out_file = os.path.join(archives_dir, archive_name)
    out_file = os.path.abspath(out_file)
    out_dir = os.path.join(working_dir, name)
    out_dir = os.path.abspath(out_dir)

    # Download
    archive = out_file
    if os.path.isfile(out_file) is False:
        archive = download_file(url, out_file, user_agent=user_agent)

    # Unpack
    if os.path.isdir(out_dir):
        print('Cleaning: {}'.format(out_dir))
        shutil.rmtree(out_dir, ignore_errors=False, onerror=onerror)
    unpack_archive(archive, working_dir)
    return

