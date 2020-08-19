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
 * Command for running mmSolver.
 */

// Internal
#include <MMSolverCmd.h>
#include <core/bundleAdjust_data.h>
#include <core/bundleAdjust_base.h>
#include <mayaUtils.h>

// STL
#include <cmath>
#include <cassert>
#include <cstdlib>
#include <algorithm>

// Utils
#include <utilities/debugUtils.h>

// Maya
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MFnDependencyNode.h>

// Internal Objects
#include <Attr.h>
#include <Marker.h>
#include <Bundle.h>
#include <Camera.h>


MMSolverCmd::~MMSolverCmd() {}

void *MMSolverCmd::creator() {
    return new MMSolverCmd();
}

MString MMSolverCmd::cmdName() {
    return MString("mmSolver");
}

/*
 * Tell Maya we have a syntax function.
 */
bool MMSolverCmd::hasSyntax() const {
    return true;
}

bool MMSolverCmd::isUndoable() const {
    return true;
}

/*
 * Add flags to the command syntax
 */
MSyntax MMSolverCmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    // Flags
    syntax.addFlag(CAMERA_FLAG, CAMERA_FLAG_LONG,
                   MSyntax::kString, MSyntax::kString);
    syntax.addFlag(MARKER_FLAG, MARKER_FLAG_LONG,
                   MSyntax::kString, MSyntax::kString, MSyntax::kString);
    syntax.addFlag(ATTR_FLAG, ATTR_FLAG_LONG,
                   MSyntax::kString,
                   MSyntax::kString, MSyntax::kString,
                   MSyntax::kString, MSyntax::kString);
    syntax.addFlag(STIFFNESS_FLAG, STIFFNESS_FLAG_LONG,
                   MSyntax::kString,
                   MSyntax::kString,
                   MSyntax::kString,
                   MSyntax::kString);
    syntax.addFlag(SMOOTHNESS_FLAG, SMOOTHNESS_FLAG_LONG,
                   MSyntax::kString,
                   MSyntax::kString,
                   MSyntax::kString,
                   MSyntax::kString);
    syntax.addFlag(FRAME_FLAG, FRAME_FLAG_LONG,
                   MSyntax::kLong);
    syntax.addFlag(TAU_FLAG, TAU_FLAG_LONG,
                   MSyntax::kDouble);
    syntax.addFlag(EPSILON1_FLAG, EPSILON1_FLAG_LONG,
                   MSyntax::kDouble);
    syntax.addFlag(EPSILON2_FLAG, EPSILON2_FLAG_LONG,
                   MSyntax::kDouble);
    syntax.addFlag(EPSILON3_FLAG, EPSILON3_FLAG_LONG,
                   MSyntax::kDouble);
    syntax.addFlag(DELTA_FLAG, DELTA_FLAG_LONG,
                   MSyntax::kDouble);
    syntax.addFlag(AUTO_DIFF_TYPE_FLAG, AUTO_DIFF_TYPE_FLAG_LONG,
                   MSyntax::kUnsigned);
    syntax.addFlag(AUTO_PARAM_SCALE_FLAG, AUTO_PARAM_SCALE_FLAG_LONG,
                   MSyntax::kUnsigned);
    syntax.addFlag(ROBUST_LOSS_TYPE_FLAG, ROBUST_LOSS_TYPE_FLAG_LONG,
                   MSyntax::kUnsigned);
    syntax.addFlag(ROBUST_LOSS_SCALE_FLAG, ROBUST_LOSS_SCALE_FLAG_LONG,
                   MSyntax::kDouble);
    syntax.addFlag(SOLVER_TYPE_FLAG, SOLVER_TYPE_FLAG_LONG,
                   MSyntax::kUnsigned);
    syntax.addFlag(ITERATIONS_FLAG, ITERATIONS_FLAG_LONG,
                   MSyntax::kUnsigned);
    syntax.addFlag(ACCEPT_ONLY_BETTER_FLAG, ACCEPT_ONLY_BETTER_FLAG_LONG,
                   MSyntax::kBoolean);
    // TODO: Deprecate 'verbose' flag, replace with 'log level' flag.
    syntax.addFlag(VERBOSE_FLAG, VERBOSE_FLAG_LONG,
                   MSyntax::kBoolean);
    syntax.addFlag(DEBUG_FILE_FLAG, DEBUG_FILE_FLAG_LONG,
                   MSyntax::kString);
    syntax.addFlag(PRINT_STATS_FLAG, PRINT_STATS_FLAG_LONG,
                   MSyntax::kString);

    // We can use marker and attr flags more than once.
    syntax.makeFlagMultiUse(CAMERA_FLAG);
    syntax.makeFlagMultiUse(MARKER_FLAG);
    syntax.makeFlagMultiUse(ATTR_FLAG);
    syntax.makeFlagMultiUse(FRAME_FLAG);
    syntax.makeFlagMultiUse(PRINT_STATS_FLAG);
    syntax.makeFlagMultiUse(STIFFNESS_FLAG);
    syntax.makeFlagMultiUse(SMOOTHNESS_FLAG);

    return syntax;
}

