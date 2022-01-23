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
Solver nodes for the mmSolver Window UI.

.. note:: This is part of the LEGACY solver, and is considered deprecated.

Solvers are presented to the user as Solver Steps, which is a step of
solver functions defined by:
- Frames
- Attribute Filter
- Strategy

'Frames' is the list of frames to compute the strategy on.

'Attribute Filter' provides a method to filter types of attributes
that will be used in the strategy. For example: Animated Only
attributes, or Static and Animated attributes.

'Strategy' is a method name for the solvers to be ordered to solve the
 frames in, for example 'sequentially' or 'all frames at once'.

If 'Animated Only' attribute filter is used then the strategy is
 unneeded and will solve each frame individually.

The ability to add new solver steps should be given with a + and -
button at top-right.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.utils.python_compat as pycompat
import mmSolver.ui.uimodels as uimodels
import mmSolver.ui.converttypes as converttypes
import mmSolver.ui.nodes as nodes
import mmSolver.logger
import mmSolver.tools.solver.lib.collection as lib_collection
import mmSolver.tools.solver.constant as const


LOG = mmSolver.logger.get_logger()


class StrategyComboBoxDelegate(uimodels.ComboBoxDelegate):

    def __init__(self, parent=None):
        super(StrategyComboBoxDelegate, self).__init__(parent)

    def getValueList(self):
        values = [
            str(const.STRATEGY_TWO_FRAMES_FWD_LABEL),
            str(const.STRATEGY_ALL_FRAMES_AT_ONCE_LABEL),
        ]
        return values


class AttributeComboBoxDelegate(uimodels.ComboBoxDelegate):

    def __init__(self, parent=None):
        super(AttributeComboBoxDelegate, self).__init__(parent)

    def getValueList(self):
        values = [
            str(const.ATTR_FILTER_STATIC_AND_ANIM_LABEL),
            str(const.ATTR_FILTER_ANIM_ONLY_LABEL),
        ]
        return values


class SolverStepNode(nodes.Node):
    def __init__(self, name, col_node,
                 parent=None,
                 data=None,
                 icon=None,
                 enabled=True,
                 editable=True,
                 selectable=True,
                 checkable=True,
                 neverHasChildren=False):
        if isinstance(name, pycompat.TEXT_TYPE) is False:
            raise TypeError
        if icon is None:
            icon = const.SOLVER_STEP_ICON_NAME
        if isinstance(data, dict) is False:
            data = {}
        data['collection_node'] = col_node
        super(SolverStepNode, self).__init__(
            name,
            data=data,
            parent=parent,
            icon=icon,
            enabled=enabled,
            selectable=selectable,
            editable=editable,
            checkable=checkable,
            neverHasChildren=neverHasChildren)
        self.typeInfo = 'solverStep'

    def collectionNode(self):
        return self.data().get('collection_node')

    def setCollectionNode(self, value):
        d = self.data()
        d['collection_node'] = value
        self.setData(d)

    def stepNode(self):
        col = self.collectionNode()
        name = self.name()
        n = lib_collection.get_named_solver_step_from_collection(col, name)
        return n

    def setStepNode(self, node):
        col = self.collectionNode()
        lib_collection.set_named_solver_step_to_collection(col, node)
        return

    def stepEnabled(self):
        n = self.stepNode()
        if n is None:
            return 'False'
        v = n.get_enabled()
        return converttypes.booleanToString(v)

    def setStepEnabled(self, value):
        v = converttypes.stringToBoolean(value)
        if v is None:
            return
        n = self.stepNode()
        if n is None:
            return
        n.set_enabled(v)
        self.setStepNode(n)
        return

    def frames(self):
        # if the option 'override current frame' is on, we ignore the actual
        # value.
        col = self.collectionNode()
        cur_frame = lib_collection.get_override_current_frame_from_collection(col)
        if cur_frame is True:
            return 'CURRENT'

        n = self.stepNode()
        if n is None:
            return '1'
        int_list = n.get_frame_list()
        string = converttypes.intListToString(int_list)
        return string

    def setFrames(self, value):
        int_list = converttypes.stringToIntList(value)
        n = self.stepNode()
        if n is None:
            return
        n.set_frame_list(int_list)
        self.setStepNode(n)
        return

    def strategy(self):
        """
        The strategy of how to compute the frames

        A strategy order to solve the frames in.
        This strategy is only needed for static attribute computation.
        """
        n = self.stepNode()
        if n is None:
            return const.STRATEGY_PER_FRAME_LABEL
        col = self.collectionNode()
        cur_frame = lib_collection.get_override_current_frame_from_collection(col)
        if cur_frame is True:
            return const.STRATEGY_PER_FRAME_LABEL
        v = n.get_strategy()
        assert v in const.STRATEGY_LIST
        idx = const.STRATEGY_LIST.index(v)

        # If we are not solving any static attributes, we show the
        # solver strategy as 'Per-Frame'
        use_static = n.get_use_static_attrs()
        value = const.STRATEGY_PER_FRAME_LABEL
        if use_static is True:
            value = const.STRATEGY_LABEL_LIST[idx]
        return value

    def setStrategy(self, value):
        assert value in const.STRATEGY_LABEL_LIST
        idx = const.STRATEGY_LABEL_LIST.index(value)
        v = const.STRATEGY_LIST[idx]
        n = self.stepNode()
        if n is None:
            return
        n.set_strategy(v)
        self.setStepNode(n)
        return

    def attrs(self):
        v = '?'
        n = self.stepNode()
        if n is None:
            return v
        use_static = n.get_use_static_attrs()
        use_animated = n.get_use_anim_attrs()
        if use_static is True and use_animated is True:
            v = const.ATTR_FILTER_STATIC_AND_ANIM_LABEL
        elif use_static is False and use_animated is True:
            v = const.ATTR_FILTER_ANIM_ONLY_LABEL
        elif use_static is True and use_animated is False:
            v = const.ATTR_FILTER_STATIC_ONLY_LABEL
        elif use_static is False and use_animated is False:
            v = const.ATTR_FILTER_NO_ATTRS_LABEL
        return v

    def setAttrs(self, value):
        use_static = False
        use_animated = True
        if value == const.ATTR_FILTER_STATIC_AND_ANIM_LABEL:
            use_static = True
            use_animated = True
        elif value == const.ATTR_FILTER_ANIM_ONLY_LABEL:
            use_static = False
            use_animated = True
        assert use_static is not None
        assert use_animated is not None
        n = self.stepNode()
        if n is None:
            return
        n.set_use_anim_attrs(use_animated)
        n.set_use_static_attrs(use_static)

        strategy = const.STRATEGY_ALL_FRAMES_AT_ONCE
        if value == const.ATTR_FILTER_ANIM_ONLY_LABEL:
            strategy = const.STRATEGY_PER_FRAME
        elif value == const.ATTR_FILTER_STATIC_AND_ANIM_LABEL:
            if n.get_strategy() == const.STRATEGY_PER_FRAME:
                strategy = const.STRATEGY_ALL_FRAMES_AT_ONCE

        n.set_strategy(strategy)
        self.setStepNode(n)
        return


