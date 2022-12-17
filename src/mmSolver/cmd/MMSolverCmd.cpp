/*
 * Copyright (C) 2018, 2019 David Cattermole.
 *
 * This file is part of mmSolver.
 *
 * mmSolver is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * mmSolver is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
 * ====================================================================
 *
 * Command for running the main solver.
 *
 * 'mmSolver' is the primary and most flexible solving command in the
 * mayaMatchMoveSolver project.
 */

#include "MMSolverCmd.h"

// STL
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdlib>

// Maya
#include <maya/MFnDependencyNode.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MStreamUtils.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>

// MM Solver
#include "mmSolver/adjust/adjust_base.h"
#include "mmSolver/adjust/adjust_data.h"
#include "mmSolver/adjust/adjust_defines.h"
#include "mmSolver/cmd/common_arg_flags.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {

MMSolverCmd::~MMSolverCmd() {}

void *MMSolverCmd::creator() { return new MMSolverCmd(); }

MString MMSolverCmd::cmdName() { return MString("mmSolver"); }

/*
 * Tell Maya we have a syntax function.
 */
bool MMSolverCmd::hasSyntax() const { return true; }

bool MMSolverCmd::isUndoable() const { return true; }

/*
 * Add flags to the command syntax
 */
MSyntax MMSolverCmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    createSolveObjectSyntax(syntax);
    createAttributeDetailsSyntax(syntax);
    createSolveFramesSyntax(syntax);
    createSolveInfoSyntax(syntax);
    createSolveLogSyntax(syntax);

    return syntax;
}

/*
 * Parse command line arguments
 */
MStatus MMSolverCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = parseSolveObjectArguments(argData, m_cameraList, m_markerList,
                                       m_bundleList, m_attrList);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = parseAttributeDetailsArguments(
        argData, m_attrList, m_stiffAttrsList, m_smoothAttrsList);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = parseSolveFramesArguments(argData, m_frameList);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = parseSolveInfoArguments(
        argData, m_iterations, m_tau, m_epsilon1, m_epsilon2, m_epsilon3,
        m_delta, m_autoDiffType, m_autoParamScale, m_robustLossType,
        m_robustLossScale, m_solverType, m_sceneGraphMode, m_timeEvalMode,
        m_acceptOnlyBetter, m_frameSolveMode, m_supportAutoDiffForward,
        m_supportAutoDiffCentral, m_supportParameterBounds, m_supportRobustLoss,
        m_removeUnusedMarkers, m_removeUnusedAttributes, m_imageWidth);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = parseSolveLogArguments(argData, m_printStatsList, m_logLevel);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    return status;
}

MStatus MMSolverCmd::doIt(const MArgList &args) {
    //
    //  Description:
    //    implements the MEL mmSolver command.
    //
    //  Arguments:
    //    argList - the argument list that was passes to the command from MEL
    //
    //  Return Value:
    //    MS::kSuccess - command succeeded
    //    MS::kFailure - command failed (returning this value will cause the
    //                     MEL script that is being run to terminate unless the
    //                     error is caught using a "catch" statement.
    //
    MStatus status = MStatus::kSuccess;

    // Mouse cursor spinning...
    // MGlobal::executeCommand("waitCursor -state on;");

    // Read all the flag arguments.
    status = parseArgs(args);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    assert(m_frameList.length() > 0);

    // Don't store each individual edits, just store the combination
    // of edits.
    m_curveChange.setInteractive(true);

    SolverOptions solverOptions;
    solverOptions.iterMax = m_iterations;
    solverOptions.tau = m_tau;
    solverOptions.eps1 = m_epsilon1;
    solverOptions.eps2 = m_epsilon2;
    solverOptions.eps3 = m_epsilon3;
    solverOptions.delta = m_delta;
    solverOptions.autoDiffType = m_autoDiffType;
    solverOptions.autoParamScale = m_autoParamScale;
    solverOptions.robustLossType = m_robustLossType;
    solverOptions.robustLossScale = m_robustLossScale;
    solverOptions.sceneGraphMode = m_sceneGraphMode;
    solverOptions.solverType = m_solverType;
    solverOptions.timeEvalMode = m_timeEvalMode;
    solverOptions.acceptOnlyBetter = m_acceptOnlyBetter;
    solverOptions.imageWidth = m_imageWidth;
    solverOptions.frameSolveMode = m_frameSolveMode;
    solverOptions.solverSupportsAutoDiffForward = m_supportAutoDiffForward;
    solverOptions.solverSupportsAutoDiffCentral = m_supportAutoDiffCentral;
    solverOptions.solverSupportsParameterBounds = m_supportParameterBounds;
    solverOptions.solverSupportsRobustLoss = m_supportRobustLoss;
    solverOptions.removeUnusedMarkers = m_removeUnusedMarkers;
    solverOptions.removeUnusedAttributes = m_removeUnusedAttributes;

    MStringArray outResult;
    bool ret = solve_v1(solverOptions, m_cameraList, m_markerList, m_bundleList,
                        m_attrList, m_frameList, m_stiffAttrsList,
                        m_smoothAttrsList, m_dgmod, m_curveChange,
                        m_computation, m_printStatsList, m_logLevel, outResult);

    MMSolverCmd::setResult(outResult);
    if (ret == false) {
        MStreamUtils::stdErrorStream()
            << "WARNING: mmSolver: Solver returned false!" << '\n';
    }

    // Mouse cursor back to normal.
    // MGlobal::executeCommand("waitCursor -state off;");
    return status;
}

MStatus MMSolverCmd::redoIt() {
    //
    //  Description:
    //    Implements redo for the MEL mmSolver command.
    //
    //    This method is called when the user has undone a command of this type
    //    and then redoes it.  No arguments are passed in as all of the
    //    necessary information is cached by the doIt method.
    //
    //  Return Value:
    //    MS::kSuccess - command succeeded
    //    MS::kFailure - redoIt failed.  this is a serious problem that will
    //                     likely cause the undo queue to be purged
    //
    MStatus status;
    m_dgmod.doIt();
    m_curveChange.redoIt();
    return status;
}

MStatus MMSolverCmd::undoIt() {
    //
    //  Description:
    //    implements undo for the MEL mmSolver command.
    //
    //    This method is called to undo a previous command of this type.  The
    //    system should be returned to the exact state that it was it previous
    //    to this command being executed.  That includes the selection state.
    //
    //  Return Value:
    //    MS::kSuccess - command succeeded
    //    MS::kFailure - redoIt failed.  this is a serious problem that will
    //                     likely cause the undo queue to be purged
    //
    MStatus status;
    m_curveChange.undoIt();
    m_dgmod.undoIt();
    return status;
}

}  // namespace mmsolver
