#!/usr/bin/env python3
# Copyright (C) 2013-2018 Florian Festi
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


class UnevenHeightBox(Boxes):
    """Box with different height in each corner"""

    ui_group = "Box"

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser("x", "y", "outside")
        self.argparser.add_argument(
            "--height0", action="store", type=float, default=50,
            help="height of the front left corner in mm")
        self.argparser.add_argument(
            "--height1", action="store", type=float, default=50,
            help="height of the front right corner in mm")
        self.argparser.add_argument(
            "--height2", action="store", type=float, default=100,
            help="height of the right back corner in mm")
        self.argparser.add_argument(
            "--height3", action="store", type=float, default=100,
            help="height of the left back corner in mm")

    def wall(self, w, h0, h1, edges="eee", move=None):

        edges = [self.edges.get(e, e) for e in edges]
        
        overallwidth = w + edges[-1].spacing() + edges[1].spacing()
        overallheight = max(h0, h1) + edges[0].spacing()

        if self.move(overallwidth, overallheight, move, before=True):
            return

        a = math.degrees(math.atan((h1-h0)/w))
        l = ((h0-h1)**2+w**2)**0.5

        self.moveTo(edges[-1].spacing(), edges[0].margin())
        edges[0](w)
        self.edgeCorner(edges[0], edges[1], 90)
        edges[1](h1)
        self.edgeCorner(edges[1], self.edges["e"], 90)
        self.polyline(0, a, l, -a)
        self.edgeCorner(self.edges["e"], edges[-1], 90)
        edges[-1](h0)
        self.edgeCorner(edges[-1], edges[0], 90)
        
        self.ctx.stroke()

        self.move(overallwidth, overallheight, move)


    def render(self):
        self.open()

        x, y = self.x, self.y
        heights = [self.height0, self.height1, self.height2, self.height3]

        if self.outside:
            x = self.adjustSize(x)
            y = self.adjustSize(y)
            for i in range(4):
                heights[i] = self.adjustSize(heights[i], None)

        t = self.thickness
        h0 , h1, h2 , h3 = heights

        self.wall(x, h0, h1, "FFF", move="right")
        self.wall(y, h1, h2, "Fff", move="right")
        self.wall(x, h2, h3, "FFF", move="right")
        self.wall(y, h3, h0, "Fff", move="right")

        self.rectangularWall(x, y, "ffff", move="right")

        self.close()


