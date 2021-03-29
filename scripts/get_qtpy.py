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
Get the Qt.py code.
"""

import sys
import os

sys.path.append(os.path.dirname(__file__))
import download_unpack


def main(archives_dir, working_dir, patches_dir):
    user_agent = None
    url = 'https://github.com/mottosso/Qt.py/archive/1.2.0.tar.gz'
    archive_name = 'Qt.py-1.2.0.tar.gz'
    name = 'Qt.py-1.2.0'
    download_unpack.add_package(
        name,
        archive_name,
        url,
        archives_dir,
        working_dir,
        user_agent=user_agent)
    return


if __name__ == '__main__':
    archives_dir = os.path.abspath(sys.argv[1])
    working_dir = os.path.abspath(sys.argv[2])
    patches_dir = os.path.abspath(sys.argv[3])
    main(archives_dir, working_dir, patches_dir)