class SolverModel(uimodels.TableModel):
    def __init__(self, node_list=None, font=None):
        super(SolverModel, self).__init__(node_list=node_list, font=font)

    def defaultNodeType(self):
        return SolverStepNode

    def columnNames(self):
        column_names = {
            0: const.SOLVER_COLUMN_NAME_ENABLED,
            1: const.SOLVER_COLUMN_NAME_FRAMES,
            2: const.SOLVER_COLUMN_NAME_ATTRIBUTES,
            3: const.SOLVER_COLUMN_NAME_STRATEGY,
        }
        return column_names

    def getGetAttrFuncFromIndex(self, index):
        get_attr_dict = {
            # Column Name to node function name
            const.SOLVER_COLUMN_NAME_ENABLED: 'stepEnabled',
            const.SOLVER_COLUMN_NAME_FRAMES: 'frames',
            const.SOLVER_COLUMN_NAME_STRATEGY: 'strategy',
            const.SOLVER_COLUMN_NAME_ATTRIBUTES: 'attrs',
        }
        return self._getGetAttrFuncFromIndex(index, get_attr_dict)

    def getSetAttrFuncFromIndex(self, index):
        set_attr_dict = {
            # Column Name to node function name
            const.SOLVER_COLUMN_NAME_ENABLED: 'setStepEnabled',
            const.SOLVER_COLUMN_NAME_FRAMES: 'setFrames',
            const.SOLVER_COLUMN_NAME_STRATEGY: 'setStrategy',
            const.SOLVER_COLUMN_NAME_ATTRIBUTES: 'setAttrs',
        }
        return self._getSetAttrFuncFromIndex(index, set_attr_dict)

    def indexCheckable(self, index):
        row_index = index.row()
        column_index = index.column()
        node = self._node_list[row_index]
        column_names = self.columnNames()
        checkable_column_mapping = {
            const.SOLVER_COLUMN_NAME_ENABLED: True,
            const.SOLVER_COLUMN_NAME_FRAMES: False,
            const.SOLVER_COLUMN_NAME_STRATEGY: False,
            const.SOLVER_COLUMN_NAME_ATTRIBUTES: False,
        }
        checkable = uimodels.getNameFromDict(
            column_index,
            column_names,
            checkable_column_mapping,
        )
        return checkable

    def indexEnabled(self, index):
        """
        Control if the given index is enabled or not.
        """
        row_index = index.row()
        column_index = index.column()
        node = self._node_list[row_index]
        if node.enabled() is False:
            return False
        column_names = self.columnNames()
        column_name = self.getColumnNameFromIndex(index)
        enabled = False
        if column_name == const.SOLVER_COLUMN_NAME_ENABLED:
            return True
        else:
            stepEnabled = node.stepEnabled()
            stepEnabled = converttypes.stringToBoolean(stepEnabled)
            if stepEnabled is False:
                return False

        # The step is enabled!
        if column_name in [const.SOLVER_COLUMN_NAME_FRAMES,
                           const.SOLVER_COLUMN_NAME_ATTRIBUTES]:
            enabled = True
        elif column_name == const.SOLVER_COLUMN_NAME_STRATEGY:
            # The 'strategy' column should be disabled if
            # 'attrs' is set to use either 'No Attributes' or
            # 'Animated Only'.
            attrs = node.attrs()
            if attrs in [const.ATTR_FILTER_STATIC_ONLY_LABEL,
                         const.ATTR_FILTER_STATIC_AND_ANIM_LABEL]:
                enabled = True

        # When 'Override Current Frame' is on, frames and strategy
        # should be editable.
        if column_name in [const.SOLVER_COLUMN_NAME_FRAMES,
                           const.SOLVER_COLUMN_NAME_STRATEGY]:
            col = node.collectionNode()
            cur_frame = lib_collection.get_override_current_frame_from_collection(col)
            if cur_frame is True:
                return False

        return enabled
