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
from boxes.lids import _TopEdge
from boxes.walledges import _WallMountedBox

class WallTypeTray(_WallMountedBox, _TopEdge):
    """Type tray - allows only continuous walls"""

    def __init__(self) -> None:
        super().__init__()
        self.addSettingsArgs(edges.StackableSettings)
        self.buildArgParser("sx", "sy", "h", "hi", "outside", "bottom_edge")
        self.argparser.add_argument(
            "--back_height",  action="store", type=float, default=0.0,
            help="additional height of the back wall")
        self.argparser.add_argument(
            "--radius",  action="store", type=float, default=0.0,
            help="radius for strengthening walls with the hooks")
        

    def xSlots(self):
        posx = -0.5 * self.thickness
        for x in self.sx[:-1]:
            posx += x + self.thickness
            posy = 0
            for y in self.sy:
                self.fingerHolesAt(posx, posy, y)
                posy += y + self.thickness

    def ySlots(self):
        posy = -0.5 * self.thickness
        for y in self.sy[:-1]:
            posy += y + self.thickness
            posx = 0
            for x in reversed(self.sx):
                self.fingerHolesAt(posy, posx, x)
                posx += x + self.thickness

    def xHoles(self):
        posx = -0.5 * self.thickness
        for x in self.sx[:-1]:
            posx += x + self.thickness
            self.fingerHolesAt(posx, 0, self.hi)

    def yHoles(self):
        posy = -0.5 * self.thickness
        for y in self.sy[:-1]:
            posy += y + self.thickness
            self.fingerHolesAt(posy, 0, self.hi)

    def render(self):

        self.generateWallEdges()
        b = self.bottom_edge
        
        if self.outside:
            self.sx = self.adjustSize(self.sx)
            self.sy = self.adjustSize(self.sy)
            self.h = self.adjustSize(self.h, b, e2=False)
            if self.hi:
                self.hi = self.adjustSize(self.hi, b, e2=False)

        x = sum(self.sx) + self.thickness * (len(self.sx) - 1)
        y = sum(self.sy) + self.thickness * (len(self.sy) - 1)
        h = self.h
        bh = self.back_height
        sameh = not self.hi
        hi = self.hi = self.hi or h
        t = self.thickness


        # outer walls
        # x sides

        self.ctx.save()

        # outer walls
        self.rectangularWall(x, h, [b, "f", "e", "f"], callback=[self.xHoles],  move="up")
        self.rectangularWall(x, h+bh, [b, "C", "e", "c"], callback=[self.mirrorX(self.xHoles, x), ], move="up")

        # floor
        if b != "e":
            self.rectangularWall(x, y, "ffff", callback=[
                self.xSlots, self.ySlots], move="up")

        # Inner walls

        be = "f" if b != "e" else "e"

        for i in range(len(self.sy) - 1):
            e = [edges.SlottedEdge(self, self.sx, be), "f",
                 edges.SlottedEdge(self, self.sx[::-1], "e", slots=0.5 * hi), "f"]

            self.rectangularWall(x, hi, e, move="up")

        # y walls

        # outer walls
        self.trapezoidSideWall(y, h, h+bh, [b, "B", "e", "h"], radius=self.radius, callback=[self.yHoles, ], move="up")
        self.moveTo(0, 8)
        self.trapezoidSideWall(y, h+bh, h, [b, "h", "e", "b"], radius=self.radius, callback=[self.mirrorX(self.yHoles, y), ], move="up")
        self.moveTo(0, 8)

        # inner walls
        for i in range(len(self.sx) - 1):
            e = [edges.SlottedEdge(self, self.sy, be, slots=0.5 * hi),
                 "f", "e", "f"]
            self.rectangularWall(y, hi, e, move="up")




