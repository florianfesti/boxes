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


class EggBot(Boxes):
    """DESCRIPTION"""

    ui_group = "Misc"

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, finger=3.0,space=3.0)
        self.addSettingsArgs(edges.StackableSettings, holedistance=5)
        # self.addSettingsArgs(edges.HingeSettings)

        # Add non default cli params if needed (see argparse std lib)
        self.argparser.add_argument(
            "--diameter",  action="store", type=float, default=125.0,
            help="Maximal Diameter object being drawn on")

    def render(self):
        # adjust to the variables you want in the local scope
        t = self.thickness
        d = self.diameter

        l = d + 30 + 50
        w = d/2 + 30

        self.rectangularWall(l, t, "seee", label="front", move="up")
        self.rectangularWall(l, w, "ffff", label="top", move="up")
        self.rectangularWall(l, d/2+20, "seef", label="back", move="up")
        self.rectangularWall(
            w, d/2 + 20, "sheE",
            callback=[lambda:self.stepper_28byj_48(front=False, x=25, y=d/2+3*t)],
            label="left", move="up")
        self.rectangularWall(w, 0, "sEeE", label="right", move="up")
