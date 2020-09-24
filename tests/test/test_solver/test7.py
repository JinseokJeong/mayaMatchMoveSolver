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
Test 'one-frame lineup' camera solving on a single frame.
"""

import time
import unittest

try:
    import maya.standalone
    maya.standalone.initialize()
except RuntimeError:
    pass
import maya.cmds


import test.test_solver.solverutils as solverUtils


# @unittest.skip
class TestSolver7(solverUtils.SolverTestCase):

    def do_solve(self, solver_name, solver_index):
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)

        # Open File Path
        scenePath = self.get_data_path('solver_test7.ma')
        maya.cmds.file(scenePath,
                       open=True,
                       force=True,
                       typ='mayaAscii',
                       ignoreVersion=True,
                       options='v=0')

        # Get cameras
        cameras = []
        nodes = maya.cmds.ls('|cam_tfm*',
                             type='transform',
                             long=True)
        for node in nodes:
            print "camera node:", node
            camTfm = node
            camShape = maya.cmds.listRelatives(node,
                                               children=True,
                                               type='camera',
                                               fullPath=True)[0]
            print 'nodes', (camTfm, camShape)
            cameras.append((camTfm, camShape))

        # Get Markers
        markers = []
        nodes = maya.cmds.ls('|cam_tfm*|marker_tfm*',
                             type='transform', long=True)
        for node in nodes:
            markerTfm = node
            maya.cmds.addAttr(markerTfm, longName='enable', at='byte',
                              minValue=0, maxValue=1, defaultValue=True)
            maya.cmds.addAttr(markerTfm, longName='weight', at='double',
                              minValue=0.0, defaultValue=1.0)
            camTfm = maya.cmds.listRelatives(node,
                                             parent=True,
                                             type='transform',
                                             fullPath=True)[0]
            camShape = maya.cmds.listRelatives(camTfm, children=True,
                                               type='camera',
                                               fullPath=True)[0]
            bundleName = markerTfm.rpartition('|')[-1]
            bundleName = bundleName.replace('marker', 'bundle')
            bundleTfm = maya.cmds.ls(bundleName, type='transform')[0]
            markers.append((markerTfm, camShape, bundleTfm))

        # Get Attrs
        node_attrs = [
            (cameras[0][0] + '.tx', 'None', 'None', 'None', 'None'),
            (cameras[0][0] + '.ty', 'None', 'None', 'None', 'None'),
            (cameras[0][0] + '.tz', 'None', 'None', 'None', 'None'),
            (cameras[0][0] + '.rx', 'None', 'None', 'None', 'None'),
            (cameras[0][0] + '.ry', 'None', 'None', 'None', 'None'),
            (cameras[0][0] + '.rz', 'None', 'None', 'None', 'None'),
            # (cameras[0][1] + '.focalLength', '10.0', '100.0', 'None', 'None'),
        ]
        frames = [1]

        kwargs = {
            'camera': cameras,
            'marker': markers,
            'attr': node_attrs,
        }

        affects_mode = 'addAttrsToMarkers'
        self.runSolverAffects(affects_mode, **kwargs)

        affects_mode = 'addAttrsToMarkers'
        self.runSolverAffects(affects_mode, **kwargs)

        # Run solver!
        s = time.time()
        result = maya.cmds.mmSolver(
            frame=frames,
            iterations=1000,
            solverType=solver_index,
            verbose=True,
            **kwargs
        )
        e = time.time()
        print 'total time:', e - s

        # save the output
        path = self.get_data_path('solver_test7_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)
        
        # Ensure the values are correct
        self.assertEqual(result[0], 'success=1')

    def test_init_levmar(self):
        self.do_solve('levmar', 0)

    def test_init_cminpack_lmdif(self):
        self.do_solve('cminpack_lmdif', 1)

    def test_init_cminpack_lmder(self):
        self.do_solve('cminpack_lmder', 2)


if __name__ == '__main__':
    prog = unittest.main()
