/*
 * Copyright (C) 2022 David Cattermole.
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
 * Lens adjustment.
 */

#include "adjust_lensModel.h"

// STL
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdlib>
#include <ctime>
#include <iostream>
#include <limits>
#include <memory>
#include <stdio.h>
#include <string>
#include <vector>
#include <unordered_set>
#include <unordered_map>

// Maya
#include <maya/MAnimCurveChange.h>
#include <maya/MComputation.h>
#include <maya/MDagPath.h>
#include <maya/MDGContext.h>
#include <maya/MFnAnimCurve.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MFnPluginData.h>
#include <maya/MGlobal.h>
#include <maya/MMatrix.h>
#include <maya/MObject.h>
#include <maya/MPoint.h>
#include <maya/MProfiler.h>
#include <maya/MStreamUtils.h>
#include <maya/MSelectionList.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MVector.h>

#if MAYA_API_VERSION >= 20180000
#include <maya/MDGContextGuard.h>
#endif

// MM Scene Graph
#include <mmscenegraph/mmscenegraph.h>

// MM Solver
#include "mmSolver/core/mmdata.h"
#include "mmSolver/core/mmmath.h"
#include "mmSolver/lens/lens_model_3de_anamorphic_deg_4_rotate_squeeze_xy.h"
#include "mmSolver/lens/lens_model_3de_classic.h"
#include "mmSolver/lens/lens_model_3de_radial_decentered_deg_4_cylindric.h"
#include "mmSolver/lens/lens_model_passthrough.h"
#include "mmSolver/lens/lens_model.h"
#include "mmSolver/node/MMLensData.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/utilities/number_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/string_utils.h"
#include "adjust_base.h"
#include "adjust_data.h"


