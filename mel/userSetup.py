#
# Copyright (C) 2018, 2019 David Cattermole.
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
A start-up script for mmSolver.

We use the Python 'userSetup.py' file rather than 'userSetup.mel'
because of the message here:
https://around-the-corner.typepad.com/adn/2012/07/distributing-files-on-maya-maya-modules.html

"""

import os
import maya.cmds
import maya.utils
import mmSolver.logger


LOG = mmSolver.logger.get_logger()
MMSOLVER_STARTED = False


def mmsolver_create_shelf():
    """
    Build the mmSolver shelf.
    """
    import mmSolver.tools.mmshelf.tool
    mmSolver.tools.mmshelf.tool.build_shelf()


def mmsolver_create_menu():
    """
    Build the mmSolver menu.
    """
    import mmSolver.tools.mmmenu.tool
    mmSolver.tools.mmmenu.tool.build_menu()


def mmsolver_create_hotkey_set():
    """
    Create the mmSolver Hotkey Set.
    """
    import mmSolver.tools.mmhotkeyset.tool
    mmSolver.tools.mmhotkeyset.tool.build_hotkey_set()


def mmsolver_startup():
    """
    Responsible for starting up mmSolver, including creating shelves,
    hotkeys and menus.
    """
    LOG.info('MM Solver Startup...')

    global MMSOLVER_STARTED
    MMSOLVER_STARTED = True

    # Only run GUI code when the Maya interactive GUI opens.
    is_batch_mode = maya.cmds.about(batch=True)
    LOG.debug('Batch Mode: %r', is_batch_mode)
    if is_batch_mode is False:
        # Create Menu.
        build_menu = bool(int(os.environ.get('MMSOLVER_CREATE_MENU', 1)))
        LOG.debug('Build Menu: %r', build_menu)
        if build_menu is True:
            maya.utils.executeDeferred(mmsolver_create_menu)

        # Create Shelf.
        build_shelf = bool(int(os.environ.get('MMSOLVER_CREATE_SHELF', 1)))
        LOG.debug('Build Shelf: %r', build_shelf)
        if build_shelf is True:
            maya.utils.executeDeferred(mmsolver_create_shelf)

        # Create Hotkey Set.
        build_hotkey_set = bool(int(os.environ.get('MMSOLVER_CREATE_HOTKEY_SET', 1)))
        LOG.debug('Build Hotkey Set: %r', build_hotkey_set)
        if build_hotkey_set is True:
            maya.utils.executeDeferred(mmsolver_create_hotkey_set)
    return


# Run Start up Function after Maya has loaded.
load_at_startup = bool(int(os.environ.get('MMSOLVER_LOAD_AT_STARTUP', 1)))
if load_at_startup is True:
    maya.utils.executeDeferred(mmsolver_startup)
