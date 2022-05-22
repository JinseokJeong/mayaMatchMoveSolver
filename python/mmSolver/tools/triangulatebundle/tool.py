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
Triangulate a 3D Bundle from a 2D Marker.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.triangulatebundle.lib as lib


LOG = mmSolver.logger.get_logger()


def main():
    """
    Triangulate Bundle using camera and Marker.

    Usage:

    1) Select markers or bundles (or both).

    2) Run tool.

    3) Bundle is triangulated in TX, TY and TZ.
    """
    # Get Markers and Bundles
    sel = maya.cmds.ls(selection=True, long=True) or []
    filter_nodes = mmapi.filter_nodes_into_categories(sel)
    mkr_nodes = filter_nodes.get(mmapi.OBJECT_TYPE_MARKER, [])
    bnd_nodes = filter_nodes.get(mmapi.OBJECT_TYPE_BUNDLE, [])
    if len(mkr_nodes) == 0 and len(bnd_nodes) == 0:
        msg = 'Please select at least one marker / bundle!'
        LOG.warning(msg)
        return

    # Get Bundles from Markers
    for mkr_node in mkr_nodes:
        mkr = mmapi.Marker(node=mkr_node)
        bnd = mkr.get_bundle()
        bnd_node = bnd.get_node()
        if bnd_node not in bnd_nodes:
            bnd_nodes.append(bnd_node)
    bnd_list = [mmapi.Bundle(node=node) for node in bnd_nodes]

    # Triangulate
    adjusted_bnd_node_list = []
    for bnd in bnd_list:
        lib.triangulate_bundle(bnd)
        adjusted_bnd_node_list.append(bnd.get_node())

    # Select all bundle nodes.
    if len(adjusted_bnd_node_list) > 0:
        maya.cmds.select(adjusted_bnd_node_list, replace=True)
    else:
        msg = 'No Bundle nodes found, see Script Editor for details.'
        LOG.warning(msg)
    return