MStatus
setLensModelAttributeValue(
    std::shared_ptr<LensModel> &lensModel,
    const AttrSolverType solverAttrType,
    const double value
) {
    MStatus status = MS::kSuccess;
    if (!lensModel) {
        return status;
    }
    LensModel* lensModelPtr = lensModel.get();
    if (!lensModelPtr) {
        status = MS::kFailure;
        return status;
    }

    auto is_model_3de_classic = 0;
    is_model_3de_classic += solverAttrType == AttrSolverType::kLens3deClassicDistortion;
    is_model_3de_classic += solverAttrType == AttrSolverType::kLens3deClassicAnamorphicSqueeze;
    is_model_3de_classic += solverAttrType == AttrSolverType::kLens3deClassicCurvatureX;
    is_model_3de_classic += solverAttrType == AttrSolverType::kLens3deClassicCurvatureY;
    is_model_3de_classic += solverAttrType == AttrSolverType::kLens3deClassicQuarticDistortion;

    auto is_model_3de_radial_deg_4 = 0;
    is_model_3de_radial_deg_4 += solverAttrType == AttrSolverType::kLens3deRadialDecenteredDeg4CylindricDegree2Distortion;
    is_model_3de_radial_deg_4 += solverAttrType == AttrSolverType::kLens3deRadialDecenteredDeg4CylindricDegree2U;
    is_model_3de_radial_deg_4 += solverAttrType == AttrSolverType::kLens3deRadialDecenteredDeg4CylindricDegree2V;
    is_model_3de_radial_deg_4 += solverAttrType == AttrSolverType::kLens3deRadialDecenteredDeg4CylindricDegree4Distortion;
    is_model_3de_radial_deg_4 += solverAttrType == AttrSolverType::kLens3deRadialDecenteredDeg4CylindricDegree4U;
    is_model_3de_radial_deg_4 += solverAttrType == AttrSolverType::kLens3deRadialDecenteredDeg4CylindricDegree4V;
    is_model_3de_radial_deg_4 += solverAttrType == AttrSolverType::kLens3deRadialDecenteredDeg4CylindricDirection;
    is_model_3de_radial_deg_4 += solverAttrType == AttrSolverType::kLens3deRadialDecenteredDeg4CylindricBending;

    auto is_model_3de_anamorphic_deg_4 = 0;
    is_model_3de_anamorphic_deg_4 += solverAttrType == AttrSolverType::kLens3deAnamorphicDeg4RotateSqueezeXYDegree2Cx02;
    is_model_3de_anamorphic_deg_4 += solverAttrType == AttrSolverType::kLens3deAnamorphicDeg4RotateSqueezeXYDegree2Cy02;
    is_model_3de_anamorphic_deg_4 += solverAttrType == AttrSolverType::kLens3deAnamorphicDeg4RotateSqueezeXYDegree2Cx22;
    is_model_3de_anamorphic_deg_4 += solverAttrType == AttrSolverType::kLens3deAnamorphicDeg4RotateSqueezeXYDegree2Cy22;
    is_model_3de_anamorphic_deg_4 += solverAttrType == AttrSolverType::kLens3deAnamorphicDeg4RotateSqueezeXYDegree4Cx04;
    is_model_3de_anamorphic_deg_4 += solverAttrType == AttrSolverType::kLens3deAnamorphicDeg4RotateSqueezeXYDegree4Cy04;
    is_model_3de_anamorphic_deg_4 += solverAttrType == AttrSolverType::kLens3deAnamorphicDeg4RotateSqueezeXYDegree4Cx24;
    is_model_3de_anamorphic_deg_4 += solverAttrType == AttrSolverType::kLens3deAnamorphicDeg4RotateSqueezeXYDegree4Cy24;
    is_model_3de_anamorphic_deg_4 += solverAttrType == AttrSolverType::kLens3deAnamorphicDeg4RotateSqueezeXYDegree4Cx44;
    is_model_3de_anamorphic_deg_4 += solverAttrType == AttrSolverType::kLens3deAnamorphicDeg4RotateSqueezeXYDegree4Cy44;
    is_model_3de_anamorphic_deg_4 += solverAttrType == AttrSolverType::kLens3deAnamorphicDeg4RotateSqueezeXYLensRotation;
    is_model_3de_anamorphic_deg_4 += solverAttrType == AttrSolverType::kLens3deAnamorphicDeg4RotateSqueezeXYSqueezeX;
    is_model_3de_anamorphic_deg_4 += solverAttrType == AttrSolverType::kLens3deAnamorphicDeg4RotateSqueezeXYSqueezeY;

    if (is_model_3de_classic > 0) {
        auto ptr = reinterpret_cast<LensModel3deClassic*>(lensModelPtr);
        if (solverAttrType == AttrSolverType::kLens3deClassicDistortion) {
            ptr->setDistortion(value);
        } else if (solverAttrType == AttrSolverType::kLens3deClassicAnamorphicSqueeze) {
            ptr->setAnamorphicSqueeze(value);
        } else if (solverAttrType == AttrSolverType::kLens3deClassicCurvatureX) {
            ptr->setCurvatureX(value);
        } else if (solverAttrType == AttrSolverType::kLens3deClassicCurvatureY) {
            ptr->setCurvatureY(value);
        } else if (solverAttrType == AttrSolverType::kLens3deClassicQuarticDistortion) {
            ptr->setQuarticDistortion(value);
        }
    } else if (is_model_3de_radial_deg_4 > 0) {
        auto ptr = reinterpret_cast<LensModel3deRadialDecenteredDeg4Cylindric*>(lensModelPtr);
        if (solverAttrType == AttrSolverType::kLens3deRadialDecenteredDeg4CylindricDegree2Distortion) {
            ptr->setDegree2Distortion(value);
        } else if (solverAttrType == AttrSolverType::kLens3deRadialDecenteredDeg4CylindricDegree2U) {
            ptr->setDegree2U(value);
        } else if (solverAttrType == AttrSolverType::kLens3deRadialDecenteredDeg4CylindricDegree2V) {
            ptr->setDegree2V(value);
        } else if (solverAttrType == AttrSolverType::kLens3deRadialDecenteredDeg4CylindricDegree4Distortion) {
            ptr->setDegree4Distortion(value);
        } else if (solverAttrType == AttrSolverType::kLens3deRadialDecenteredDeg4CylindricDegree4U) {
            ptr->setDegree4U(value);
        } else if (solverAttrType == AttrSolverType::kLens3deRadialDecenteredDeg4CylindricDegree4V) {
            ptr->setDegree4V(value);
        } else if (solverAttrType == AttrSolverType::kLens3deRadialDecenteredDeg4CylindricDirection) {
            ptr->setCylindricDirection(value);
        } else if (solverAttrType == AttrSolverType::kLens3deRadialDecenteredDeg4CylindricBending) {
            ptr->setCylindricBending(value);
        }
    } else if (is_model_3de_anamorphic_deg_4 > 0) {
        auto ptr = reinterpret_cast<LensModel3deAnamorphicDeg4RotateSqueezeXY*>(lensModelPtr);
        if (solverAttrType == AttrSolverType::kLens3deAnamorphicDeg4RotateSqueezeXYDegree2Cx02) {
            ptr->setDegree2Cx02(value);
        } else if (solverAttrType == AttrSolverType::kLens3deAnamorphicDeg4RotateSqueezeXYDegree2Cy02) {
            ptr->setDegree2Cy02(value);
        } else if (solverAttrType == AttrSolverType::kLens3deAnamorphicDeg4RotateSqueezeXYDegree2Cx22) {
            ptr->setDegree2Cx22(value);
        } else if (solverAttrType == AttrSolverType::kLens3deAnamorphicDeg4RotateSqueezeXYDegree2Cy22) {
            ptr->setDegree2Cy22(value);
        } else if (solverAttrType == AttrSolverType::kLens3deAnamorphicDeg4RotateSqueezeXYDegree4Cx04) {
            ptr->setDegree4Cx04(value);
        } else if (solverAttrType == AttrSolverType::kLens3deAnamorphicDeg4RotateSqueezeXYDegree4Cy04) {
            ptr->setDegree4Cy04(value);
        } else if (solverAttrType == AttrSolverType::kLens3deAnamorphicDeg4RotateSqueezeXYDegree4Cx24) {
            ptr->setDegree4Cx24(value);
        } else if (solverAttrType == AttrSolverType::kLens3deAnamorphicDeg4RotateSqueezeXYDegree4Cy24) {
            ptr->setDegree4Cy24(value);
        } else if (solverAttrType == AttrSolverType::kLens3deAnamorphicDeg4RotateSqueezeXYDegree4Cx44) {
            ptr->setDegree4Cx44(value);
        } else if (solverAttrType == AttrSolverType::kLens3deAnamorphicDeg4RotateSqueezeXYDegree4Cy44) {
            ptr->setDegree4Cy44(value);
        } else if (solverAttrType == AttrSolverType::kLens3deAnamorphicDeg4RotateSqueezeXYLensRotation) {
            ptr->setLensRotation(value);
        } else if (solverAttrType == AttrSolverType::kLens3deAnamorphicDeg4RotateSqueezeXYSqueezeX) {
            ptr->setSqueezeX(value);
        } else if (solverAttrType == AttrSolverType::kLens3deAnamorphicDeg4RotateSqueezeXYSqueezeY) {
            ptr->setSqueezeY(value);
        }
    } else {
        MMSOLVER_ERR("Unknown lens attribute: solverAttrType="
                     << static_cast<int>(solverAttrType));
    }

    return status;
}

