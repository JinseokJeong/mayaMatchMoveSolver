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
Constant values for utilities.
"""

# Constants for smooth method selection.
SMOOTH_TYPE_AVERAGE = 'average'
SMOOTH_TYPE_GAUSSIAN = 'gaussian'
SMOOTH_TYPE_FOURIER = 'fourier'
SMOOTH_TYPES = [
    SMOOTH_TYPE_AVERAGE,
    SMOOTH_TYPE_GAUSSIAN,
    SMOOTH_TYPE_FOURIER,
]

# Raytrace
RAYTRACE_MAX_DIST = 9999999999.0
RAYTRACE_EPSILON = 0.0001

# Config
CONFIG_PATH_VAR_NAME = 'MMSOLVER_CONFIG_PATH'

# Maya configuration
SCENE_DATA_NODE = 'MM_SOLVER_SCENE_DATA'
SCENE_DATA_ATTR = 'data'
