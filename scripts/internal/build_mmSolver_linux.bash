#!/usr/bin/env bash
#
# Copyright (C) 2019, 2022 David Cattermole.
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
# ---------------------------------------------------------------------
#
# Builds the Maya MatchMove Solver project.
#
# This script is assumed to be called with a number of variables
# already set:
#
# - MAYA_VERSION
# - MAYA_LOCATION
# - PYTHON_EXE
# - CMAKE_EXE

# The -e flag causes the script to exit as soon as one command returns
# a non-zero exit code.
set -ev

# Store the current working directory, to return to.
CWD=`pwd`

# Clear all build information before re-compiling.
# Turn this off when wanting to make small changes and recompile.
FRESH_BUILD=1

# Run the Python API and Solver tests inside Maya, after a
# successfully build an install process.
RUN_TESTS=0

# Where to install the module?
#
# The "$HOME/maya/2018/modules" directory is automatically searched
# for Maya module (.mod) files. Therefore we can install directly.
#
INSTALL_MODULE_DIR="${HOME}/maya/${MAYA_VERSION}/modules"

# Build ZIP Package.
# For developer use. Make ZIP packages ready to distribute to others.
BUILD_PACKAGE=1

# What type of build? "Release" or "Debug"?
BUILD_TYPE=Release

# Build options, to allow faster compilation times. (not to be used by
# users wanting to build this project.)
BUILD_PLUGIN=1
BUILD_PYTHON=1
BUILD_MEL=1
BUILD_3DEQUALIZER=1
BUILD_SYNTHEYES=1
BUILD_BLENDER=1
BUILD_QT_UI=1
BUILD_DOCS=1
BUILD_ICONS=1
BUILD_CONFIG=1
BUILD_TESTS=0

# Path to this script.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
# The root of this project.
PROJECT_ROOT=`readlink -f ${DIR}/../..`
echo "Project Root: ${PROJECT_ROOT}"

# Set up Python environment.
PYTHON_VIRTUAL_ENV_DIR_NAME="python_venv_linux_maya${MAYA_VERSION}"
source "${PROJECT_ROOT}/scripts/internal/python_venv_activate.bash"

# Paths for dependencies.
#
# By default these paths will work if the "build_thirdparty.bat"
# scripts have been run before this script.
CMINPACK_ROOT="${PROJECT_ROOT}/external/install/maya${MAYA_VERSION}_linux/cminpack"
CXSPARSE_ROOT="${PROJECT_ROOT}/external/install/maya${MAYA_VERSION}_linux/cxsparse"
CERES_ROOT="${PROJECT_ROOT}/external/install/maya${MAYA_VERSION}_linux/ceres"
CERES_DIR="${CERES_ROOT}/lib64/cmake/Ceres/"
CERES_INCLUDE_DIR="${CERES_ROOT}/include"
CERES_LIB_PATH="${CERES_ROOT}/lib64"
LIBMV_ROOT="${PROJECT_ROOT}/external/install/maya${MAYA_VERSION}_linux/libmv"
EIGEN3_INCLUDE_DIR="${PROJECT_ROOT}/external/install/maya${MAYA_VERSION}_linux/eigen/include/eigen3"
GLOG_ROOT="${PROJECT_ROOT}/external/install/maya${MAYA_VERSION}_linux/glog"
GLOG_INCLUDE_DIR="${PROJECT_ROOT}/external/install/maya${MAYA_VERSION}_linux/glog/include"
GLOG_LIB_PATH="${PROJECT_ROOT}/external/install/maya${MAYA_VERSION}_linux/glog/lib64"
GFLAGS_ROOT="${PROJECT_ROOT}/external/install/maya${MAYA_VERSION}_linux/libmv"
GFLAGS_INCLUDE_DIR="${PROJECT_ROOT}/external/install/maya${MAYA_VERSION}_linux/libmv/include/third_party/gflags"
GFLAGS_LIB_PATH="${PROJECT_ROOT}/external/install/maya${MAYA_VERSION}_linux/libmv/lib"
OPENMVG_ROOT="${PROJECT_ROOT}/external/install/maya${MAYA_VERSION}_linux/openMVG"
OPENMVG_DIR="${OPENMVG_ROOT}/share/openMVG/cmake"
OPENMVG_INCLUDE_DIR="${OPENMVG_ROOT}/include"
OPENMVG_LIB_PATH="${OPENMVG_ROOT}/lib"
LDPK_ROOT="${PROJECT_ROOT}/external/install/maya${MAYA_VERSION}_linux/ldpk"
LDPK_INCLUDE_DIR="${LDPK_ROOT}/include"
LDPK_LIB_PATH="${LDPK_ROOT}/lib"
MMSCENEGRAPH_INSTALL_DIR="${PROJECT_ROOT}/external/install/maya${MAYA_VERSION}_windows64/mmscenegraph"
MMSCENEGRAPH_CMAKE_CONFIG_DIR="${MMSCENEGRAPH_INSTALL_DIR}/lib/cmake/mmscenegraph"

