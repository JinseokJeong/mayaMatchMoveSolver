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
Marker functions.
"""

import time

import maya.cmds
import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.solver.maya_callbacks as maya_callbacks
import mmSolver.tools.solver.lib.callbacks as lib_callbacks


LOG = mmSolver.logger.get_logger()


def add_markers_to_collection(mkr_list, col):
    s = time.time()
    if isinstance(col, mmapi.Collection) is False:
        msg = 'col argument must be a Collection: %r'
        raise TypeError(msg % col)
    col.add_marker_list(mkr_list)
    e = time.time()
    LOG.debug('add_markers_to_collection: %r seconds', e - s)
    return


def remove_markers_from_collection(mkr_list, col):
    s = time.time()
    result = col.remove_marker_list(mkr_list)
    e = time.time()
    LOG.debug('remove_markers_from_collection: %r seconds', e - s)
    return result


def get_markers_from_collection(col):
    s = time.time()
    mkr_list = col.get_marker_list()
    e = time.time()
    LOG.debug('get_markers_from_collection: %r seconds', e - s)
    return mkr_list


def add_callbacks_to_markers(mkr_list, callback_manager):
    s = time.time()

    callback_type = maya_callbacks.TYPE_MARKER
    for mkr_obj in mkr_list:
        # Marker
        mkr_node_path = mkr_obj.get_node()
        lib_callbacks.add_callback_to_any_node(
            callback_manager,
            callback_type,
            mkr_node_path,
            maya_callbacks.add_callbacks_to_marker,
        )

        # Bundle
        bnd_obj = mkr_obj.get_bundle()
        bnd_node_path = bnd_obj.get_node()
        lib_callbacks.add_callback_to_any_node(
            callback_manager,
            callback_type,
            bnd_node_path,
            maya_callbacks.add_callbacks_to_bundle,
        )

        # Marker Group
        mkrgrp_obj = mkr_obj.get_marker_group()
        mkrgrp_node_path = mkrgrp_obj.get_node()
        lib_callbacks.add_callback_to_any_node(
            callback_manager,
            callback_type,
            mkrgrp_node_path,
            maya_callbacks.add_callbacks_to_marker_group,
        )

        # Camera Transform
        cam_obj = mkr_obj.get_camera()
        cam_tfm_node_path = cam_obj.get_transform_node()
        lib_callbacks.add_callback_to_any_node(
            callback_manager,
            callback_type,
            cam_tfm_node_path,
            maya_callbacks.add_callbacks_to_camera,
        )

        # Camera Shape
        cam_shp_node_path = cam_obj.get_shape_node()
        lib_callbacks.add_callback_to_any_node(
            callback_manager,
            callback_type,
            cam_shp_node_path,
            maya_callbacks.add_callbacks_to_camera,
        )

    e = time.time()
    LOG.debug('add_callbacks_to_markers: %r seconds', e - s)
    return


def remove_callbacks_from_markers(mkr_list, callback_manager):
    s = time.time()
    msg = 'Node UUID has multiple paths: node=%r node_uuids=%r'

    callback_type = maya_callbacks.TYPE_MARKER
    for mkr_obj in mkr_list:
        bnd_obj = mkr_obj.get_bundle()
        cam_obj = mkr_obj.get_camera()
        mkrgrp_obj = mkr_obj.get_marker_group()

        mkr_node_path = mkr_obj.get_node()
        bnd_node_path = bnd_obj.get_node()
        mkrgrp_node_path = mkrgrp_obj.get_node()
        cam_tfm_node_path = cam_obj.get_transform_node()
        cam_shp_node_path = cam_obj.get_shape_node()
        node_path_list = [
            mkr_node_path,
            bnd_node_path,
            mkrgrp_node_path,
            cam_tfm_node_path,
            cam_shp_node_path,
        ]
        for node_path in node_path_list:
            node_uuids = maya.cmds.ls(node_path, uuid=True) or []
            if len(node_uuids) != 1:
                LOG.warning(msg, node_path, node_uuids)
                continue
            node_uuid = node_uuids[0]
            have_type = callback_manager.type_has_node(callback_type, node_uuid)
            if have_type is False:
                continue
            callback_manager.remove_type_node_ids(
                callback_type,
                node_uuid,
            )

    e = time.time()
    LOG.debug('remove_callbacks_from_markers: %r seconds', e - s)
    return
