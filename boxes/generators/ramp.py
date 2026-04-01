# Copyright (C) 2013-2016 Florian Festi
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from boxes import *
from boxes.edges import CompoundEdge
from collections.abc import Callable

class Ramp(Boxes):
    """Ramp for accessibility purposes
    x is the width of the ramp, generally the width of the step the ramp is built for
    y is the length of the ramp, will influence the steepness of the ramp
    h is the height of the ramp.
    """

    ui_group = "Misc" # see ./__init__.py for names

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.argparser.add_argument(
            "--n",
            action="store",
            type=int,
            default=0,
            help="Number of reinforcement triangle inside"
        )

        # Uncomment the settings for the edge types you use
        # use keyword args to set default values
        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser(x=100, y=100, h=100)

    def fingerHolesCB(self, sections:list[float], height:float) -> Callable:

        def CB():
            posx = 0
            for x in sections:
                posx += x + self.thickness
                self.fingerHolesAt(posx, 0, height)

        return CB

    def render(self):
        # adjust to the variables you want in the local scope
        x, y, h = self.x, self.y, self.h
        n = self.n
        t = self.thickness

        # Calculating the angle of steepness, bit complicated due to material thickness.
        # Going with Newton-Raphson method

        def solve_angle_newton(H:float, L:float, T:float, a0_deg:float=45, tol:float=1e-8, max_iter:int=50) -> float:
            def f(a):
                return L * math.sin(a) - H * math.cos(a) + T * math.cos(2 * a)

            def df(a):
                return L * math.cos(a) + H * math.sin(a) - 2 * T * math.sin(2 * a)

            a = math.radians(a0_deg)

            for _ in range(max_iter):
                fa = f(a)
                dfa = df(a)

                if abs(dfa) < 1e-12:
                    raise RuntimeError("Derivative too small — Newton failed")

                a_new = a - fa / dfa

                if abs(a_new - a) < tol:
                    return a_new

                a = a_new

            raise RuntimeError("Newton method did not converge")
        try:
            a = solve_angle_newton(h, y, t)
        except RuntimeError:
            raise RuntimeError("Could not calculate the angle")

        # Calculating triangle part dimensions:
        tx = y - t - t * math.sin(a) - t / math.tan(a)
        ty = h - t - t * math.tan(a) - t * math.cos(a)
        tz = (tx**2+ty**2)**0.5

        self.edges["k"] = CompoundEdge(self, "EFE", [t / math.sin(a), tz, t / math.cos(a)])
        self.edges["K"] = CompoundEdge(self, "EFE", [t / math.cos(a), tz, t / math.sin(a)])
        # Drawing triangular sides
        self.rectangularTriangle(tx, ty, move="up", edges="fff", label=f"Side", num=2)

        # Drawing triangular reinforcement (inside)
        self.rectangularTriangle(tx, ty, move="up", edges="ffe", label=f"Inside", num=n)

        holes = [(x / (n + 1)) - t] * n

        # Rectangular parts of the prism are easier
        self.rectangularWall(x, ty, edges="FFeF", move="up", label="Vertical Wall", callback=[self.fingerHolesCB(holes, ty)])
        self.rectangularWall(x, tx, move="up", edges="eFfF", label="Bottom", callback=[self.fingerHolesCB(holes, tx)])

        self.rectangularWall(x, tz + t / math.sin(a) + t / math.cos(a), move="up", edges="eKek", label="Diagonal")
