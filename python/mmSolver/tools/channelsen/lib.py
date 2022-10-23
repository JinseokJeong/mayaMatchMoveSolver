# Copyright (C) 2019 Anil Reddy.
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
The Channel Sensitivity tool - user facing.
"""

import maya.cmds
import maya.mel
import mmSolver.logger

import mmSolver.ui.channelboxutils as channelbox_utils

LOG = mmSolver.logger.get_logger()


def get_value():
    """
    Get the current channel sensitivity value.

    :return: Current channel sensitivity value
    :rtype: float
    """
    channel_box = channelbox_utils.get_ui_name()
    if channel_box is None:
        LOG.warning('Channel Box was not found, cannot set sensitivity.')
    value = maya.cmds.channelBox(channel_box, query=True, speed=True)
    return value


def set_value(value):
    """
    Set channel sensitivity value.

    :param value: A possible value to set channel sensitivity
                  value
    :return: None
    """
    channel_box = channelbox_utils.get_ui_name()
    if channel_box is None:
        LOG.warning('Channel Box was not found, cannot set sensitivity.')

    # Maya 2017 doesn't have a channel box sensitivity icon, but Maya
    # 2016 and 2018 does. Lets just check rather than hard-code
    # version-specific behaviour.
    button_exists = maya.cmds.control('cbManipsButton', exists=True)
    if button_exists is True:
        cmd = 'channelBoxSettings useManips 1;'
        maya.mel.eval(cmd)

    maya.cmds.channelBox(channel_box, edit=True, speed=value)
    return
