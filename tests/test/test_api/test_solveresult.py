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
Test functions for API utils module.
"""

import pprint
import unittest
import time

import maya.cmds

import test.test_api.apiutils as test_api_utils
import mmSolver._api.solveresult as solveresult  # used indirectly.
import mmSolver.api as mmapi


def create_example_solve_scene():
    """
    Very basic single frame solver set up.

    This function does not execute the solve, execution must be done manually.

    :return: API Collection object.
    """
    # Camera
    cam_tfm = maya.cmds.createNode('transform',
                                   name='cam_tfm')
    cam_shp = maya.cmds.createNode('camera',
                                   name='cam_shp',
                                   parent=cam_tfm)
    maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
    maya.cmds.setAttr(cam_tfm + '.ty',  1.0)
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
    sol.set_verbose(True)
    sol.set_frame_list(frm_list)

    # Collection
    col = mmapi.Collection()
    col.create_node('mySolveCollection')
    col.add_solver(sol)
    col.add_marker(mkr)
    col.add_attribute(attr_tx)
    col.add_attribute(attr_ty)
    return col


# @unittest.skip
class TestSolveResult(test_api_utils.APITestCase):
    def test_init(self):
        col = create_example_solve_scene()
        results = col.execute()
        success = results[0].get_success()
        err = results[0].get_final_error()
        self.assertTrue(isinstance(success, bool))
        self.assertTrue(isinstance(err, float))

        print('error stats: ' + pprint.pformat(results[0].get_error_stats()))
        print('timer stats: ' + pprint.pformat(results[0].get_timer_stats()))
        print('solver stats: ' + pprint.pformat(results[0].get_solver_stats()))
        print('frame error list: ' + pprint.pformat(dict(results[0].get_frame_error_list())))
        print('marker error list: ' + pprint.pformat(dict(results[0].get_marker_error_list())))

    def test_combine_timer_stats(self):
        col = create_example_solve_scene()
        results = col.execute()
        success = results[0].get_success()
        err = results[0].get_final_error()
        self.assertTrue(isinstance(success, bool))
        self.assertTrue(isinstance(err, float))

        timer_stats = mmapi.combine_timer_stats(results)
        assert isinstance(timer_stats, dict)
        for k, v in timer_stats.items():
            assert v >= 0

    def test_merge_frame_error_list(self):
        col = create_example_solve_scene()
        results = col.execute()
        success = results[0].get_success()
        err = results[0].get_final_error()
        self.assertTrue(isinstance(success, bool))
        self.assertTrue(isinstance(err, float))

        frame_error_list = mmapi.merge_frame_error_list(results)
        assert isinstance(frame_error_list, dict)

    def test_merge_frame_list(self):
        col = create_example_solve_scene()
        results = col.execute()
        success = results[0].get_success()
        err = results[0].get_final_error()
        self.assertTrue(isinstance(success, bool))
        self.assertTrue(isinstance(err, float))

        frame_list = mmapi.merge_frame_list(results)
        assert isinstance(frame_list, list)
        assert len(frame_list) > 0

    def test_get_average_frame_error_list(self):
        frame_error_list = {
            1: 0,
            2: 0.5,
            3: 1.0
        }
        v = mmapi.get_average_frame_error_list(frame_error_list)
        assert self.approx_equal(v, 0.5)

        frame_error_list = {1: 1.0}
        v = mmapi.get_average_frame_error_list(frame_error_list)
        assert self.approx_equal(v, 1.0)

        frame_error_list = {}
        v = mmapi.get_average_frame_error_list(frame_error_list)
        assert self.approx_equal(v, 0.0)

        col = create_example_solve_scene()
        results = col.execute()
        success = results[0].get_success()
        err = results[0].get_final_error()
        self.assertTrue(isinstance(success, bool))
        self.assertTrue(isinstance(err, float))

        frame_error_list = dict(results[0].get_frame_error_list())

        v = mmapi.get_average_frame_error_list(frame_error_list)
        assert isinstance(v, float)

    def test_get_max_frame_error(self):
        frame_error_list = {
            1: 0,
            2: 0.5,
            3: 1.0
        }
        frm, val = mmapi.get_max_frame_error(frame_error_list)
        assert self.approx_equal(frm, 3) and isinstance(frm, int)
        assert self.approx_equal(val, 1.0)

        frame_error_list = {1: 1.0}
        frm, val = mmapi.get_max_frame_error(frame_error_list)
        assert self.approx_equal(frm, 1) and isinstance(frm, int)
        assert self.approx_equal(val, 1.0)

        frame_error_list = {}
        frm, val = mmapi.get_max_frame_error(frame_error_list)
        assert frm is None
        assert self.approx_equal(val, -0.0)

        col = create_example_solve_scene()
        results = col.execute()
        success = results[0].get_success()
        err = results[0].get_final_error()
        self.assertTrue(isinstance(success, bool))
        self.assertTrue(isinstance(err, float))

        frame_error_list = dict(results[0].get_frame_error_list())
        frm, val = mmapi.get_max_frame_error(frame_error_list)
        assert frm is None or isinstance(frm, float) or isinstance(frm, int)
        assert isinstance(val, float)

    def test_merge_marker_error_list(self):
        col = create_example_solve_scene()
        results = col.execute()
        success = results[0].get_success()
        err = results[0].get_final_error()
        self.assertTrue(isinstance(success, bool))
        self.assertTrue(isinstance(err, float))

        marker_error_list = mmapi.merge_marker_error_list(results)
        assert isinstance(marker_error_list, dict)
        assert len(marker_error_list) > 0

    def test_merge_marker_node_list(self):
        col = create_example_solve_scene()
        results = col.execute()
        success = results[0].get_success()
        err = results[0].get_final_error()
        self.assertTrue(isinstance(success, bool))
        self.assertTrue(isinstance(err, float))

        nodes = mmapi.merge_marker_node_list(results)
        assert isinstance(nodes, list)
        assert len(nodes) > 0

    def test_perfect_solve(self):
        """
        Open a file and trigger a solve to get perfect results.
        Make sure solver results doesn't fail in this case.
        """
        # Open the Maya file
        file_name = 'mmSolverBasicSolveA_triggerMaxFrameErrorTraceback.ma'
        path = self.get_data_path('scenes', file_name)
        maya.cmds.file(path, open=True, force=True)

        # Run solver!
        s = time.time()
        col = mmapi.Collection(node='collection1')
        solres_list = mmapi.execute(col)
        e = time.time()
        print 'total time:', e - s

        # save the output
        path = self.get_data_path('solveresult_testPerfectSolve_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        solres = solres_list[0]
        success = solres.get_success()
        err = solres.get_final_error()
        frame_list = mmapi.merge_frame_list([solres])
        frame_error_list = mmapi.merge_frame_error_list([solres])
        avg_error = mmapi.get_average_frame_error_list(frame_error_list)
        max_frame_error = mmapi.get_max_frame_error(frame_error_list)
        # self.assertEqual(max_frame_error[0], 120)
        self.assertIsInstance(max_frame_error[0], int)
        self.assertIsInstance(max_frame_error[1], float)
        self.assertTrue(success)
        self.assertLess(avg_error, 1.0)
        self.assertGreater(err, 0.0)
        return


if __name__ == '__main__':
    prog = unittest.main()
