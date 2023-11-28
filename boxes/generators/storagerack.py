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

class StorageRack(Boxes):
    """StorageRack to store boxes and trays which have their own floor"""

    ui_group = "Shelf"

    description = """

Drawers are not included:

![Inside](static/samples/StorageRack-2.jpg)
![Back wall details](static/samples/StorageRack-3.jpg)

"""

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.StackableSettings)
        
        self.argparser.add_argument(
            "--depth",  action="store", type=float, default=200,
            help="depth of the rack")
        self.argparser.add_argument(
            "--rail",  action="store", type=float, default=30,
            help="depth of the rack")
        self.buildArgParser("x", "sh", "outside", "bottom_edge")
        self.argparser.add_argument(
            "--top_edge", action="store",
            type=ArgparseEdgeType("FheSŠ"), choices=list("FheSŠ"),
            default="F",
            help="edge type for top edge")

    def hHoles(self):
        posh = -0.5 * self.thickness
        for h in self.sh[:-1]:
            posh += h + self.thickness
            self.fingerHolesAt(posh, 0, self.depth)

    def backHoles(self):
        posh = -0.5 * self.thickness
        for nr, h in enumerate(self.sh[:-1]):
            posh += h + self.thickness
            if ((self.bottom_edge == "e" and nr == 0) or
                (self.top_edge == "e" and nr == len(self.sh) - 2)): 
                self.fingerHolesAt(0, posh, self.x, 0)
            else:
                self.fingerHolesAt(0, posh, self.rail, 0)
                self.fingerHolesAt(self.x, posh, self.rail, 180)

    def render(self):
        if self.outside:
            self.depth = self.adjustSize(self.depth, e2=False)
            self.sh = self.adjustSize(self.sh, self.top_edge, self.bottom_edge)
            self.x = self.adjustSize(self.x)

        h = sum(self.sh) + self.thickness * (len(self.sh) - 1)
        x = self.x
        d = self.depth
        t = self.thickness


        # outer walls
        b = self.bottom_edge
        t = self.top_edge
        self.closedtop = self.top_edge in "fFhŠ"

        # sides

        self.ctx.save()

        # side walls
        self.rectangularWall(d, h, [b, "F", t, "E"], callback=[None, self.hHoles, ], move="up")
        self.rectangularWall(d, h, [b, "E", t, "F"], callback=[None, self.hHoles, ], move="up")

        # full floors
        self.rectangularWall(d, x, "fffE", move="up")
        self.rectangularWall(d, x, "fffE", move="up")

        num = len(self.sh)-1
        if b == "e":
            num -= 1
        if t == "e":
            num -= 1
            
        for i in range(num):
            self.rectangularWall(d, self.rail, "ffee", move="up")
            self.rectangularWall(d, self.rail, "feef", move="up")

        self.ctx.restore()
        self.rectangularWall(d, h, "ffff", move="right only")

        # back wall
        self.rectangularWall(x, h, [b, "f", t, "f"],  callback=[self.backHoles], move="up")