/*
 * Parse command line arguments
 */
MStatus MMSolverCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    // Get 'Verbose'
    // TODO: Deprecate 'verbose' flag, replace with 'log level' flag.
    m_verbose = VERBOSE_DEFAULT_VALUE;
    if (argData.isFlagSet(VERBOSE_FLAG)) {
        status = argData.getFlagArgument(VERBOSE_FLAG, 0, m_verbose);
        CHECK_MSTATUS(status);
    }

    // Get 'Debug File'
    m_debugFile = DEBUG_FILE_DEFAULT_VALUE;
    if (argData.isFlagSet(DEBUG_FILE_FLAG)) {
        status = argData.getFlagArgument(DEBUG_FILE_FLAG, 0, m_debugFile);
        CHECK_MSTATUS(status);
    }

    // Get 'Accept Only Better'
    m_acceptOnlyBetter = ACCEPT_ONLY_BETTER_DEFAULT_VALUE;
    if (argData.isFlagSet(ACCEPT_ONLY_BETTER_FLAG)) {
        status = argData.getFlagArgument(ACCEPT_ONLY_BETTER_FLAG, 0, m_acceptOnlyBetter);
        CHECK_MSTATUS(status);
    }

    // Get 'Print Statistics'
    unsigned int printStatsNum = argData.numberOfFlagUses(PRINT_STATS_FLAG);
    m_printStatsList.clear();
    for (unsigned int i = 0; i < printStatsNum; ++i) {
        MArgList printStatsArgs;
        status = argData.getFlagArgumentList(PRINT_STATS_FLAG, i, printStatsArgs);
        if (status == MStatus::kSuccess) {
            MString printStatsArg = "";
            for (unsigned j = 0; j < printStatsArgs.length(); ++j) {
                printStatsArg = printStatsArgs.asString(j, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);
                m_printStatsList.append(printStatsArg);
            }
         }
    }

    m_cameraList.clear();
    m_markerList.clear();
    m_bundleList.clear();

    // Get 'Camera'
    MString cameraTransform = "";
    MString cameraShape = "";
    unsigned int cameraNum = argData.numberOfFlagUses(CAMERA_FLAG);
    for (unsigned int i = 0; i < cameraNum; ++i) {

        MArgList cameraArgs;
        status = argData.getFlagArgumentList(CAMERA_FLAG, i, cameraArgs);
        if (status == MStatus::kSuccess) {
            if (cameraArgs.length() != 2) {
                ERR("Camera argument list must have 2 arguments; "
                    << "\"cameraTransform\", \"cameraShape\".");
                continue;
            }

            cameraTransform = cameraArgs.asString(0, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            nodeExistsAndIsType(cameraTransform, MFn::Type::kTransform);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            cameraShape = cameraArgs.asString(1, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            nodeExistsAndIsType(cameraShape, MFn::Type::kCamera);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            CameraPtr camera = CameraPtr(new Camera());
            camera->setTransformNodeName(cameraTransform);
            camera->setShapeNodeName(cameraShape);
            m_cameraList.push_back(camera);
        }
    }

    // Get 'Markers'
    MString markerName = "";
    MString cameraName = "";
    MString bundleName = "";
    unsigned int markerNum = argData.numberOfFlagUses(MARKER_FLAG);
    for (unsigned int i = 0; i < markerNum; ++i) {
        MArgList markerArgs;
        status = argData.getFlagArgumentList(MARKER_FLAG, i, markerArgs);
        if (status == MStatus::kSuccess) {
            if (markerArgs.length() != 3) {
                ERR("Marker argument list must have 3 arguments; "
                  << "\"marker\", \"cameraShape\",  \"bundle\".");
                continue;
            }

            markerName = markerArgs.asString(0, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            status = nodeExistsAndIsType(markerName, MFn::Type::kTransform);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            cameraName = markerArgs.asString(1, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            status = nodeExistsAndIsType(cameraName, MFn::Type::kCamera);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            bundleName = markerArgs.asString(2, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            status = nodeExistsAndIsType(bundleName, MFn::Type::kTransform);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            // Camera
            CameraPtr camera = CameraPtr(new Camera());
            for (unsigned int j = 0; j < m_cameraList.size(); ++j) {
                if (m_cameraList[j]->getShapeNodeName() == cameraName) {
                    camera = m_cameraList[j];
                    break;
                }
            }
            if (camera->getShapeNodeName() == "") {
                ERR("Camera shape name was not given with marker. "
                            << "marker=" << markerName << " "
                            << "camera=" << cameraName << " "
                            << "bundle=" << bundleName);
            }
            // TODO: Print warnings if any of the following attributes
            // on the camera are animated/connected:
            //
            // - camera.horizontalFilmAperture
            // - camera.verticalFilmAperture
            // - camera.nearClippingPlane
            // - camera.farClippingPlane
            // - camera.cameraScale
            // - camera.filmFit

            // Bundle
            BundlePtr bundle = BundlePtr(new Bundle());
            for (unsigned int j = 0; j < m_bundleList.size(); ++j) {
                if (m_bundleList[j]->getNodeName() == bundleName) {
                    bundle = m_bundleList[j];
                    break;
                }
            }
            if (bundle->getNodeName() == "") {
                bundle->setNodeName(bundleName);
            }

            // Marker
            for (unsigned int j = 0; j < m_markerList.size(); ++j) {
                if (m_markerList[j]->getNodeName() == markerName) {
                    ERR("Marker name cannot be specified more than once. "
                        << "markerName=" << markerName);
                }
            }
            MarkerPtr marker = MarkerPtr(new Marker());
            marker->setNodeName(markerName);
            marker->setBundle(bundle);
            marker->setCamera(camera);

            m_markerList.push_back(marker);
            m_bundleList.push_back(bundle);
        }
    }

    // Get 'Attributes'
    m_attrList.clear();
    unsigned int attrsNum = argData.numberOfFlagUses(ATTR_FLAG);
    for (unsigned int i = 0; i < attrsNum; ++i) {
        MArgList attrArgs;
        status = argData.getFlagArgumentList(ATTR_FLAG, i, attrArgs);
        if (status == MStatus::kSuccess) {
            if (attrArgs.length() != 5) {
                ERR("Attribute argument list must have 5 argument; "
                    << "\"node.attribute\", "
                    << "\"min\", \"max\", "
                    << "\"offset\", \"scale\".");
                continue;
            }

            // TODO: Print errors and exit with failure if any of the
            // following attributes are detected:
            //
            // - camera.horizontalFilmAperture
            // - camera.verticalFilmAperture
            // - camera.nearClippingPlane
            // - camera.farClippingPlane
            // - camera.cameraScale
            // - camera.filmFit
            // - defaultResolution.width
            // - defaultResolution.height
            // - defaultResolution.deviceAspectRatio

            AttrPtr attr = AttrPtr(new Attr());
            MString nodeAttrName = attrArgs.asString(0);
            attr->setName(nodeAttrName);

            // Get Min/Max attribute values
            MString minValueStr = attrArgs.asString(1);
            MString maxValueStr = attrArgs.asString(2);
            if (minValueStr.isDouble()) {
                attr->setMinimumValue(minValueStr.asDouble());
            }
            if (maxValueStr.isDouble()) {
                attr->setMaximumValue(maxValueStr.asDouble());
            }

            // Add an internal offset value used to make sure values
            // are not at 0.0.
            MString offsetValueStr = attrArgs.asString(3);
            if (offsetValueStr.isDouble()) {
                attr->setOffsetValue(offsetValueStr.asDouble());
            }

            // Add an internal scale value.
            //
            // TODO: Get the node this attribute is connected to. If
            // it's a DAG node we must query the position, then create
            // a function to scale down attributes farther away from
            // camera. Issue #26.
            MString scaleValueStr = attrArgs.asString(4);
            if (scaleValueStr.isDouble()) {
                attr->setScaleValue(scaleValueStr.asDouble());
            }

            m_attrList.push_back(attr);
            MPlug attrPlug = attr->getPlug();
        }
    }

    // Get Stiffness Values
    unsigned int stiffnessNum = argData.numberOfFlagUses(STIFFNESS_FLAG);
    for (unsigned int i = 0; i < stiffnessNum; ++i) {
        MArgList stiffnessArgs;
        status = argData.getFlagArgumentList(STIFFNESS_FLAG, i, stiffnessArgs);
        if (status == MStatus::kSuccess) {
            if (stiffnessArgs.length() != 4) {
                ERR("Attribute Stiffness argument list must have 4 argument; "
                            << "\"node.attribute\", "
                            << "\"node.attributeStiffWeight\", "
                            << "\"node.attributeStiffVariance\", "
                            << "\"node.attributeStiffValue\".");
                continue;
            }

            // Find the already created Attribute.
            MString nodeAttrName = stiffnessArgs.asString(0);
            AttrPtr foundAttr;
            int foundIndex = 0;
            for (AttrPtrListIt ait = m_attrList.begin();
                 ait != m_attrList.end();
                 ++ait) {
                AttrPtr attr = *ait;
                if (nodeAttrName == attr->getName()) {
                    foundAttr = attr;
                    break;
                }
                foundIndex++;
            }
            if (foundAttr->getName() == ".") {
                ERR("Attribute Stiffness name is not a declared attribute; "
                            << nodeAttrName);
                continue;
            }
            AttrPtr stiffWeightAttr = AttrPtr(new Attr());
            MString weightNodeAttrName = stiffnessArgs.asString(1);
            stiffWeightAttr->setName(weightNodeAttrName);

            AttrPtr stiffVarianceAttr = AttrPtr(new Attr());
            MString varianceNodeAttrName = stiffnessArgs.asString(2);
            stiffVarianceAttr->setName(varianceNodeAttrName);

            AttrPtr stiffValueAttr = AttrPtr(new Attr());
            MString valueNodeAttrName = stiffnessArgs.asString(3);
            stiffValueAttr->setName(valueNodeAttrName);

            StiffAttrsPtr stiffAttrs = StiffAttrsPtr(new StiffAttrs());
            stiffAttrs->attrIndex = foundIndex;
            stiffAttrs->weightAttr = stiffWeightAttr;
            stiffAttrs->varianceAttr = stiffVarianceAttr;
            stiffAttrs->valueAttr = stiffValueAttr;

            m_stiffAttrsList.push_back(stiffAttrs);
        }
    }

    // Get Smoothness Values
    unsigned int smoothnessNum = argData.numberOfFlagUses(SMOOTHNESS_FLAG);
    for (unsigned int i = 0; i < smoothnessNum; ++i) {
        MArgList smoothnessArgs;
        status = argData.getFlagArgumentList(SMOOTHNESS_FLAG, i, smoothnessArgs);
        if (status == MStatus::kSuccess) {
            if (smoothnessArgs.length() != 4) {
                ERR("Attribute Smoothness argument list must have 4 argument; "
                            << "\"node.attribute\", "
                            << "\"node.attributeSmoothWeight\", "
                            << "\"node.attributeSmoothVariance\", "
                            << "\"node.attributeSmoothValue\".");
                continue;
            }

            // Find the already created Attribute.
            MString nodeAttrName = smoothnessArgs.asString(0);
            AttrPtr foundAttr;
            int foundIndex = 0;
            for (AttrPtrListIt ait = m_attrList.begin();
                 ait != m_attrList.end();
                 ++ait) {
                AttrPtr attr = *ait;
                if (nodeAttrName == attr->getName()) {
                    foundAttr = attr;
                    break;
                }
                foundIndex++;
            }
            if (foundAttr->getName() == ".") {
                ERR("Attribute Smoothness name is not a declared attribute; "
                            << nodeAttrName);
                continue;
            }
            AttrPtr smoothWeightAttr = AttrPtr(new Attr());
            MString weightNodeAttrName = smoothnessArgs.asString(1);
            smoothWeightAttr->setName(weightNodeAttrName);

            AttrPtr smoothVarianceAttr = AttrPtr(new Attr());
            MString varianceNodeAttrName = smoothnessArgs.asString(2);
            smoothVarianceAttr->setName(varianceNodeAttrName);

            AttrPtr smoothValueAttr = AttrPtr(new Attr());
            MString valueNodeAttrName = smoothnessArgs.asString(3);
            smoothValueAttr->setName(valueNodeAttrName);

            SmoothAttrsPtr smoothAttrs = SmoothAttrsPtr(new SmoothAttrs());
            smoothAttrs->attrIndex = foundIndex;
            smoothAttrs->weightAttr = smoothWeightAttr;
            smoothAttrs->varianceAttr = smoothVarianceAttr;
            smoothAttrs->valueAttr = smoothValueAttr;

            m_smoothAttrsList.push_back(smoothAttrs);
        }
    }

    // Get 'Frames'
    m_frameList.clear();
    MTime::Unit unit = MTime::uiUnit();
    unsigned int framesNum = argData.numberOfFlagUses(FRAME_FLAG);
    for (unsigned int i = 0; i < framesNum; ++i) {
        MArgList frameArgs;
        status = argData.getFlagArgumentList(FRAME_FLAG, i, frameArgs);
        if (status == MStatus::kSuccess) {
            if (frameArgs.length() != 1) {
                ERR("Attribute argument list must have 1 argument; \"frame\".");
                continue;
            }
            int value = frameArgs.asInt(0, &status);
            CHECK_MSTATUS(status);

            MTime frame = MTime((double) value, unit);
            m_frameList.append(frame);
        }
    }

    // Make sure we have a frame list.
    if (m_frameList.length() == 0) {
        status = MS::kFailure;
        status.perror("Frame List length is 0, must have a frame to solve.");
        return status;
    }

    // Get 'Solver Type'
    SolverTypePair solverType = getSolverTypeDefault();
    m_solverType = solverType.first;
    if (argData.isFlagSet(SOLVER_TYPE_FLAG)) {
        status = argData.getFlagArgument(SOLVER_TYPE_FLAG, 0, m_solverType);
        CHECK_MSTATUS(status);
    }

    // Set defaults based on solver type chosen.
    if (m_solverType == SOLVER_TYPE_CMINPACK_LMDIF) {
        m_iterations = CMINPACK_LMDIF_ITERATIONS_DEFAULT_VALUE;
        m_tau = CMINPACK_LMDIF_TAU_DEFAULT_VALUE;
        m_epsilon1 = CMINPACK_LMDIF_EPSILON1_DEFAULT_VALUE;
        m_epsilon2 = CMINPACK_LMDIF_EPSILON2_DEFAULT_VALUE;
        m_epsilon3 = CMINPACK_LMDIF_EPSILON3_DEFAULT_VALUE;
        m_delta = CMINPACK_LMDIF_DELTA_DEFAULT_VALUE;
        m_autoDiffType = CMINPACK_LMDIF_AUTO_DIFF_TYPE_DEFAULT_VALUE;
        m_autoParamScale = CMINPACK_LMDIF_AUTO_PARAM_SCALE_DEFAULT_VALUE;
        m_robustLossType = CMINPACK_LMDIF_ROBUST_LOSS_TYPE_DEFAULT_VALUE;
        m_robustLossScale = CMINPACK_LMDIF_ROBUST_LOSS_SCALE_DEFAULT_VALUE;
        m_supportAutoDiffForward = CMINPACK_LMDIF_SUPPORT_AUTO_DIFF_FORWARD_VALUE;
        m_supportAutoDiffCentral = CMINPACK_LMDIF_SUPPORT_AUTO_DIFF_CENTRAL_VALUE;
        m_supportParameterBounds = CMINPACK_LMDIF_SUPPORT_PARAMETER_BOUNDS_VALUE;
        m_supportRobustLoss = CMINPACK_LMDIF_SUPPORT_ROBUST_LOSS_VALUE;
    } else if (m_solverType == SOLVER_TYPE_CMINPACK_LMDER) {
        m_iterations = CMINPACK_LMDER_ITERATIONS_DEFAULT_VALUE;
        m_tau = CMINPACK_LMDER_TAU_DEFAULT_VALUE;
        m_epsilon1 = CMINPACK_LMDER_EPSILON1_DEFAULT_VALUE;
        m_epsilon2 = CMINPACK_LMDER_EPSILON2_DEFAULT_VALUE;
        m_epsilon3 = CMINPACK_LMDER_EPSILON3_DEFAULT_VALUE;
        m_delta = CMINPACK_LMDER_DELTA_DEFAULT_VALUE;
        m_autoDiffType = CMINPACK_LMDER_AUTO_DIFF_TYPE_DEFAULT_VALUE;
        m_autoParamScale = CMINPACK_LMDER_AUTO_PARAM_SCALE_DEFAULT_VALUE;
        m_robustLossType = CMINPACK_LMDER_ROBUST_LOSS_TYPE_DEFAULT_VALUE;
        m_robustLossScale = CMINPACK_LMDER_ROBUST_LOSS_SCALE_DEFAULT_VALUE;
        m_supportAutoDiffForward = CMINPACK_LMDER_SUPPORT_AUTO_DIFF_FORWARD_VALUE;
        m_supportAutoDiffCentral = CMINPACK_LMDER_SUPPORT_AUTO_DIFF_CENTRAL_VALUE;
        m_supportParameterBounds = CMINPACK_LMDER_SUPPORT_PARAMETER_BOUNDS_VALUE;
        m_supportRobustLoss = CMINPACK_LMDER_SUPPORT_ROBUST_LOSS_VALUE;
    } else if (m_solverType == SOLVER_TYPE_LEVMAR) {
        m_iterations = LEVMAR_ITERATIONS_DEFAULT_VALUE;
        m_tau = LEVMAR_TAU_DEFAULT_VALUE;
        m_epsilon1 = LEVMAR_EPSILON1_DEFAULT_VALUE;
        m_epsilon2 = LEVMAR_EPSILON2_DEFAULT_VALUE;
        m_epsilon3 = LEVMAR_EPSILON3_DEFAULT_VALUE;
        m_delta = LEVMAR_DELTA_DEFAULT_VALUE;
        m_autoDiffType = LEVMAR_AUTO_DIFF_TYPE_DEFAULT_VALUE;
        m_autoParamScale = LEVMAR_AUTO_PARAM_SCALE_DEFAULT_VALUE;
        m_robustLossType = LEVMAR_ROBUST_LOSS_TYPE_DEFAULT_VALUE;
        m_robustLossScale = LEVMAR_ROBUST_LOSS_SCALE_DEFAULT_VALUE;
        m_supportAutoDiffForward = LEVMAR_SUPPORT_AUTO_DIFF_FORWARD_VALUE;
        m_supportAutoDiffCentral = LEVMAR_SUPPORT_AUTO_DIFF_CENTRAL_VALUE;
        m_supportParameterBounds = LEVMAR_SUPPORT_PARAMETER_BOUNDS_VALUE;
        m_supportRobustLoss = LEVMAR_SUPPORT_ROBUST_LOSS_VALUE;
    } else {
        ERR("Solver Type is invalid. "
            << "Value may be 0 or 1 (0 == levmar, 1 == cminpack_lm);"
            << "value=" << m_solverType);
        status = MS::kFailure;
        status.perror("Solver Type is invalid. Value may be 0 or 1 (0 == levmar, 1 == cminpack_lm).");
        return status;
    }

    // Get 'Iterations'
    if (argData.isFlagSet(ITERATIONS_FLAG)) {
        status = argData.getFlagArgument(ITERATIONS_FLAG, 0, m_iterations);
        CHECK_MSTATUS(status);
    }

    // Get 'Tau'
    if (argData.isFlagSet(TAU_FLAG)) {
        status = argData.getFlagArgument(TAU_FLAG, 0, m_tau);
        CHECK_MSTATUS(status);
    }
    m_tau = std::max(0.0, m_tau);
    m_tau = std::min(m_tau, 1.0);
    assert((0.0 <= m_tau) <= 1.0);

    // Get 'Epsilon1'
    if (argData.isFlagSet(EPSILON1_FLAG)) {
        status = argData.getFlagArgument(EPSILON1_FLAG, 0, m_epsilon1);
        CHECK_MSTATUS(status);
    }

    // Get 'Epsilon2'
    if (argData.isFlagSet(EPSILON2_FLAG)) {
        status = argData.getFlagArgument(EPSILON2_FLAG, 0, m_epsilon2);
        CHECK_MSTATUS(status);
    }

    // Get 'Epsilon3'
    if (argData.isFlagSet(EPSILON3_FLAG)) {
        status = argData.getFlagArgument(EPSILON3_FLAG, 0, m_epsilon3);
        CHECK_MSTATUS(status);
    }

    // Get 'Delta'
    if (argData.isFlagSet(DELTA_FLAG)) {
        status = argData.getFlagArgument(DELTA_FLAG, 0, m_delta);
        CHECK_MSTATUS(status);
    }

    // Get 'Auto Differencing Type'
    if (argData.isFlagSet(AUTO_DIFF_TYPE_FLAG)) {
        status = argData.getFlagArgument(AUTO_DIFF_TYPE_FLAG, 0, m_autoDiffType);
        CHECK_MSTATUS(status);
    }

    // Get 'Auto Parameter Scaling'
    if (argData.isFlagSet(AUTO_PARAM_SCALE_FLAG)) {
        status = argData.getFlagArgument(AUTO_PARAM_SCALE_FLAG, 0, m_autoParamScale);
        CHECK_MSTATUS(status);
    }

    // Get 'Robust Loss Type'
    if (argData.isFlagSet(ROBUST_LOSS_TYPE_FLAG)) {
        status = argData.getFlagArgument(ROBUST_LOSS_TYPE_FLAG, 0, m_robustLossType);
        CHECK_MSTATUS(status);
    }

    // Get 'Robust Loss Scale'
    if (argData.isFlagSet(ROBUST_LOSS_SCALE_FLAG)) {
        status = argData.getFlagArgument(ROBUST_LOSS_SCALE_FLAG, 0, m_robustLossScale);
        CHECK_MSTATUS(status);
    }
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
    solverOptions.solverType = m_solverType;
    solverOptions.solverSupportsAutoDiffForward = m_supportAutoDiffForward;
    solverOptions.solverSupportsAutoDiffCentral = m_supportAutoDiffCentral;
    solverOptions.solverSupportsParameterBounds = m_supportParameterBounds;
    solverOptions.solverSupportsRobustLoss = m_supportRobustLoss;

    MStringArray outResult;
    bool ret = solve(
            solverOptions,
            m_cameraList,
            m_markerList,
            m_bundleList,
            m_attrList,
            m_frameList,
            m_stiffAttrsList,
            m_smoothAttrsList,
            m_dgmod,
            m_curveChange,
            m_computation,
            m_acceptOnlyBetter,
            m_debugFile,
            m_printStatsList,
            m_verbose,
            outResult
    );

    MMSolverCmd::setResult(outResult);
    if (ret == false) {
        WRN("mmSolver: Solver returned false!");
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
//    and then redoes it.  No arguments are passed in as all of the necessary
//    information is cached by the doIt method.
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
