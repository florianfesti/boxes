# Copyright (C) 2013-2020 Florian Festi
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
from boxes.generators.console2 import Console2

class SideDoorHousing(Console2):
    """A box with service hatches at the sides"""

    ui_group = "Box"

    description = """
This box is designed as a housing for electronic projects. It has hatches that can be re-opened with simple tools. It intentionally cannot be opened with bare hands - if build with thin enough material. The hatches are at the x sides.

#### Assembly instructions
The main body is easy to assemble by starting with the floor and then adding the four walls and the top piece.

For the removable walls you need to add the lips and latches. The U-shaped clamps holding the latches in place need to be clued in place without also gluing the latches themselves. Make sure the springs on the latches point inwards and the angled ends point to the side walls as shown here (showing a different box type):

![Wall details](static/samples/Console2-backwall-detail.jpg)

#### Re-Opening

The latches lock in place when closed. To open them they need to be pressed in and can then be moved aside.
"""

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=.5)
        self.addSettingsArgs(edges.StackableSettings)

        self.buildArgParser(x=100, y=100, h=100, bottom_edge="s")
        self.argparser.add_argument(
            "--double_door",  action="store", type=boolarg, default=True,
            help="allow removing the backwall, too")

        
    def render(self):
        x, y, h = self.x, self.y, self.h
        t = self.thickness
        bottom = self.edges.get(self.bottom_edge)

        self.latchpos = latchpos = 3*t


        self.rectangularWall(x, y, "ffff", move="right") # floor
        if self.double_door: # top
            self.rectangularWall(x, y, "EFEF", move="right")
        else:
            self.rectangularWall(x, y, "EFFF", move="right")

        for move in ("right", "mirror right"):
            re = edges.CompoundEdge(self, ("f", "e"),
                                    (bottom.endwidth()+t, h-t))
            if self.double_door:
                le = edges.CompoundEdge(self, ("e", "f"),
                                        (h-t, bottom.endwidth()+t))
            else:
                le = "f"
            self.rectangularWall( # side
                y, h, (bottom, re, "f", le), ignore_widths=[1, 6],
                callback=[
                    None, None, lambda:
                    (self.rectangularHole(1.55*t, latchpos, 1.1*t, 1.1*t),
                     self.double_door and
                     self.rectangularHole(y-1.55*t, latchpos, 1.1*t, 1.1*t))],
                move=move)

            
        for i in range(2 if self.double_door else 1):
            self.rectangularWall(x, t, (bottom, "F", "e", "F"),
                                 ignore_widths=[1, 6], move="up")
            self.rectangularWall( # back wall
                x, h-1.1*t, "eEeE",
                callback=[
                    lambda: self.fingerHolesAt(.5*t, 0, h-4.05*t-latchpos),
                    lambda:self.latch_hole(h-1.2*t-latchpos),
                    lambda: self.fingerHolesAt(.5*t, 3.05*t+latchpos, h-4.05*t-latchpos),
                    lambda:self.latch_hole(latchpos)],
                move="right")
            self.rectangularWall(x, t, (bottom, "F", "e", "F"),
                                 ignore_widths=[1, 6], move="down only")
        if not self.double_door:
            self.rectangularWall(x, h, (bottom, "F", "f", "F"),
                                 ignore_widths=[1, 6], move="right")

        # hardware for back wall
        if self.double_door:
            latches = 4
        else:
            latches = 2

        self.partsMatrix(latches, 0, "right",
                         self.rectangularWall, 2*t, h-4.05*t-latchpos, "EeEf")
        self.partsMatrix(latches, 2, "up", self.latch)
        self.partsMatrix(2*latches, 2, "up", self.latch_clamp)
