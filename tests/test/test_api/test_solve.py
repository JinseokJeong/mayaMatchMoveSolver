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
Solve a single non-animated bundle to the screen-space location of a bundle.

This test is the same as 'test.test_solver.test1' except this test uses the
Python API. It's a basic example of how to use the API.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time
import pprint
import math
import unittest

import maya.cmds

import mmSolver.logger
import mmSolver.utils.time as time_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver.api as mmapi
import mmSolver.tools.solver.lib.collection as lib_col
import mmSolver.tools.loadmarker.lib.mayareadfile as marker_read
import test.test_api.apiutils as test_api_utils


LOG = mmSolver.logger.get_logger()


# @unittest.skip
class TestSolve(test_api_utils.APITestCase):

    def checkSolveResults(self, solres_list):
        # Ensure the values are correct
        for res in solres_list:
            success = res.get_success()
            err = res.get_final_error()
            print('final error', success, err)
            self.assertTrue(success)
            self.assertTrue(isinstance(err, float))

        # Check the final error values
        frm_err_list = mmapi.merge_frame_error_list(solres_list)

        avg_err = mmapi.get_average_frame_error_list(frm_err_list)
        print('avg error', avg_err)

        max_err_frm, max_err_val = mmapi.get_max_frame_error(frm_err_list)
        print('max error frame and value:', max_err_frm, max_err_val)
        self.assertLess(avg_err, 1.0)
        self.assertGreater(avg_err, 0.0)
        self.assertLess(max_err_val, 1.0)
        self.assertGreater(max_err_val, 0.0)
        return

    def test_init(self):
        """
        Single Frame solve.
        """
        # Camera
        cam_tfm = maya.cmds.createNode('transform',
                                       name='cam_tfm')
        cam_shp = maya.cmds.createNode('camera',
                                       name='cam_shp',
                                       parent=cam_tfm)
        maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', -5.0)
        cam = mmapi.Camera(shape=cam_shp)

        # Bundle
        bnd = mmapi.Bundle().create_node()
        bundle_tfm = bnd.get_node()
        maya.cmds.setAttr(bundle_tfm + '.tx', 5.5)
        maya.cmds.setAttr(bundle_tfm + '.ty', 6.4)
        maya.cmds.setAttr(bundle_tfm + '.tz', -25.0)
        assert mmapi.get_object_type(bundle_tfm) == 'bundle'

        # Marker
        mkr = mmapi.Marker().create_node(cam=cam, bnd=bnd)
        marker_tfm = mkr.get_node()
        assert mmapi.get_object_type(marker_tfm) == 'marker'
        maya.cmds.setAttr(marker_tfm + '.tx', 0.0)
        maya.cmds.setAttr(marker_tfm + '.ty', 0.0)

        # Attributes
        attr_tx = mmapi.Attribute(bundle_tfm + '.tx')
        attr_ty = mmapi.Attribute(bundle_tfm + '.ty')

        # Frames
        frm_list = [
            mmapi.Frame(1, primary=True)
        ]

        # Solver
        sol = mmapi.Solver()
        sol.set_max_iterations(10)
        sol.set_solver_type(mmapi.SOLVER_TYPE_DEFAULT)
        sol.set_verbose(True)
        sol.set_frame_list(frm_list)

        # Collection
        col = mmapi.Collection()
        col.create_node('mySolveCollection')
        col.add_solver(sol)
        col.add_marker(mkr)
        col.add_attribute(attr_tx)
        col.add_attribute(attr_ty)

        # save the output
        path = self.get_data_path('test_solve_init_before.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Run solver!
        results = mmapi.execute(col)

        # Set Deviation
        mmapi.update_deviation_on_markers([mkr], results)
        mmapi.update_deviation_on_collection(col, results)

        # save the output
        path = self.get_data_path('test_solve_init_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        self.checkSolveResults(results)
        # assert self.approx_equal(maya.cmds.getAttr(bundle_tfm+'.tx'), -6.0)
        # assert self.approx_equal(maya.cmds.getAttr(bundle_tfm+'.ty'), 3.6)
        return

    def test_init_solverstandard(self):
        """
        Single Frame solve, using the standard solver
        """
        # Camera
        cam_tfm = maya.cmds.createNode('transform',
                                       name='cam_tfm')
        cam_shp = maya.cmds.createNode('camera',
                                       name='cam_shp',
                                       parent=cam_tfm)
        maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', -5.0)
        cam = mmapi.Camera(shape=cam_shp)

        # Bundle
        bnd = mmapi.Bundle().create_node()
        bundle_tfm = bnd.get_node()
        maya.cmds.setAttr(bundle_tfm + '.tx', 5.5)
        maya.cmds.setAttr(bundle_tfm + '.ty', 6.4)
        maya.cmds.setAttr(bundle_tfm + '.tz', -25.0)
        assert mmapi.get_object_type(bundle_tfm) == 'bundle'

        # Marker
        mkr = mmapi.Marker().create_node(cam=cam, bnd=bnd)
        marker_tfm = mkr.get_node()
        assert mmapi.get_object_type(marker_tfm) == 'marker'
        maya.cmds.setAttr(marker_tfm + '.tx', 0.0)
        maya.cmds.setAttr(marker_tfm + '.ty', 0.0)

        # Attributes
        attr_tx = mmapi.Attribute(bundle_tfm + '.tx')
        attr_ty = mmapi.Attribute(bundle_tfm + '.ty')

        # Frames
        frm_list = [
            mmapi.Frame(1, primary=True)
        ]

        # Solver
        sol = mmapi.SolverStandard()
        sol.set_use_single_frame(True)
        sol.set_single_frame(frm_list[0])
        sol.set_global_solve(False)
        sol.set_only_root_frames(False)

        # Collection
        col = mmapi.Collection()
        col.create_node('mySolveCollection')
        col.add_solver(sol)
        col.add_marker(mkr)
        col.add_attribute(attr_tx)
        col.add_attribute(attr_ty)

        # save the output
        path = self.get_data_path('test_solve_init_solverstandard_before.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Run solver!
        results = mmapi.execute(col)

        # Set Deviation
        mmapi.update_deviation_on_markers([mkr], results)
        mmapi.update_deviation_on_collection(col, results)

        # save the output
        path = self.get_data_path('test_solve_init_solverstandard_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        self.checkSolveResults(results)
        # assert self.approx_equal(maya.cmds.getAttr(bundle_tfm+'.tx'), -6.0)
        # assert self.approx_equal(maya.cmds.getAttr(bundle_tfm+'.ty'), 3.6)
        return

    def test_marker_enable(self):
        start = 1
        end = 5

        # Set Time Range
        maya.cmds.playbackOptions(
            animationStartTime=start,
            minTime=start,
            animationEndTime=end,
            maxTime=end
        )

        # Camera
        cam_tfm = maya.cmds.createNode('transform',
                                       name='cam_tfm')
        cam_shp = maya.cmds.createNode('camera',
                                       name='cam_shp',
                                       parent=cam_tfm)
        maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', -5.0)
        cam = mmapi.Camera(shape=cam_shp)

        # Bundle
        bnd = mmapi.Bundle().create_node()
        bundle_tfm = bnd.get_node()
        maya.cmds.setAttr(bundle_tfm + '.tx', 5.5)
        maya.cmds.setAttr(bundle_tfm + '.ty', 6.4)
        maya.cmds.setAttr(bundle_tfm + '.tz', -25.0)
        assert mmapi.get_object_type(bundle_tfm) == 'bundle'

        # calculate angle of view (AOV)
        f = maya.cmds.getAttr(cam_shp + '.focalLength')
        fbw = maya.cmds.getAttr(cam_shp + '.horizontalFilmAperture') * 25.4
        fbh = maya.cmds.getAttr(cam_shp + '.verticalFilmAperture') * 25.4
        aov = math.degrees(2.0 * math.atan(fbw * (0.5 / f)))

        # Set Camera Anim
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateY', time=start, value=-(aov/2),
                              inTangentType='linear',
                              outTangentType='linear')
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateY', time=end, value=(aov/2),
                              inTangentType='linear',
                              outTangentType='linear')

        # Marker
        mkr = mmapi.Marker().create_node(cam=cam, bnd=bnd)
        marker_tfm = mkr.get_node()
        assert mmapi.get_object_type(marker_tfm) == 'marker'
        mid_value = 0.23534346
        maya.cmds.setKeyframe(marker_tfm, attribute='translateX', time=start, value=-0.5,
                              inTangentType='linear',
                              outTangentType='linear')
        maya.cmds.setKeyframe(marker_tfm, attribute='translateX', time=start+1,
                              value=-mid_value,
                              inTangentType='linear',
                              outTangentType='linear')
        maya.cmds.setKeyframe(marker_tfm, attribute='translateX', time=end-1,
                              value=mid_value,
                              inTangentType='linear',
                              outTangentType='linear')
        maya.cmds.setKeyframe(marker_tfm, attribute='translateX', time=end, value=0.5,
                              inTangentType='linear',
                              outTangentType='linear')
        maya.cmds.setAttr(marker_tfm + '.ty', 0.0)

        maya.cmds.setKeyframe(marker_tfm, attribute='enable', time=1, value=1,
                              inTangentType='linear',
                              outTangentType='linear')
        maya.cmds.setKeyframe(marker_tfm, attribute='enable', time=2, value=1,
                              inTangentType='linear',
                              outTangentType='linear')
        maya.cmds.setKeyframe(marker_tfm, attribute='enable', time=3, value=0,
                              inTangentType='linear',
                              outTangentType='linear')
        maya.cmds.setKeyframe(marker_tfm, attribute='enable', time=4, value=1,
                              inTangentType='linear',
                              outTangentType='linear')
        maya.cmds.setKeyframe(marker_tfm, attribute='enable', time=5, value=1,
                              inTangentType='linear',
                              outTangentType='linear')

        # Create Sphere
        sph_tfm, shp_node = maya.cmds.polySphere()
        maya.cmds.setAttr(sph_tfm + '.tx', -1.0)
        maya.cmds.setAttr(sph_tfm + '.ty', 1.0)
        maya.cmds.setAttr(sph_tfm + '.tz', -25.0)

        # Attributes
        attr_tx = mmapi.Attribute(bundle_tfm + '.tx')
        attr_ty = mmapi.Attribute(bundle_tfm + '.ty')

        # Frames
        frm_list = [
            mmapi.Frame(1, primary=True),
            mmapi.Frame(2, primary=True),
            mmapi.Frame(3, primary=True),
            mmapi.Frame(4, primary=True),
            mmapi.Frame(5, primary=True)
        ]

        # Solver
        sol = mmapi.Solver()
        sol.set_max_iterations(1000)
        sol.set_solver_type(mmapi.SOLVER_TYPE_DEFAULT)
        sol.set_verbose(True)
        sol.set_frame_list(frm_list)

        # Collection
        col = mmapi.Collection()
        col.create_node('mySolveCollection')
        col.add_solver(sol)
        col.add_marker(mkr)
        col.add_attribute(attr_tx)
        col.add_attribute(attr_ty)

        # save the output
        path = self.get_data_path('test_solve_marker_enabled_before.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Run solver!
        results = mmapi.execute(col)

        # Ensure the values are correct
        for res in results:
            success = res.get_success()
            err = res.get_final_error()
            print('error stats: ' + pprint.pformat(res.get_error_stats()))
            print('timer stats: ' + pprint.pformat(res.get_timer_stats()))
            print('solver stats: ' + pprint.pformat(res.get_solver_stats()))
            print('frame error list: ' + pprint.pformat(dict(res.get_frame_error_list())))
            print('marker error list: ' + pprint.pformat(dict(res.get_marker_error_list())))

            self.assertTrue(success)
            # self.assertGreater(0.001, err)
        # assert self.approx_equal(maya.cmds.getAttr(bundle_tfm+'.tx'), -6.0)
        # assert self.approx_equal(maya.cmds.getAttr(bundle_tfm+'.ty'), 3.6)

        # Set Deviation
        mmapi.update_deviation_on_markers([mkr], results)
        mmapi.update_deviation_on_collection(col, results)

        # save the output
        path = self.get_data_path('test_solve_marker_enabled_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.checkSolveResults(results)
        return

    def test_per_frame(self):
        """
        Solve animated values, per-frame.
        """
        # Camera
        cam_tfm = maya.cmds.createNode('transform',
                                       name='cam_tfm')
        cam_shp = maya.cmds.createNode('camera',
                                       name='cam_shp',
                                       parent=cam_tfm)
        maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', -5.0)
        cam = mmapi.Camera(shape=cam_shp)

        # Bundle
        bnd = mmapi.Bundle().create_node()
        bundle_tfm = bnd.get_node()
        maya.cmds.setAttr(bundle_tfm + '.tx', 5.5)
        maya.cmds.setAttr(bundle_tfm + '.ty', 6.4)
        maya.cmds.setAttr(bundle_tfm + '.tz', -25.0)
        assert mmapi.get_object_type(bundle_tfm) == 'bundle'
        maya.cmds.setKeyframe(bundle_tfm,
                              attribute='translateX',
                              time=1, value=5.5,
                              inTangentType='linear',
                              outTangentType='linear')
        maya.cmds.setKeyframe(bundle_tfm,
                              attribute='translateY',
                              time=1, value=6.4,
                              inTangentType='linear',
                              outTangentType='linear')
        maya.cmds.setKeyframe(bundle_tfm,
                              attribute='translateZ',
                              time=1, value=-25.0,
                              inTangentType='linear',
                              outTangentType='linear')

        # Marker
        mkr = mmapi.Marker().create_node(cam=cam, bnd=bnd)
        marker_tfm = mkr.get_node()
        assert mmapi.get_object_type(marker_tfm) == 'marker'
        # maya.cmds.setAttr(marker_tfm + '.tx', 0.0)
        # maya.cmds.setAttr(marker_tfm + '.ty', 0.0)
        maya.cmds.setKeyframe(marker_tfm,
                              attribute='translateX',
                              time=1, value=-0.5,
                              inTangentType='linear',
                              outTangentType='linear')
        maya.cmds.setKeyframe(marker_tfm,
                              attribute='translateX',
                              time=5, value=0.5,
                              inTangentType='linear',
                              outTangentType='linear')
        maya.cmds.setKeyframe(marker_tfm,
                              attribute='translateY',
                              time=1, value=-0.5,
                              inTangentType='linear',
                              outTangentType='linear')
        maya.cmds.setKeyframe(marker_tfm,
                              attribute='translateY',
                              time=5, value=0.5,
                              inTangentType='linear',
                              outTangentType='linear')

        # Attributes
        attr_tx = mmapi.Attribute(bundle_tfm + '.tx')
        attr_ty = mmapi.Attribute(bundle_tfm + '.ty')

        # Frames
        frm_list = [
            mmapi.Frame(1),
            mmapi.Frame(2),
            mmapi.Frame(3),
            mmapi.Frame(4),
            mmapi.Frame(5),
        ]

        # Solver
        sol_list = []
        for frm in frm_list:
            sol = mmapi.Solver()
            sol.set_max_iterations(10)
            sol.set_verbose(True)
            sol.set_frame_list([frm])
            sol_list.append(sol)

        # Collection
        col = mmapi.Collection()
        col.create_node('mySolveCollection')
        col.add_solver_list(sol_list)
        col.add_marker(mkr)
        col.add_attribute(attr_tx)
        col.add_attribute(attr_ty)

        # save the output
        path = self.get_data_path('test_solve_per_frame_before.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Run solver!
        results = mmapi.execute(col)

        # Set Deviation
        mmapi.update_deviation_on_markers([mkr], results)
        mmapi.update_deviation_on_collection(col, results)

        # save the output
        path = self.get_data_path('test_solve_per_frame_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.checkSolveResults(results)
        return

    def test_stA_refine_good_solve(self):
        """
        Test file based on 3DEqualizer 'stA' image sequence.

        The Maya file loaded contains a good 3DEqualizer solve.  This
        test tests the solver to ensure it produces good results,
        given an already good solution.

        The 'stA' image sequence has a frame range of 0 to 94.
        """
        start_frame = 0
        end_frame = 94

        path = self.get_data_path('scenes', 'stA_v001.ma')
        ok = maya.cmds.file(path, open=True, ignoreVersion=True, force=True)
        assert isinstance(ok, pycompat.TEXT_TYPE)

        # Camera
        cam_name = 'stA_1_1Shape1'
        cam = mmapi.Camera(shape=cam_name)
        cam_tfm_node = cam.get_transform_node()
        cam_shp_node = cam.get_shape_node()

        # Marker Group
        mkr_grp_name = 'markerGroup1'
        mkr_grp = mmapi.MarkerGroup(node=mkr_grp_name)
        mkr_grp_node = mkr_grp.get_node()

        # Markers
        mkr_list = []
        bnd_list = []
        mkr_nodes = maya.cmds.listRelatives(
            mkr_grp_node,
            children=True,
            shapes=False) or []
        for node in mkr_nodes:
            if node.endswith('_MKR') is False:
                continue
            assert mmapi.get_object_type(node) == 'marker'
            mkr = mmapi.Marker(node=node)
            bnd = mkr.get_bundle()
            mkr_list.append(mkr)
            bnd_list.append(bnd)
        assert len(mkr_list) > 0
        assert len(bnd_list) > 0

        # Attributes
        attr_list = []
        for bnd in bnd_list:
            bnd_node = bnd.get_node()
            attr_tx = mmapi.Attribute(node=bnd_node, attr='tx')
            attr_ty = mmapi.Attribute(node=bnd_node, attr='ty')
            attr_tz = mmapi.Attribute(node=bnd_node, attr='tz')
            attr_list.append(attr_tx)
            attr_list.append(attr_ty)
            attr_list.append(attr_tz)
        attr_tx = mmapi.Attribute(node=cam_tfm_node, attr='tx')
        attr_ty = mmapi.Attribute(node=cam_tfm_node, attr='ty')
        attr_tz = mmapi.Attribute(node=cam_tfm_node, attr='tz')
        attr_rx = mmapi.Attribute(node=cam_tfm_node, attr='rx')
        attr_ry = mmapi.Attribute(node=cam_tfm_node, attr='ry')
        attr_rz = mmapi.Attribute(node=cam_tfm_node, attr='rz')
        attr_fl = mmapi.Attribute(node=cam_shp_node, attr='focalLength')
        attr_list.append(attr_tx)
        attr_list.append(attr_ty)
        attr_list.append(attr_tz)
        attr_list.append(attr_rx)
        attr_list.append(attr_ry)
        attr_list.append(attr_rz)
        attr_list.append(attr_fl)

        # Frames
        #
        # Root Frames are automatically calculated from the markers.
        root_frm_list = []
        not_root_frm_list = []
        min_frames_per_marker = 2
        frame_nums = mmapi.get_root_frames_from_markers(
            mkr_list, min_frames_per_marker, start_frame, end_frame)
        for f in frame_nums:
            frm = mmapi.Frame(f)
            root_frm_list.append(frm)
        for f in range(start_frame, end_frame + 1):
            frm = mmapi.Frame(f)
            not_root_frm_list.append(frm)

        # Solvers
        sol_list = []
        sol = mmapi.SolverStandard()
        sol.set_root_frame_list(root_frm_list)
        sol.set_frame_list(not_root_frm_list)
        sol.set_only_root_frames(False)
        sol.set_global_solve(False)
        sol.set_use_single_frame(False)
        sol_list.append(sol)

        # Collection
        col = mmapi.Collection()
        col.create_node('mySolveCollection')
        col.set_solver_list(sol_list)
        col.add_marker_list(mkr_list)
        col.add_attribute_list(attr_list)

        # save the output
        path = self.get_data_path('test_solve_stA_refine_before.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Run solver!
        LOG.warning('Running Solver Test... (it may take some time to finish).')
        results = mmapi.execute(col)

        # Set Deviation
        mmapi.update_deviation_on_markers(mkr_list, results)
        mmapi.update_deviation_on_collection(col, results)

        # save the output
        path = self.get_data_path('test_solve_stA_refine_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.checkSolveResults(results)
        return

    def test_badPerFrameSolve(self):
        """
        This file solves wildly, with each frame good, then next bad. The
        animCurves created are very spikey, but we expect to solve a
        smooth curve.

        When opening the scene file manually using the GUI, and
        running the solver, the undo-ing the (bad) result, the
        timeline is traversed slowly. This shows issue #45.
        """
        s = time.time()

        # Open the Maya file
        file_name = 'mmSolverBasicSolveA_badSolve01.ma'
        path = self.get_data_path('scenes', file_name)
        maya.cmds.file(path, open=True, force=True, ignoreVersion=True)

        col = mmapi.Collection(node='collection1')
        lib_col.compile_collection(col)
        e = time.time()
        print('pre-solve time:', e - s)

        # Run solver!
        s = time.time()
        solres_list = mmapi.execute(col)
        e = time.time()
        print('total time:', e - s)

        # Set Deviation
        mkr_list = col.get_marker_list()
        mmapi.update_deviation_on_markers(mkr_list, solres_list)
        mmapi.update_deviation_on_collection(col, solres_list)

        # save the output
        path = self.get_data_path('test_solve_badPerFrameSolve_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.checkSolveResults(solres_list)
        return

    def test_badPerFrameSolve_solverstandard(self):
        """
        The same test as 'test_badPerFrameSolve', but using the SolverStandard class.
        """
        s = time.time()
        # Open the Maya file
        file_name = 'mmSolverBasicSolveA_badSolve01.ma'
        path = self.get_data_path('scenes', file_name)
        maya.cmds.file(path, open=True, force=True, ignoreVersion=True)
        print('File opened:', path)

        # Frames
        start_frame = 1
        end_frame = 120
        root_frames = [1, 30, 60, 90, 120]
        root_frm_list = []
        for f in root_frames:
            frm = mmapi.Frame(f)
            root_frm_list.append(frm)
        print('root frames:', root_frm_list)

        frm_list = []
        for f in range(start_frame, end_frame):
            frm = mmapi.Frame(f)
            frm_list.append(frm)
        print('frames:', frm_list)

        # Solver
        sol = mmapi.SolverStandard()
        sol.set_root_frame_list(root_frm_list)
        sol.set_frame_list(frm_list)
        sol.set_use_single_frame(False)
        sol.set_global_solve(False)
        sol.set_only_root_frames(False)
        sol_list = [sol]
        print('Solver:', sol)
        e = time.time()
        print('pre-solve time:', e - s)

        # Run solver!
        s = time.time()
        col = mmapi.Collection(node='collection1')
        col.set_solver_list(sol_list)
        solres_list = mmapi.execute(col)
        e = time.time()
        print('total time:', e - s)

        # Set Deviation
        mkr_list = col.get_marker_list()
        mmapi.update_deviation_on_markers(mkr_list, solres_list)
        mmapi.update_deviation_on_collection(col, solres_list)

        # save the output
        path = self.get_data_path('test_solve_badPerFrameSolve_solverstandard_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.checkSolveResults(solres_list)
        return

    def test_allFrameStrategySolve(self):
        """
        Solving only a 'all frames' solver step across multiple frames.
        """
        # Open the Maya file
        file_name = 'mmSolverBasicSolveA_badSolve02.ma'
        path = self.get_data_path('scenes', file_name)
        maya.cmds.file(path, open=True, force=True, ignoreVersion=True)

        # Collection
        col = mmapi.Collection(node='collection1')
        mkr_list = col.get_marker_list()

        # Frames
        #
        # Root Frames are automatically calculated from the markers.
        root_frm_list = []
        not_root_frm_list = []
        start_frame, end_frame = time_utils.get_maya_timeline_range_inner()
        min_frames_per_marker = 3
        frame_nums = mmapi.get_root_frames_from_markers(
            mkr_list, min_frames_per_marker, start_frame, end_frame)
        for f in frame_nums:
            frm = mmapi.Frame(f)
            root_frm_list.append(frm)
        for f in range(0, 41):
            frm = mmapi.Frame(f)
            not_root_frm_list.append(frm)

        # Define Solver
        sol_list = []
        sol = mmapi.SolverStandard()
        sol.set_root_frame_list(root_frm_list)
        sol.set_frame_list(not_root_frm_list)
        sol.set_only_root_frames(False)
        sol.set_global_solve(False)
        sol.set_single_frame(False)
        sol.set_root_frame_strategy(mmapi.ROOT_FRAME_STRATEGY_GLOBAL_VALUE)
        sol_list.append(sol)
        col.set_solver_list(sol_list)

        # Run solver!
        s = time.time()
        lib_col.compile_collection(col)
        solres_list = mmapi.execute(col)
        e = time.time()
        print('total time:', e - s)

        # Set Deviation
        mkr_list = col.get_marker_list()
        mmapi.update_deviation_on_markers(mkr_list, solres_list)
        mmapi.update_deviation_on_collection(col, solres_list)

        # save the output
        path = self.get_data_path('test_solve_allFrameStrategySolve_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.checkSolveResults(solres_list)
        return

    # @unittest.skip
    def test_solveAllFramesCausesStaticAnimCurves(self):
        """
        Solving with the scene file 'mmSolverBasicSolveB_before.ma', was
        reported to solve as static values, the same as the initial
        values. The DG did not evaluate some how and the solve was
        therefore useless.

        GitHub Issue #53.
        """
        s = time.time()
        # Open the Maya file
        file_name = 'mmSolverBasicSolveB_before.ma'
        path = self.get_data_path('scenes', file_name)
        maya.cmds.file(path, open=True, force=True, ignoreVersion=True)

        # NOTE: We leave these nodes alone, since these are already in
        # the 'correct' position, we are treating these as surveyed.
        # When we have less than 3 points as survey the solve goes
        # crazy.
        dont_touch_these_nodes = [
            '|bundle_12_BND',
            '|bundle_13_BND',
            '|bundle_14_BND']

        # Triangulate all 3D points.
        nodes = maya.cmds.ls(type='transform') or []
        bnd_nodes = mmapi.filter_bundle_nodes(nodes)
        bnd_list = [mmapi.Bundle(node=n) for n in bnd_nodes]
        for bnd in bnd_list:
            bnd_node = bnd.get_node()
            if bnd_node in dont_touch_these_nodes:
                continue
            attrs = ['translateX', 'translateY', 'translateZ']
            for attr_name in attrs:
                plug = bnd_node + '.' + attr_name
                maya.cmds.setAttr(plug, lock=False)
                maya.cmds.setAttr(plug, 0.0)

        # Get Bundle attributes to compute.
        bnd_attr_list = []
        for bnd in bnd_list:
            node = bnd.get_node()
            attrs = ['translateX', 'translateY', 'translateZ']
            for attr_name in attrs:
                attr = mmapi.Attribute(node=node, attr=attr_name)
                bnd_attr_list.append(attr)

        # Camera attributes
        cam_tfm = 'stA_1_1'
        cam = mmapi.Camera(cam_tfm)
        cam_shp = cam.get_shape_node()
        cam_attr_list = []
        attrs = ['translateX', 'translateY', 'translateZ',
                 'rotateX', 'rotateY', 'rotateZ']
        for attr_name in attrs:
            attr = mmapi.Attribute(node=cam_tfm, attr=attr_name)
            cam_attr_list.append(attr)
        attr = mmapi.Attribute(node=cam_shp, attr='focalLength')
        cam_attr_list.append(attr)

        # Get Markers
        col = mmapi.Collection(node='collection1')
        mkr_list = col.get_marker_list()

        # Frames
        #
        # Root Frames are automatically calculated from the markers.
        root_frm_list = []
        not_root_frm_list = []
        start_frame = 0
        end_frame = 94
        min_frames_per_marker = 2
        f_list = mmapi.get_root_frames_from_markers(
            mkr_list, min_frames_per_marker, start_frame, end_frame)
        for f in f_list:
            frm = mmapi.Frame(f)
            root_frm_list.append(frm)
        for f in range(start_frame, end_frame + 1):
            frm = mmapi.Frame(f)
            not_root_frm_list.append(frm)

        # Run solver!
        sol_list = []
        sol = mmapi.SolverStandard()
        sol.set_root_frame_list(root_frm_list)
        sol.set_frame_list(not_root_frm_list)
        sol.set_only_root_frames(False)
        sol.set_global_solve(False)
        sol.set_single_frame(False)
        sol_list.append(sol)

        attr_list = cam_attr_list + bnd_attr_list
        col.set_attribute_list(attr_list)
        col.set_solver_list(sol_list)
        e = time.time()
        print('pre=solve time:', e - s)

        # save the output, before.
        name = 'test_solve_solveAllFramesCausesStaticAnimCurves_before.ma'
        path = self.get_data_path(name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        s = time.time()
        solres_list = mmapi.execute(col)
        e = time.time()
        print('total time:', e - s)

        # Set Deviation
        mkr_list = col.get_marker_list()
        mmapi.update_deviation_on_markers(mkr_list, solres_list)
        mmapi.update_deviation_on_collection(col, solres_list)

        # save the output
        name = 'test_solve_solveAllFramesCausesStaticAnimCurves_after.ma'
        path = self.get_data_path(name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.checkSolveResults(solres_list)
        return

    def do_solve_opera_house(self, solver_name, solver_type_index, scene_graph_mode):
        """
        Load pre-tracked Markers for the 'opera house' image sequence,
        then solve it.

        http://danielwedge.com/fmatrix/operahouse.html
        """
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)
        scene_graph_name = mmapi.SCENE_GRAPH_MODE_NAME_LIST[scene_graph_mode]
        scene_graph_label = mmapi.SCENE_GRAPH_MODE_LABEL_LIST[scene_graph_mode]
        print('Scene Graph:', scene_graph_label)

        # Time Range
        start = 0
        end = 41
        maya.cmds.playbackOptions(
            animationStartTime=start, minTime=start,
            animationEndTime=end, maxTime=end)

        # Camera
        cam_tfm = maya.cmds.createNode('transform',
                                       name='cam_tfm')
        cam_shp = maya.cmds.createNode('camera',
                                       name='cam_shp',
                                       parent=cam_tfm)
        maya.cmds.setAttr(cam_tfm + '.rotateOrder', 2)  # zxy
        maya.cmds.setAttr(cam_shp + '.focalLength', 14)
        maya.cmds.setAttr(cam_shp + '.horizontalFilmAperture', 5.4187 / 25.4)
        maya.cmds.setAttr(cam_shp + '.verticalFilmAperture', 4.0640 / 25.4)
        cam = mmapi.Camera(shape=cam_shp)

        # Set Camera Keyframes
        cam_data = {
            '0': (-0.19889791581420663, 0.5591321634949238, 7.258789219735233, -1.9999507874015703, -0.3999999999999992, 0.0),
            '22': (-4.840404384215566, 0.7543627646977502, 6.3465857678271425, -3.0709513272069815, -36.91024116734281, 0.0),
            '41': (-8.584368967987194, 0.6990718939718145, 5.508167213044364, -1.4738793091011815, -54.30997787050599, 0.0)
        }
        for key in sorted(cam_data.keys()):
            frame = int(key)
            for i, attr in enumerate(['tx', 'ty', 'tz', 'rx', 'ry', 'rz']):
                value = cam_data[key][i]
                maya.cmds.setKeyframe(cam_tfm, attribute=attr, time=frame, value=value)
        maya.cmds.setKeyframe(cam_shp, attribute='focalLength', time=start, value=14.0)
        maya.cmds.setKeyframe(cam_shp, attribute='focalLength', time=end, value=14.0)

        # Create image plane
        path = self.get_data_path('operahouse', 'frame00.jpg')
        imgpl = maya.cmds.imagePlane(
            camera=cam_shp,
            fileName=path
        )
        maya.cmds.setAttr(imgpl[1] + '.useFrameExtension', 1)
        maya.cmds.setAttr(imgpl[1] + '.depth', 2000)
        maya.cmds.setAttr(imgpl[1] + '.frameCache', 0)
        maya.cmds.setAttr(imgpl[1] + '.coverageX', 3072)
        maya.cmds.setAttr(imgpl[1] + '.coverageY', 2304)

        # Create Horizon Line
        cir = maya.cmds.circle(name='horizon', nrx=0, nry=1, nrz=0)
        maya.cmds.setAttr(cir[1] + ".radius", 3000)

        # Create Cube for Opera House
        cube = maya.cmds.polyCube()
        maya.cmds.setAttr(cube[0] + ".ty", 0.5)
        maya.cmds.setAttr(cube[0] + ".sx", 2.68)
        maya.cmds.setAttr(cube[0] + ".sy", 0.91625416)
        maya.cmds.setAttr(cube[0] + ".sz", 1.68658365)

        # Marker Group
        mkr_grp = mmapi.MarkerGroup().create_node(cam=cam)
        mkr_grp_node = mkr_grp.get_node()

        # Bundle Group
        bnd_grp = maya.cmds.createNode('transform', name='bundleGroup')
        bnd_fg_grp = maya.cmds.createNode(
            'transform',
            name='bundles_fg',
            parent=bnd_grp)
        bnd_bg_grp = maya.cmds.createNode(
            'transform',
            name='bundles_bg',
            parent=bnd_grp)

        # Load Markers
        fg_points = [
            'Track_01',
            'Track_02',
            'Track_05',
            'Track_06',
            'Track_08',
            'Track_09',
            'Track_10',
            'Track_11',
            'Track_19',
            'Track_20',
            'Track_21',
            'Track_22',
            'Track_23',
            'Track_23',
            'Track_24',
            'Track_25',
            'Track_26',
            'Track_27',
        ]
        bg_points = [
            'Track_03',
            'Track_04',
            'Track_07',
            'Track_12',
            'Track_13',
            'Track_14',
            'Track_15',
            'Track_16',
            'Track_17',
            'Track_18',
            'Track_28',
            'Track_29',
            'Track_30',
            'Track_31',
        ]
        bnd_positions = {
            'Track_23': (-0.7669678476654883, 0.704741253611808, 0.11480582185051777),
            'Track_14': (-6.096859889443822, 2.0552736121532478, -64.25806442305448),
            'Track_12': (45.11056705173852, 2.602519222901666, -43.16772737415769),
            'Track_13': (-11.331222134074189, -0.9161249928992397, -63.60343691220178),
            'Track_28': (12.97847320083373, 0.4908757961951475, -6.558878377403925),
            'Track_24': (-0.9577362080844809, 0.11947272894636578, -0.29860515939718035),
            'Track_25': (-0.3816240705349317, 0.09511793539283707, 0.5968218516602972),
            'Track_05': (-0.5497538933513093, 0.9121450956455763, 0.0689419211208016),
            'Track_06': (0.6442115545215732, 0.09146863102772763, 0.2698159600733472),
            'Track_02': (-1.1928085448379213, 0.06849164070024401, 0.741609523996595),
            'Track_17': (4.101733117764308, 0.4416977194116366, -20.775735845844235),
            'Track_16': (10.499779696104385, 2.4959245952203037, -61.65315035391216),
            'Track_21': (0.4422885021421483, 0.15594114410956195, -0.4586671394741284),
            'Track_18': (13.426726902476766, 2.208127581689255, -62.440721369338476),
            'Track_27': (-1.203371663768503, 0.07727436882970459, -0.34432924439358475),
            'Track_07': (24.82344439444535, 3.8981611004590917, -62.57148439047777),
            'Track_26': (-1.036542158437551, 0.1301250303434169, 0.6183349238312523),
            'Track_11': (-1.2868698932117608, 0.07508027422294668, -0.6923287330737453),
            'Track_09': (-1.1210978513200678, -0.0009538700668097195, -0.7481409812887209),
            'Track_20': (0.5370453995103619, 0.32144750391315535, 0.10037404391850258),
            'Track_08': (-0.35711469535141427, 0.8134673956410489, -0.8873816770491396),
            'Track_19': (-1.0708190128497155, 0.5849715587489718, 0.22909459498373133),
            'Track_10': (-0.8256010837265352, 0.04548785302325305, -0.6865934949556973),
            'Track_30': (12.219883964568602, 1.6676763053004873, -63.511794156133575),
            'Track_22': (-0.42435005852350927, 0.6386843510112235, -1.0271747982989685),
            'Track_31': (14.4768210901898, 1.5761955139450978, -40.10088917167338),
            'Track_15': (-0.17540615158899264, 2.5048877383268424, -64.10912011449136),
            'Track_29': (15.264518808431728, 1.8337698745022983, -62.076762425418536),
            'Track_03': (311.42375656555913, 16.402469194090923, -179.38329132993437),
            'Track_01': (-1.0890118590423876, 0.5109764471108498, -0.707187214616633),
            'Track_04': (209.73939576288353, 12.878819985707446, -150.30617721944793)
        }
        mkr_fg_grp = maya.cmds.createNode('transform',
                                          name='fg',
                                          parent=mkr_grp_node)
        mkr_bg_grp = maya.cmds.createNode('transform',
                                          name='bg',
                                          parent=mkr_grp_node)
        path = self.get_data_path('match_mover', 'loadmarker.rz2')
        _, mkr_data_list = marker_read.read(path)
        mkr_list = marker_read.create_nodes(
            mkr_data_list,
            cam=cam,
            mkr_grp=mkr_grp
        )
        mkr_fg_list = []
        mkr_bg_list = []
        for mkr in mkr_list:
            mkr_node = mkr.get_node()
            mgrp = mkr_grp_node
            bgrp = bnd_grp
            pos = None
            for name in fg_points:
                if name in mkr_node:
                    if name in bnd_positions:
                        pos = bnd_positions[name]
                    mgrp = mkr_fg_grp
                    bgrp = bnd_fg_grp
                    mkr_fg_list.append(mkr)
                    break
            for name in bg_points:
                if name in mkr_node:
                    if name in bnd_positions:
                        pos = bnd_positions[name]
                    mgrp = mkr_bg_grp
                    bgrp = bnd_bg_grp
                    mkr_bg_list.append(mkr)
                    break
            maya.cmds.parent(mkr_node, mgrp, relative=True)

            bnd = mkr.get_bundle()
            bnd_node = bnd.get_node()
            plug_tx = bnd_node + '.tx'
            plug_ty = bnd_node + '.ty'
            plug_tz = bnd_node + '.tz'
            maya.cmds.setAttr(plug_tx, pos[0])
            maya.cmds.setAttr(plug_ty, pos[1])
            maya.cmds.setAttr(plug_tz, pos[2])
            maya.cmds.parent(bnd_node, bgrp, relative=True)

            # bnd_node = bnd.get_node()
            # plug_tx = bnd_node + '.tx'
            # plug_ty = bnd_node + '.ty'
            # plug_tz = bnd_node + '.tz'
            # maya.cmds.setAttr(plug_tx, lock=True)
            # maya.cmds.setAttr(plug_ty, lock=True)
            # maya.cmds.setAttr(plug_tz, lock=True)

        # Frames
        #
        # Root Frames are automatically calculated from the markers.
        root_frm_list = []
        not_root_frm_list = []
        min_frames_per_marker = 2
        frame_nums = mmapi.get_root_frames_from_markers(
            mkr_list, min_frames_per_marker, start, end)
        print('frame_nums', frame_nums)
        for f in frame_nums:
            frm = mmapi.Frame(f)
            root_frm_list.append(frm)
        for f in range(start, end + 1):
            frm = mmapi.Frame(f)
            not_root_frm_list.append(frm)

        sol_list = []
        sol = mmapi.SolverStandard()
        sol.set_single_frame(False)
        sol.set_root_frame_list(root_frm_list)
        sol.set_frame_list(not_root_frm_list)
        sol.set_only_root_frames(False)
        sol.set_global_solve(False)
        sol.set_solver_type(solver_type_index)
        sol.set_scene_graph_mode(scene_graph_mode)
        sol._auto_attr_blocks = True
        sol._triangulate_bundles = False
        sol_list.append(sol)

        # Collection
        col = mmapi.Collection()
        col.create_node('mySolverCollection')
        col.add_solver_list(sol_list)

        # Add markers
        col.add_marker_list(mkr_fg_list)
        col.add_marker_list(mkr_bg_list)

        # Attributes
        attr_cam_tx = mmapi.Attribute(cam_tfm + '.tx')
        attr_cam_ty = mmapi.Attribute(cam_tfm + '.ty')
        attr_cam_tz = mmapi.Attribute(cam_tfm + '.tz')
        attr_cam_rx = mmapi.Attribute(cam_tfm + '.rx')
        attr_cam_ry = mmapi.Attribute(cam_tfm + '.ry')
        attr_cam_rz = mmapi.Attribute(cam_tfm + '.rz')
        attr_cam_focal = mmapi.Attribute(cam_shp + '.focalLength')
        col.add_attribute(attr_cam_tx)
        col.add_attribute(attr_cam_ty)
        col.add_attribute(attr_cam_tz)
        col.add_attribute(attr_cam_rx)
        col.add_attribute(attr_cam_ry)
        col.add_attribute(attr_cam_rz)

        mkr_list = col.get_marker_list()
        for mkr in mkr_list:
            bnd = mkr.get_bundle()
            bnd_node = bnd.get_node()
            attr_tx = mmapi.Attribute(bnd_node + '.tx')
            attr_ty = mmapi.Attribute(bnd_node + '.ty')
            attr_tz = mmapi.Attribute(bnd_node + '.tz')
            col.add_attribute(attr_tx)
            col.add_attribute(attr_ty)
            col.add_attribute(attr_tz)

        # save the output
        file_name = 'test_solve_opera_house_{}_{}_before.ma'.format(
            solver_name, scene_graph_name)
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Run solver!
        results = mmapi.execute(col)

        # Ensure the values are correct
        for res in results:
            success = res.get_success()
            err = res.get_final_error()
            print('err', err, 'success', success)

        # Set Deviation
        mmapi.update_deviation_on_markers(mkr_list, results)
        mmapi.update_deviation_on_collection(col, results)

        # save the output
        file_name = 'test_solve_opera_house_{}_{}_after.ma'.format(
            solver_name, scene_graph_name)
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.checkSolveResults(results)
        return

    def test_opera_house_ceres_maya_dag(self):
        self.do_solve_opera_house('ceres', mmapi.SOLVER_TYPE_CERES, mmapi.SCENE_GRAPH_MODE_MAYA_DAG)

    def test_opera_house_ceres_mmscenegraph(self):
        self.do_solve_opera_house('ceres', mmapi.SOLVER_TYPE_CERES, mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH)

    def test_opera_house_cminpack_lmdif_maya_dag(self):
        self.do_solve_opera_house('cminpack_lmdif', mmapi.SOLVER_TYPE_CMINPACK_LMDIF, mmapi.SCENE_GRAPH_MODE_MAYA_DAG)

    def test_opera_house_cminpack_lmdif_mmscenegraph(self):
        self.do_solve_opera_house('cminpack_lmdif', mmapi.SOLVER_TYPE_CMINPACK_LMDIF, mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH)

    def test_opera_house_cminpack_lmder_maya_dag(self):
        self.do_solve_opera_house('cminpack_lmder', mmapi.SOLVER_TYPE_CMINPACK_LMDER, mmapi.SCENE_GRAPH_MODE_MAYA_DAG)

    def test_opera_house_cminpack_lmder_mmscenegraph(self):
        self.do_solve_opera_house('cminpack_lmder', mmapi.SOLVER_TYPE_CMINPACK_LMDER, mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH)


if __name__ == '__main__':
    prog = unittest.main()
