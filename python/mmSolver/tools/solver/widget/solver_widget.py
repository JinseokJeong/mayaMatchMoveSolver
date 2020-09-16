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
Widget class to hold all Solver Settings for the solver GUI.
"""

import time

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.solver.lib.state as lib_state
import mmSolver.tools.solver.lib.collectionstate as lib_col_state
import mmSolver.tools.solver.widget.ui_solver_widget as ui_solver_widget
import mmSolver.tools.solver.widget.solver_standard_widget as solver_standard_widget
import mmSolver.tools.solver.widget.solver_basic_widget as solver_basic_widget
import mmSolver.tools.solver.widget.solver_legacy_widget as solver_legacy_widget


LOG = mmSolver.logger.get_logger()


def _populateWidgetsEnabled(widgets):
    col = lib_state.get_active_collection()
    enabled = col is not None
    for widget in widgets:
        widget.setEnabled(enabled)
    return


class SolverWidget(QtWidgets.QWidget, ui_solver_widget.Ui_Form):

    tabChanged = QtCore.Signal()
    dataChanged = QtCore.Signal()
    sendWarning = QtCore.Signal(str)

    def __init__(self, parent=None, *args, **kwargs):
        s = time.time()
        super(SolverWidget, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Solver Settings Basic Widget
        self.basic_widget = solver_basic_widget.SolverBasicWidget(self)
        self.basic_layout.addWidget(self.basic_widget)

        # Solver Settings Standard Widget
        self.standard_widget = solver_standard_widget.SolverStandardWidget(self)
        self.standard_layout.addWidget(self.standard_widget)

        # Solver Settings Legacy Widget
        self.legacy_widget = solver_legacy_widget.SolverLegacyWidget(self)
        self.legacy_layout.addWidget(self.legacy_widget)

        self._tab_name_to_index_map = {
            'basic': 0,
            'standard': 1,
            'legacy': 2,
        }
        self._tab_index_to_widget_map = {
            0: self.basic_widget,
            1: self.standard_widget,
            2: self.legacy_widget,
        }
        self.all_tab_widgets = [
            self.basic_widget,
            self.standard_widget,
            self.legacy_widget
        ]

        self.validate_pushButton.setEnabled(False)

        self.tabWidget.currentChanged.connect(self._tabChanged)
        self.basic_widget.dataChanged.connect(self._dataChanged)
        self.standard_widget.dataChanged.connect(self._dataChanged)
        self.legacy_widget.dataChanged.connect(self._dataChanged)
        self.standard_widget.sendWarning.connect(self._sendWarningToUser)
        self.standard_widget.sendWarning.connect(self._sendWarningToUser)

        self.basic_widget.frameRange_widget.rangeTypeChanged.connect(self.updateInfo)
        self.basic_widget.frameRange_widget.framesChanged.connect(self.updateInfo)
        self.basic_widget.frameRange_widget.incrementByFrameChanged.connect(self.updateInfo)
        self.standard_widget.frameRange_widget.rangeTypeChanged.connect(self.updateInfo)
        self.validate_pushButton.clicked.connect(self.runUpdateInfo)

        # First time we open this UI, we should update the solver info text.
        value = lib_state.get_auto_update_solver_validation_state()
        if value is False:
            self.validate_pushButton.clicked.emit()

        e = time.time()
        LOG.debug('SolverWidget init: %r seconds', e - s)
        return

    def getSolverTabValue(self, col):
        value = lib_col_state.get_solver_tab_from_collection(col)
        return value

    def setSolverTabValue(self, col, value):
        lib_col_state.set_solver_tab_on_collection(col, value)
        return

    @QtCore.Slot(int)
    def _tabChanged(self, idx):
        self.updateModel()

        # Store the tab name we've changed to.
        col = lib_state.get_active_collection()
        if col is not None:
            name = self.tabWidget.tabText(idx)
            name = name.lower()
            self.setSolverTabValue(col, name)

        self.tabChanged.emit()
        return

    def _dataChanged(self):
        self.dataChanged.emit()
        return

    def _getTabWidget(self, idx):
        widget = self._tab_index_to_widget_map.get(idx, None)
        if widget is None:
            raise RuntimeError('tab index is not valid: %r' % idx)
        assert widget is not None
        return widget

    def updateModel(self):
        is_running = mmapi.is_solver_running()
        if is_running is True:
            return
        col = lib_state.get_active_collection()
        if col is not None:
            tab_name = self.getSolverTabValue(col)
            tab_name = tab_name.lower()
            idx = self._tab_name_to_index_map.get(tab_name, None)
            if idx is None:
                msg = 'Solver tab name is not valid: %r' % tab_name
                raise ValueError(msg)
            self.tabWidget.setCurrentIndex(idx)

        idx = self.tabWidget.currentIndex()
        tab_widget = self._getTabWidget(idx)
        tab_widget.updateModel()

        widgets = [
            tab_widget,
            self.info_label,
        ]
        _populateWidgetsEnabled(widgets)
        self.updateInfo()
        return

    def updateInfo(self):
        is_running = mmapi.is_solver_running()
        if is_running is True:
            return

        value = lib_state.get_auto_update_solver_validation_state()
        self.validate_pushButton.setEnabled(not value)
        if value is not True:
            return

        self.runUpdateInfo()
        return

    def runUpdateInfo(self):
        s = time.time()
        idx = self.tabWidget.currentIndex()
        tab_widget = self._getTabWidget(idx)
        text = tab_widget.queryInfo()
        self.info_label.setText(text)
        e = time.time()
        LOG.debug('SolverWidget runUpdateInfo: %r seconds', e - s)
        return

    @QtCore.Slot(bool)
    def autoUpdateSolverValidationChanged(self, value):
        lib_state.set_auto_update_solver_validation_state(value)
        self.updateInfo()
        return

    @QtCore.Slot(str)
    def _sendWarningToUser(self, value):
        self.sendWarning.emit(value)
        return
