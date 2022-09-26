#!/usr/bin/env python3
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

class StorageShelf(_TopEdge):
    """StorageShelf can be used to store Typetray"""

    ui_group = "Shelf"
    description = "This is a simple shelf box."

    def __init__(self):
        Boxes.__init__(self)
        self.addTopEdgeSettings(fingerjoint={"surroundingspaces": 0.5},
                                roundedtriangle={"outset" : 1})
        self.buildArgParser("x", "sy", "sh", "outside", "bottom_edge",
                            "top_edge")
        self.argparser.add_argument(
            "--retainer",  action="store", type=float, default=0.0,
            help="height of retaining wall at the front edges")
        self.argparser.add_argument(
            "--retainer_hole_edge",  action="store", type=boolarg, default=False,
            help="use finger hole edge for retainer walls")
        
        

    def ySlots(self):
        posy = -0.5 * self.thickness
        h = sum(self.sh) + self.thickness * (len(self.sh) - 1)
        for y in self.sy[:-1]:
            posy += y + self.thickness
            self.fingerHolesAt(posy, 0, h, 90)

    def hSlots(self):
        posh = -0.5 * self.thickness
        for h in self.sh[:-1]:
            posh += h + self.thickness
            posy = 0
            for y in reversed(self.sy):
                self.fingerHolesAt(posh, posy, y)
                posy += y + self.thickness

    def yHoles(self):
        posy = -0.5 * self.thickness
        for y in self.sy[:-1]:
            posy += y + self.thickness
            self.fingerHolesAt(posy, 0, self.x)

    def hHoles(self):
        posh = -0.5 * self.thickness
        for h in self.sh[:-1]:
            posh += h + self.thickness
            self.fingerHolesAt(posh, 0, self.x)

    def render(self):
        if self.outside:
            self.sy = self.adjustSize(self.sy)
            self.sh = self.adjustSize(self.sh, self.top_edge, self.bottom_edge)
            self.x = self.adjustSize(self.x, e2=False)

        y = sum(self.sy) + self.thickness * (len(self.sy) - 1)
        h = sum(self.sh) + self.thickness * (len(self.sh) - 1)
        x = self.x
        t = self.thickness


        # outer walls
        b = self.bottom_edge
        t1, t2, t3, t4 = self.topEdges(self.top_edge)
        #if top_edge is t put the handle on the x walls
        if(self.top_edge=='t'):
            t1,t2,t3,t4=(t2,t1,t4,t3)
        self.closedtop = self.top_edge in "fFhŠY"

        # x sides

        self.ctx.save()

        # outer walls
        # XXX retainer
        self.rectangularWall(x, h, [b, "F", t1, "e"], callback=[None, self.hHoles, ], move="up", label="left")
        self.rectangularWall(x, h, [b, "e", t3, "F"], callback=[None, self.hHoles, ], move="up", label="right")

        # floor
        if b != "e":
            e = "fffe"
            if self.retainer:
                e = "ffff"
            self.rectangularWall(x, y, e, callback=[None, self.yHoles], move="up", label="bottom")

        # inner walls

        be = "f" if b != "e" else "e"

        for i in range(len(self.sh) - 1):
            e = ["f", edges.SlottedEdge(self, self.sy[::-1], "f", slots=0.5 * x), "f", "e"]
            if self.retainer:
                e[3] = "f"

            self.rectangularWall(x, y, e, move="up", label="inner horizontal " + str(i+1))

        # top / lid
        if self.closedtop:
            e = "FFFe" if self.top_edge == "f" else "fffe"
            self.rectangularWall(x, y, e, callback=[None, self.yHoles, ], move="up", label="top")
        else:
            self.drawLid(x, y, self.top_edge)

        self.ctx.restore()
        self.rectangularWall(x, h, "ffff", move="right only", label="invisible")

        # y walls

        # outer walls
        self.rectangularWall(y, h, [b, "f", t2, "f"],  callback=[self.ySlots, self.hSlots,], move="up", label="back")

        # inner walls
        for i in range(len(self.sy) - 1):
            # XXX retainer
            e = [be, edges.SlottedEdge(self, self.sh, "e", slots=0.5 * x),
                 "e", "f"]
            if self.closedtop:
                e = [be, edges.SlottedEdge(self, self.sh, "e", slots=0.5 * x),"f", "f"]
            self.rectangularWall(x, h, e, move="up", label="inner vertical " + str(i+1))


        if self.retainer:
            for i in range(len(self.sh)):
                # XXX finger holes, F edges, left and right
                e = "FEeE"
                if self.retainer_hole_edge or (i == 0 and b == "h"):
                    e = "hEeE"
                self.rectangularWall(y, self.retainer, e, move="up", label="retainer " + str(i+1))
