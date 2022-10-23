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
Solver tool scene data manipulation.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import maya.cmds
import mmSolver.logger
import mmSolver.tools.solver.constant as const

LOG = mmSolver.logger.get_logger()


def _get_scene_data_node():
    nodes = maya.cmds.ls(sl=True, long=True) or []

    node_name = const.MM_SOLVER_DATA_NODE_NAME
    node_type = const.MM_SOLVER_DATA_NODE_TYPE
    attr_name = const.MM_SOLVER_DATA_ATTR_NAME
    plug = node_name + '.' + attr_name

    # Ensure node exists.
    node = node_name
    if maya.cmds.objExists(node_name) is False:
        node = maya.cmds.createNode(
            node_type,
            name=node_name,
            skipSelect=True,
        )

    # Ensure attribute exists.
    attrs = maya.cmds.listAttr(node_name)
    if attr_name not in attrs:
        maya.cmds.addAttr(node, longName=attr_name, dataType='string')
        value = json.dumps(dict())
        maya.cmds.setAttr(plug, value, type='string')
        maya.cmds.setAttr(plug, lock=True)

    if len(nodes) > 0:
        maya.cmds.select(nodes, replace=True)
    return node


def _get_scene_data_value(node):
    attr_name = const.MM_SOLVER_DATA_ATTR_NAME
    plug = node + '.' + attr_name
    attr_value = maya.cmds.getAttr(plug)
    data = json.loads(attr_value)
    if isinstance(data, dict) is False:
        msg = 'Stored scene data should always be dict. '
        msg += 'Something went wrong! '
        msg += 'attr_value=%r data=%r'
        raise TypeError(msg % (attr_value, data))
    return data


def _set_scene_data_value(node, data):
    if maya.cmds.objExists(node) is False:
        msg = 'node must exist. '
        msg += 'node=%r'
        raise TypeError(msg % node)
    if isinstance(data, dict) is False:
        msg = 'data must be of dict type. '
        msg += 'node=%r data=%r'
        raise TypeError(msg % (node, data))
    attr_name = const.MM_SOLVER_DATA_ATTR_NAME
    plug = node + '.' + attr_name
    attr_value = json.dumps(data)
    maya.cmds.setAttr(plug, lock=False)
    maya.cmds.setAttr(plug, attr_value, type='string')
    maya.cmds.setAttr(plug, lock=True)
    return


def get_scene_data(name):
    node = _get_scene_data_node()
    data = _get_scene_data_value(node)
    return data.get(name)


def set_scene_data(name, value):
    node = _get_scene_data_node()
    data = _get_scene_data_value(node)
    data[name] = value
    _set_scene_data_value(node, data)
    return