# Build mmSolver project
mkdir -p build_linux_maya${MAYA_VERSION}_${BUILD_TYPE}
cd build_linux_maya${MAYA_VERSION}_${BUILD_TYPE}
# -DCMAKE_CXX_CLANG_TIDY="clang-tidy"
export MAYA_VERSION=${MAYA_VERSION}
${CMAKE_EXE} \
    -DCMAKE_BUILD_TYPE=${BUILD_TYPE} \
    -DCMAKE_INSTALL_PREFIX=${INSTALL_MODULE_DIR} \
    -DCMAKE_POSITION_INDEPENDENT_CODE=1 \
    -DCMAKE_CXX_STANDARD=${CXX_STANDARD} \
    -DBUILD_PLUGIN=${BUILD_PLUGIN} \
    -DBUILD_PYTHON=${BUILD_PYTHON} \
    -DBUILD_MEL=${BUILD_MEL} \
    -DBUILD_3DEQUALIZER=${BUILD_3DEQUALIZER} \
    -DBUILD_SYNTHEYES=${BUILD_SYNTHEYES} \
    -DBUILD_BLENDER=${BUILD_BLENDER} \
    -DBUILD_QT_UI=${BUILD_QT_UI} \
    -DBUILD_DOCS=${BUILD_DOCS} \
    -DBUILD_ICONS=${BUILD_ICONS} \
    -DBUILD_CONFIG=${BUILD_CONFIG} \
    -DBUILD_TESTS=${BUILD_TESTS} \
    -DLIBMV_ROOT=${LIBMV_ROOT} \
    -DCMINPACK_ROOT=${CMINPACK_ROOT} \
    -DCXSPARSE_ROOT=${CXSPARSE_ROOT} \
    -DCeres_DIR=${CERES_DIR} \
    -DEIGEN3_INCLUDE_DIR=${EIGEN3_INCLUDE_DIR} \
    -DGLOG_ROOT=${GLOG_ROOT} \
    -DGLOG_LIB_PATH=${GLOG_LIB_PATH} \
    -DGLOG_INCLUDE_DIR=${GLOG_INCLUDE_DIR} \
    -DGFLAGS_ROOT=${GFLAGS_ROOT} \
    -DGFLAGS_INCLUDE_DIR=${GFLAGS_INCLUDE_DIR} \
    -DOpenMVG_DIR=${OPENMVG_DIR} \
    -DLDPK_ROOT=${LDPK_ROOT} \
    -DLDPK_INCLUDE_DIR=${LDPK_INCLUDE_DIR} \
    -DLDPK_LIB_PATH=${LDPK_LIB_PATH} \
    -DMAYA_LOCATION=${MAYA_LOCATION} \
    -DMAYA_VERSION=${MAYA_VERSION} \
    -DMMSCENEGRAPH_LIB_DIR=${MMSCENEGRAPH_LIB_DIR} \
    -DMMSCENEGRAPH_INCLUDE_DIR=${MMSCENEGRAPH_INCLUDE_DIR} \
    ..

NUMBER_OF_CPUS=`nproc --all`
${CMAKE_EXE} --build . --parallel ${NUMBER_OF_CPUS}

# Comment this line out to stop the automatic install into the home directory.
${CMAKE_EXE} --install .

# Run tests
if [ ${RUN_TESTS} -eq 1 ]; then
    ${CMAKE_EXE} --build . --target test
fi

# Build ZIP package.
if [ ${BUILD_PACKAGE} -eq 1 ]; then
    ${CMAKE_EXE} --build . --target package
fi

# Return back project root directory.
cd ${CWD}
