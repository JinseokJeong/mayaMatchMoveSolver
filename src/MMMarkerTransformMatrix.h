/*
 * Copyright (C) 2018, 2019, 2020 David Cattermole.
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
 * A transform node that can have translate values offset with lens
 * distortion models.
 */

#include <maya/MMatrix.h>
#include <maya/MPxTransform.h>
#include <maya/MPxTransformationMatrix.h>

#include <core/lensModel.h>


class MMMarkerTransformMatrix : public MPxTransformationMatrix {
public:
    MMMarkerTransformMatrix();
    static void *creator();

    virtual MMatrix asMatrix() const;
    virtual MMatrix asMatrix(double percent) const;
    
    LensModel* getLensModel() const;
    void setLensModel(LensModel* value);

    static MTypeId m_id;

protected:
    typedef MPxTransformationMatrix ParentClass;

    LensModel* m_value;
};
