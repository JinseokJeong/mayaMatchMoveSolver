/*
 * Copyright (C) 2019 David Cattermole.
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
 * Header for mmReprojection Maya command.
 */

#ifndef MAYA_MM_REPROJECTION_CMD_H
#define MAYA_MM_REPROJECTION_CMD_H


// STL
#include <cmath>

// Maya
#include <maya/MGlobal.h>
#include <maya/MIOStream.h>

#include <maya/MPxCommand.h>
#include <maya/MArgList.h>
#include <maya/MArgDatabase.h>
#include <maya/MSyntax.h>

#include <maya/MSelectionList.h>
#include <maya/MTime.h>
#include <maya/MTimeArray.h>

// Internal Objects
#include <Camera.h>

// Command arguments and command name:

// Camera to reproject into.
#define CAMERA_FLAG            "-c"
#define CAMERA_FLAG_LONG       "-camera"

// Time
#define TIME_FLAG              "-t"
#define TIME_FLAG_LONG         "-time"

// Query as World Point?
#define WORLD_POINT_FLAG       "-wp"
#define WORLD_POINT_FLAG_LONG  "-asWorldPoint"

// Query as Normalized Coordinate?
#define NORM_COORD_FLAG       "-nc"
#define NORM_COORD_FLAG_LONG  "-asNormalizedCoordinate"


class MMReprojectionCmd : public MPxCommand {
public:

    MMReprojectionCmd() : m_nodeList(),
                          m_camera(),
                          m_timeList(),
                          m_asWorldPoint(false),
                          m_asNormalizedCoordinate(false) {};

    virtual ~MMReprojectionCmd();

    virtual bool hasSyntax() const;
    static MSyntax newSyntax();

    virtual MStatus doIt(const MArgList &args);

    virtual bool isUndoable() const;

    static void *creator();

    static MString cmdName();

private:
    MStatus parseArgs( const MArgList& args );

    MSelectionList m_nodeList;
    Camera m_camera;
    MTimeArray m_timeList;

    bool m_asWorldPoint;
    bool m_asNormalizedCoordinate;
};

#endif // MAYA_MM_REPROJECTION_CMD_H
