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
Module for attributes and related functions.
"""

import maya.cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim

import mmSolver.utils.node as node_utils
import mmSolver._api.utils as api_utils
import mmSolver._api.constant as const
import mmSolver.logger

LOG = mmSolver.logger.get_logger()


class Attribute(object):
    """
    The Attribute - A variable, or set of variables over time to solve.

    Example usage::

        >>> import mmSolver.api as mmapi
        >>> node = maya.cmds.createNode('transform', name='myNode')
        >>> attr = mmapi.Attribute(node=node, attr='tx')
        >>> attr.get_node()
        '|myNode'
        >>> attr.get_attr()
        'translateX'
        >>> attr.get_attr(long_name=False)
        'tx'
        >>> attr.get_name()
        '|myNode.translateX'
        >>> attr.get_state()
        1  # 1 == ATTR_STATE_STATIC

    """
    def __init__(self, name=None, node=None, attr=None):
        """
        Initialise an Attribute object.

        Attribute can use a 'name', or 'node' and 'attr'.

        A 'name' is a string of both node and attribute path; `node.attr`.

        :param name: Node and attribute path as a single string: 'node.attr'
        :type name: str

        :param node: DG Maya node path.
        :type node: str

        :param attr: Long or short attribute name.
        :type attr: str
        """
        if isinstance(name, (str, unicode)):
            assert api_utils.get_object_type(name) == const.OBJECT_TYPE_ATTRIBUTE
            part = name.partition('.')
            node = part[0]
            attr = part[-1]

        self._plug = None
        self._dependFn = None
        if isinstance(node, (str, unicode)) and isinstance(attr, (str, unicode)):
            assert maya.cmds.objExists(node)
            # Long and short names must be checked.
            attr_list_long = maya.cmds.listAttr(node, shortNames=False) or []
            attr_list_short = maya.cmds.listAttr(node, shortNames=True) or []
            if attr not in (attr_list_long + attr_list_short):
                msg = 'Attribute not found on node. node=%r attr=%r'
                LOG.error(msg, node, attr)
                raise RuntimeError(msg)

            node_attr = node + '.' + attr
            plug = node_utils.get_as_plug(node_attr)
            self._plug = plug

            node_obj = self._plug.node()
            self._dependFn = OpenMaya.MFnDependencyNode(node_obj)
        return

    def __repr__(self):
        result = '<{class_name}('.format(class_name=self.__class__.__name__)
        result += '{hash} name={name}'
        result += ')>'
        result = result.format(
            hash=hex(hash(self)),
            name=self.get_name(),
        )
        return result

    def get_node(self, full_path=True):
        node = None
        if self._dependFn is not None:
            try:
                node = self._dependFn.name()
            except RuntimeError:
                pass
        if node is not None and full_path is True:
            node = node_utils.get_long_name(node)
        return node

    def get_node_uid(self):
        """
        Get the Attribute's node unique identifier.

        :return: The Attribute UUID or None
        :rtype: None or str or unicode
        """
        node = self.get_node()
        if node is None:
            return None
        uids = maya.cmds.ls(node, uuid=True) or []
        return uids[0]

    def get_attr(self, long_name=True):
        name = None
        if self._plug is not None:
            include_node_name = False
            include_non_mandatory_indices = True
            include_instanced_indices = True
            use_alias = False
            use_full_attribute_path = False
            name = self._plug.partialName(
                include_node_name,
                include_non_mandatory_indices,
                include_instanced_indices,
                use_alias,
                use_full_attribute_path,
                long_name  # use long name.
            )
        return name

    def get_name(self, full_path=True):
        name = None
        node = self.get_node(full_path=full_path)
        attr = self.get_attr(long_name=full_path)
        if (isinstance(node, (str, unicode)) and
                isinstance(attr, (str, unicode))):
            name = node + '.' + attr
        return name

    def get_state(self):
        state = const.ATTR_STATE_INVALID

        check_parents = True
        check_children = True
        free = self._plug.isFreeToChange(check_parents, check_children)
        if free != OpenMaya.MPlug.kFreeToChange:
            state = const.ATTR_STATE_LOCKED
            return state

        check_parents = False
        animPlugs = OpenMaya.MPlugArray()
        OpenMayaAnim.MAnimUtil.findAnimatedPlugs(self._plug.node(),
                                                 animPlugs,
                                                 check_parents)
        for i in range(animPlugs.length()):
            plug = animPlugs[i]
            if self._plug.name() == plug.name():
                state = const.ATTR_STATE_ANIMATED

        if state == const.ATTR_STATE_INVALID:
            state = const.ATTR_STATE_STATIC

        return state

    def is_static(self):
        return self.get_state() == const.ATTR_STATE_STATIC

    def is_animated(self):
        return self.get_state() == const.ATTR_STATE_ANIMATED

    def is_locked(self):
        return self.get_state() == const.ATTR_STATE_LOCKED