MStatus getNodePlug(
    const MObject &node,
    const MString &attrName,
    MPlug &out_plug,
    const bool wantNetworkedPlug=true)
{
    MStatus status = MS::kSuccess;

    MFnDependencyNode mfnDependNode(node, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    out_plug = mfnDependNode.findPlug(attrName, wantNetworkedPlug, &status);
    return status;
}

MStatus getNodeEnabledState(
    const MObject &node,
    const MString &attrName,
    bool &out_enabled)
{
    MStatus status = MS::kSuccess;

    MPlug plug;
    status = getNodePlug(node, attrName, plug);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    if (plug.isNull()) {
        out_enabled = false;
        return status;
    }

    out_enabled = plug.asBool(&status);
    CHECK_MSTATUS(status);

    return status;
}

MStatus getLensModelFromPlug(
    const MPlug &plug,
    std::shared_ptr<LensModel> &out_lensModel)
{
    MStatus status = MS::kSuccess;

    MObject data_object = plug.asMObject(&status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    if (data_object.isNull()) {
        status = MS::kFailure;
        return status;
    }

    MFnPluginData pluginDataFn(data_object);
    const mmsolver::MMLensData* outputLensData =
        (const mmsolver::MMLensData*) pluginDataFn.constData(&status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    if (outputLensData == nullptr) {
        status = MS::kFailure;
        return status;
    }

    auto nodeLens = outputLensData->getValue();
    if (nodeLens == nullptr) {
        status = MS::kFailure;
        return status;
    }

    out_lensModel = nodeLens->cloneAsSharedPtr();
    return status;
}

// Get the node name on the other side of the
// 'inputAttrName' plug connection.
//
// For example, with a connection like this:
//
// mmLensModel3de.outLens -> camera.inLens
//
// with 'node' as a MObject for 'camera' and 'inputAttrName' set as
// "inLens", this function will return the MObject for the
// 'mmLensModel3de' node.
MStatus getConnectedLensNode(
    const MObject &node,
    const MString &inputAttrName,
    MObject &out_node)
{
    MStatus status = MS::kSuccess;
    out_node = MObject();

    MPlug inputPlug;
    status = getNodePlug(
        node,
        inputAttrName,
        inputPlug);
    if (inputPlug.isNull()) {
        return status;
    }

    MPlug upstream_plug = inputPlug.source();
    if (upstream_plug.isNull()) {
        return status;
    }

    out_node = upstream_plug.node();
    return status;
}

MStatus getUniqueNodeName(
    MObject &node,
    MString &out_uniqueNodeName)
{
    MStatus status = MS::kSuccess;

    MDagPath dagPath;
    status = MDagPath::getAPathTo(node, dagPath);
    if (status == MS::kSuccess) {
        out_uniqueNodeName = dagPath.fullPathName();
    } else {
        MFnDependencyNode fnDependNode(node, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        out_uniqueNodeName = fnDependNode.name(&status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    return status;
}

// Get the Lenses for each Camera, and make sure to store the upstream
// lenses too.
MStatus getLensesFromCameraList(
    const CameraPtrList &cameraList,
    std::unordered_map<std::string, int32_t> &out_cameraNodeNameToCameraIndex,
    std::vector<std::vector<MString>> &out_cameraLensNodeNames,
    std::vector<MString> &out_lensNodeNamesVec,
    std::unordered_map<std::string, std::shared_ptr<LensModel>> &out_lensNodeNameToLensModel)
{
    MStatus status = MS::kSuccess;

    const MString inputAttrName = "inLens";
    const MString outputAttrName = "outLens";
    const MString enableAttrName = "enable";

    auto num_cameras = cameraList.size();
    for (uint32_t i = 0; i < num_cameras; i++) {
        auto camera = cameraList[i];

        MString cameraShapeName = camera->getShapeNodeName();
        std::string cameraShapeNameStr(cameraShapeName.asChar());
        out_cameraNodeNameToCameraIndex.insert({cameraShapeNameStr, i});

        MObject camera_shape_node_object = camera->getShapeObject();
        MObject node_object;

        // Get connected 'mmLensModeToggle' node (or whatever node is
        // connected) and ensure the node is active. If the node is
        // not active, the camera doesn't have any lens distortion and
        // can be ignored.
        status = getConnectedLensNode(
            camera_shape_node_object,
            outputAttrName,
            node_object);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        bool lens_toggle_enabled = false;
        status = getNodeEnabledState(
            node_object,
            enableAttrName,
            lens_toggle_enabled);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        if (!lens_toggle_enabled) {
            // The 'mmLensModeToggle' node will disable all downstream
            // lens nodes, so we can skip them.
            std::vector<MString> lensNodeNames;
            out_cameraLensNodeNames.push_back(lensNodeNames);
            continue;
        }

        status = getConnectedLensNode(
            camera_shape_node_object,
            inputAttrName,
            node_object);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        std::vector<MString> lensNodeNames;
        for (uint32_t node_depth = 0; !node_object.isNull(); ++node_depth) {
            bool lens_model_enabled = false;
            status = getNodeEnabledState(
                node_object,
                enableAttrName,
                lens_model_enabled);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            if (lens_model_enabled) {
                MString lensNodeName;
                status = getUniqueNodeName(node_object, lensNodeName);
                CHECK_MSTATUS_AND_RETURN_IT(status);
                std::string lensNodeNameStr(lensNodeName.asChar());

                lensNodeNames.push_back(lensNodeName);

                bool found = std::find(
                    out_lensNodeNamesVec.cbegin(),
                    out_lensNodeNamesVec.cend(),
                    lensNodeName) != out_lensNodeNamesVec.cend();
                if (!found) {
                    out_lensNodeNamesVec.push_back(lensNodeName);
                }

                auto search = out_lensNodeNameToLensModel.find(lensNodeNameStr);
                if (search == out_lensNodeNameToLensModel.end()) {
                    MFnDependencyNode mfnDependNode(node_object, &status);
                    CHECK_MSTATUS_AND_RETURN_IT(status);

                    const bool wantNetworkedPlug = true;
                    MPlug outputPlug = mfnDependNode.findPlug(outputAttrName, wantNetworkedPlug, &status);
                    if (status != MS::kSuccess) {
                        // The camera may not have an 'outLens' attribute and may
                        // not have a lens node connected to it.
                        status = MS::kSuccess;
                        continue;
                    }

                    std::shared_ptr<LensModel> lensModel;
                    status = getLensModelFromPlug(outputPlug, lensModel);
                    if (status != MS::kSuccess) {
                        continue;
                    }

                    out_lensNodeNameToLensModel.insert({lensNodeNameStr, lensModel});
                }
            }

            MObject upstream_node;
            status = getConnectedLensNode(
                node_object,
                inputAttrName,
                upstream_node);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            if (upstream_node.isNull()) {
                // There is nothing upstream anymore.
                node_object = MObject();
                continue;
            }
            node_object = upstream_node;
        }
        out_cameraLensNodeNames.push_back(lensNodeNames);
    }
    assert(out_cameraLensNodeNames.size() == num_cameras);

    return status;
}

MStatus getAttrsFromLensNode(
    const MObject &node,
    const MString &nodeName,
    std::vector<Attr> &out_attrs
) {
    MStatus status = MS::kSuccess;
    out_attrs.clear();

    MFnDependencyNode mfn_depend_node(node, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    const MString enableAttrName = "enable";

    bool nodeEnabled = false;
    status = getNodeEnabledState(
        node,
        enableAttrName,
        nodeEnabled);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    if (!nodeEnabled) {
        return status;
    }

    MString nodeTypeName = mfn_depend_node.typeName(&status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    MStringArray attrNames;
    if (nodeTypeName.asChar() == "mmLensModel3de") {
        // TODO: Should the 'lensModel' enum be queried and only the
        //  needed lensModel attributes appended?
        attrNames.append("tdeClassic_distortion");
        attrNames.append("tdeClassic_anamorphicSqueeze");
        attrNames.append("tdeClassic_curvatureX");
        attrNames.append("tdeClassic_curvatureY");
        attrNames.append("tdeClassic_quarticDistortion");

        attrNames.append("tdeRadialDeg4_degree2_distortion");
        attrNames.append("tdeRadialDeg4_degree2_u");
        attrNames.append("tdeRadialDeg4_degree2_v");
        attrNames.append("tdeRadialDeg4_degree4_distortion");
        attrNames.append("tdeRadialDeg4_degree4_u");
        attrNames.append("tdeRadialDeg4_degree4_v");
        attrNames.append("tdeRadialDeg4_cylindricDirection");
        attrNames.append("tdeRadialDeg4_cylindricBending");

        attrNames.append("tdeAnamorphicDeg4_degree2_cx02");
        attrNames.append("tdeAnamorphicDeg4_degree2_cy02");
        attrNames.append("tdeAnamorphicDeg4_degree2_cx22");
        attrNames.append("tdeAnamorphicDeg4_degree2_cy22");
        attrNames.append("tdeAnamorphicDeg4_degree4_cx04");
        attrNames.append("tdeAnamorphicDeg4_degree4_cy04");
        attrNames.append("tdeAnamorphicDeg4_degree4_cx24");
        attrNames.append("tdeAnamorphicDeg4_degree4_cy24");
        attrNames.append("tdeAnamorphicDeg4_degree4_cx44");
        attrNames.append("tdeAnamorphicDeg4_degree4_cy44");
        attrNames.append("tdeAnamorphicDeg4_lensRotation");
        attrNames.append("tdeAnamorphicDeg4_squeeze_x");
        attrNames.append("tdeAnamorphicDeg4_squeeze_y");
    }

    for (auto i = 0; i < attrNames.length(); ++i) {
        Attr attr = Attr();
        attr.setNodeName(nodeName);
        attr.setAttrName(attrNames[i]);
        out_attrs.push_back(attr);
    }

    return status;
}

// NOTE: The same lens node may be connected to multiple camera nodes
// and be 'shared' across cameras. In such a case, when an attribute
// on a single lens node is adjusted, the lens distortion should
// change for all connected cameras.
MStatus constructLenses(
    const std::vector<MString> &lensNodeNames,
    const CameraPtrList &cameraList,
    const MTimeArray &frameList,
    const std::vector<std::vector<MString>> &cameraLensNodeNames,
    const std::unordered_map<std::string, std::shared_ptr<LensModel>> &lensNodeNameToLensModel,
    std::unordered_map<std::string, uint32_t> &out_lensNodeNameToLensModelIndex,
    std::vector<std::shared_ptr<LensModel>> &out_lensModelList)
{
    MStatus status = MS::kSuccess;

    auto num_cameras = cameraList.size();
    auto num_frames = frameList.length();
    out_lensModelList.clear();

    // Loop over all Lenses (including the "input" Lenses) and query
    // the attribute values per-frame.
    for (uint32_t i = 0; i < lensNodeNames.size(); i++) {
        MString lensNodeName = lensNodeNames[i];
        std::string lensNodeNameStr(lensNodeName.asChar());

        MObject node;
        status = getAsObject(lensNodeName, node);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        if (node.isNull()) {
            MMSOLVER_ERR(
                "Node name "
                << "\"" << lensNodeNameStr << "\""
                " is not valid, skipping.");
            continue;
        }

        auto search = lensNodeNameToLensModel.find(lensNodeNameStr);
        if (search == lensNodeNameToLensModel.end()) {
            MMSOLVER_ERR(
                "Lens node name "
                << "\"" << lensNodeNameStr << "\""
                << " does not have a LensModel object, this should not happen. ");
            continue;
        }
        std::shared_ptr<LensModel> lensModel = search->second;

        auto lensIndex = static_cast<int32_t>(out_lensModelList.size());
        out_lensNodeNameToLensModelIndex.insert({lensNodeNameStr, lensIndex});

        // Fill out_lensModelList.
        for (uint32_t j = 0; j < num_frames; j++) {
            std::shared_ptr<LensModel> lensModelClone = lensModel->cloneAsSharedPtr();
            out_lensModelList.push_back(lensModelClone);
        }

        // Determine what type of lens node we have and find plugs on
        // the lens node.
        std::vector<Attr> lensAttrs;
        status = getAttrsFromLensNode(node, lensNodeName, lensAttrs);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        auto num_lens_attrs = lensAttrs.size();

        for (uint32_t j = 0; j < num_frames; j++) {
            auto lensFrameIndex = lensIndex + j;
            std::shared_ptr<LensModel> lensModel = out_lensModelList[lensFrameIndex];
            if (!lensModel) {
                continue;
            }

            const MTime frame = frameList[j];
            for (uint32_t k = 0; k < num_lens_attrs; k++) {
                // Query values from attrs
                double value = 0.0;
                const auto timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;
                status = lensAttrs[k].getValue(value, frame, timeEvalMode);
                CHECK_MSTATUS_AND_RETURN_IT(status);
                const auto solverAttrType = lensAttrs[k].getSolverAttrType();

                // Set attribute on the LensModel object.
                status = setLensModelAttributeValue(
                    lensModel,
                    solverAttrType,
                    value);
                CHECK_MSTATUS_AND_RETURN_IT(status);
            }
        }
    }

    return status;
}

// Connect up the lenses, in reverse connection order (last to first).
MStatus connectLensModels(
    const std::vector<MString> &lensNodeNames,
    const MTimeArray &frameList,
    const std::vector<std::vector<MString>> &cameraLensNodeNames,
    const std::unordered_map<std::string, uint32_t> &lensNodeNameToLensModelIndex,
    std::vector<std::shared_ptr<LensModel>> &inout_lensModelList)
{
    MStatus status = MS::kSuccess;

    auto num_frames = frameList.length();

    for (uint32_t i = 0; i < cameraLensNodeNames.size(); ++i) {
        std::vector<std::shared_ptr<LensModel>> previousLensModels;
        previousLensModels.resize(num_frames);

        std::vector<MString> lensNodeNames = cameraLensNodeNames[i];
        for (uint32_t j = lensNodeNames.size(); j < 0; --j) {
            MString lensNodeName = lensNodeNames[j];
            std::string lensNodeNameStr = lensNodeName.asChar();

            auto search = lensNodeNameToLensModelIndex.find(lensNodeNameStr);
            if (search != lensNodeNameToLensModelIndex.end()) {
                auto lensIndex = search->second;

                for (uint32_t j = 0; j < num_frames; j++) {
                    std::shared_ptr<LensModel> previousLensModel = previousLensModels[j];

                    auto lensFrameIndex = lensIndex + j;
                    std::shared_ptr<LensModel> lensModel = inout_lensModelList[lensFrameIndex];
                    lensModel->setInputLensModel(previousLensModel);

                    previousLensModels[j] = lensModel;
                }
            }
        }
    }

    return status;
}

// Marker to LensModel data structure.
MStatus constructMarkerToLensModelMap(
    const MarkerPtrList &markerList,
    const MTimeArray &frameList,
    const std::unordered_map<std::string, int32_t> &cameraNodeNameToCameraIndex,
    const std::vector<std::vector<MString>> &cameraLensNodeNames,
    const std::unordered_map<std::string, uint32_t> &lensNodeNameToLensModelIndex,
    const std::vector<std::shared_ptr<LensModel>> &lensModelList,
    std::vector<std::shared_ptr<LensModel>> &out_markerFrameToLensModelList)
{
    MStatus status = MS::kSuccess;

    auto num_markers = markerList.size();
    auto num_frames = frameList.length();
    out_markerFrameToLensModelList.clear();
    out_markerFrameToLensModelList.resize(num_markers * num_frames);

    for (uint32_t i = 0; i < num_markers; ++i) {
        MarkerPtr marker = markerList[i];
        CameraPtr camera = marker->getCamera();

        MString cameraShapeName = camera->getShapeNodeName();
        std::string cameraShapeNameStr(cameraShapeName.asChar());
        auto search = cameraNodeNameToCameraIndex.find(cameraShapeNameStr);
        if (search == cameraNodeNameToCameraIndex.end()) {
            // This should not happen as long as the cameras all have
            // shape node names (which is expected to always be true).
            MMSOLVER_ERR(
                "Camera node name \"" << cameraShapeName
                << "\" not found in camera names lookup map, cannot continue!"
            );
            status = MS::kFailure;
            CHECK_MSTATUS_AND_RETURN_IT(status);
        }
        auto cameraIndex = search->second;

        std::vector<MString> lensNodeNames = cameraLensNodeNames[cameraIndex];
        if (lensNodeNames.size() == 0) {
            // No Lens distortion.
            std::shared_ptr<LensModel> lensModel;
            for (uint32_t j = 0; j < num_frames; j++) {
                auto markerFrameIndex = (i * num_frames) + j;
                out_markerFrameToLensModelList[markerFrameIndex] = lensModel;
            }
        } else {
            MString lensNodeName = lensNodeNames[0];
            std::string lensNodeNameStr(lensNodeName.asChar());

            auto search = lensNodeNameToLensModelIndex.find(lensNodeNameStr);
            if (search != lensNodeNameToLensModelIndex.end()) {
                auto lensIndex = search->second;

                for (uint32_t j = 0; j < num_frames; j++) {
                    auto markerFrameIndex = (i * num_frames) + j;
                    auto lensFrameIndex = lensIndex + j;
                    std::shared_ptr<LensModel> lensModel = lensModelList[lensFrameIndex];
                    out_markerFrameToLensModelList[markerFrameIndex] = lensModel;
                }
            }
        }
    }

    return status;
}

// Create a mapping data structure between Attribute (index) and the
// corresponding Lens (index).
MStatus constructAttributeToLensModelMap(
    const AttrPtrList &attrList,
    const MTimeArray &frameList,
    const std::unordered_map<std::string, uint32_t> &lensNodeNameToLensModelIndex,
    const std::vector<std::shared_ptr<LensModel>> &lensModelList,
    std::vector<std::shared_ptr<LensModel>> &out_attrFrameToLensModelList)
{
    MStatus status = MS::kSuccess;

    auto num_attrs = attrList.size();
    auto num_frames = frameList.length();
    out_attrFrameToLensModelList.clear();
    out_attrFrameToLensModelList.resize(num_attrs * num_frames);

    for (uint32_t i = 0; i < num_attrs; ++i) {
        AttrPtr attr = attrList[i];

        const auto object_type = attr->getObjectType();
        if (object_type != ObjectType::kLens) {
            continue;
        }

        MString nodeName = attr->getNodeName();
        std::string nodeNameStr(nodeName.asChar());

        auto search = lensNodeNameToLensModelIndex.find(nodeNameStr);
        if (search == lensNodeNameToLensModelIndex.end()) {
            MMSOLVER_WRN(
                "Lens node name \"" << nodeName
                << "\" not found in lens names lookup map, lens node will be ignored!"
            );
            continue;
        }
        auto lensIndex = search->second;

        for (uint32_t j = 0; j < num_frames; j++) {
            auto attrFrameIndex = (i * num_frames) + j;
            auto lensFrameIndex = lensIndex + j;
            auto lensModel = lensModelList[lensFrameIndex];
            out_attrFrameToLensModelList[attrFrameIndex] = lensModel;
        }
    }

    return status;
}

// Construct the data structures that will be re-used in the
// 'measureErrors*' and 'setParameters*' functions.
MStatus
constructLensModelList(
        const CameraPtrList &cameraList,
        const MarkerPtrList &markerList,
        const AttrPtrList &attrList,
        const MTimeArray &frameList,
        // TODO: Can we reduce the indirection by one level and store the direct pointer?
        //  If so, we must ensure out_lensList is not destroyed until we are finished solving.
        std::vector<std::shared_ptr<LensModel>> &out_markerFrameToLensModelList,
        std::vector<std::shared_ptr<LensModel>> &out_attrFrameToLensModelList,
        std::vector<std::shared_ptr<LensModel>> &out_lensModelList
) {
    MStatus status = MS::kSuccess;

    std::unordered_map<std::string, int32_t> cameraNodeNameToCameraIndex;
    std::vector<std::vector<MString>> cameraLensNodeNames;
    std::vector<MString> lensNodeNamesVec;
    std::unordered_map<std::string, std::shared_ptr<LensModel>> lensNodeNameToLensModel;
    status = getLensesFromCameraList(
            cameraList,
        cameraNodeNameToCameraIndex,
        cameraLensNodeNames,
        lensNodeNamesVec,
        lensNodeNameToLensModel);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    std::unordered_map<std::string, uint32_t> lensNodeNameToLensModelIndex;
    status = constructLenses(
        lensNodeNamesVec,
        cameraList,
        frameList,
        cameraLensNodeNames,
        lensNodeNameToLensModel,
        lensNodeNameToLensModelIndex,
        out_lensModelList);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = connectLensModels(
        lensNodeNamesVec,
        frameList,
        cameraLensNodeNames,
        lensNodeNameToLensModelIndex,
        out_lensModelList);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = constructMarkerToLensModelMap(
        markerList,
        frameList,
        cameraNodeNameToCameraIndex,
        cameraLensNodeNames,
        lensNodeNameToLensModelIndex,
        out_lensModelList,
        out_markerFrameToLensModelList);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = constructAttributeToLensModelMap(
        attrList,
        frameList,
        lensNodeNameToLensModelIndex,
        out_lensModelList,
        out_attrFrameToLensModelList);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    return status;
}
