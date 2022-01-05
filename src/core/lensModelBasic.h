/*
 * Copyright (C) 2020 David Cattermole.
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
 * Fanctor class for the basic brownian lens distortion model.
 */

#ifndef MAYA_MM_SOLVER_CORE_LENS_MODEL_BASIC_H
#define MAYA_MM_SOLVER_CORE_LENS_MODEL_BASIC_H

#include <core/lensModel.h>

class LensModelBasic : public LensModel {
public:

    LensModelBasic() : m_k1(0.0), m_k2(0.0) {};

    LensModelBasic(double k1, double k2) : m_k1(k1), m_k2(k2) {};

    double getK1() const;

    void setK1(double value);

    double getK2() const;

    void setK2(double value);

    LensModel* getInputLensModel() const;

    void setInputLensModel(LensModel* value);

    virtual void applyModel(double x,
                            double y,
                            double &out_x,
                            double &out_y) const;

private:

    LensModel* m_inputLensModel;
    double m_k1;
    double m_k2;
};


#endif // MAYA_MM_SOLVER_CORE_LENS_MODEL_BASIC_H
