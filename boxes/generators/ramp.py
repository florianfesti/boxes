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
    """Ramp for accessibility purposes"""

    ui_group = "Misc"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)

        self.argparser.add_argument(
            "--x",
            action="store",
            type=float,
            default=100.,
            help="width of the ramp in mm, generally the width of the step the ramp is built for"
        )
        self.argparser.add_argument(
            "--y",
            action="store",
            type=float,
            default=100.,
            help="height of the ramp in mm"
        )
        self.argparser.add_argument(
            "--h",
            action="store",
            type=float,
            default=100.,
            help="depth of the ramp in mm, will influence the steepness of the ramp"
        )
        self.argparser.add_argument(
            "--n",
            action="store",
            type=int,
            default=0,
            help="Number of reinforcement triangle inside"
        )

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

        a = math.atan(h/y)
        # Calculating triangle part dimensions:
        tx = y - t - t * math.sin(a) - 2*t / math.tan(a)
        ty = tx * math.tan(a)
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
