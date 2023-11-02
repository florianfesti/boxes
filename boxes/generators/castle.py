# Copyright (C) 2013-2014 Florian Festi
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


class Castle(Boxes):
    """Castle tower with two walls"""

    description = """This was done as a table decoration. May be at some point in the future someone will create a proper castle
with towers and gates and walls that can be attached in multiple configurations."""
    ui_group = "Unstable"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)

    def render(self, t_x=70, t_h=250, w1_x=300, w1_h=120, w2_x=100, w2_h=120):
        s = edges.FingerJointSettings(10.0, relative=True,
                                      space=1, finger=1,
                                      width=self.thickness)

        s.edgeObjects(self, "pPQ")

        self.moveTo(0, 0)
        self.rectangularWall(t_x, t_h, edges="efPf", move="right", callback=[lambda: self.fingerHolesAt(t_x * 0.5, 0, w1_h, 90), ])
        self.rectangularWall(t_x, t_h, edges="efPf", move="right")
        self.rectangularWall(t_x, t_h, edges="eFPF", move="right", callback=[lambda: self.fingerHolesAt(t_x * 0.5, 0, w2_h, 90), ])
        self.rectangularWall(t_x, t_h, edges="eFPF", move="right")

        self.rectangularWall(w1_x, w1_h, "efpe", move="right")
        self.rectangularWall(w2_x, w2_h, "efpe", move="right")



