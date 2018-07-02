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
from boxes.edges import Bolts
from boxes.lids import _TopEdge, _ChestLid

class UniversalBox(_TopEdge, _ChestLid):
    """Box with various options for different styles and lids"""

    ui_group = "Box"

    def __init__(self):
        Boxes.__init__(self)
        self.addTopEdgeSettings()
        self.addSettingsArgs(edges.FlexSettings)
        self.buildArgParser("top_edge", "bottom_edge", "x", "y", "h")
        self.argparser.add_argument(
            "--lid",  action="store", type=str, default="default (none)",
            choices=("default (none)", "chest", "flat"),
            help="additional lid")
        self.angle = 0

    def top_hole(self, x, y, top_edge):
        t = self.thickness

        if top_edge == "f":
            edge = self.edges["F"]
            self.moveTo(2*t+self.burn, 2*t, 90)
        elif top_edge == "F":
            edge = self.edges["f"]
            self.moveTo(t+self.burn, 2*t, 90)
        else:
            raise ValueError("Only f and F supported")

        for l in (y, x, y, x):
            edge(l)
            if top_edge == "F": self.edge(t)
            self.corner(-90)
            if top_edge == "F": self.edge(t)

    def render(self):
        x, y, h = self.x, self.y, self.h
        t = self.thickness

        self.open()

        t1, t2, t3, t4 = self.topEdges(self.top_edge)
        b = self.edges.get(self.bottom_edge, self.edges["F"])

        d2 = Bolts(2)
        d3 = Bolts(3)

        d2 = d3 = None

        self.rectangularWall(y, h, [b, "f", t2, "f"],
                             bedBolts=[d3], move="right")
        self.rectangularWall(x, h, [b, "F", t1, "F"],
                             bedBolts=[d2], move="up")
        self.rectangularWall(x, h, [b, "F", t3, "F"],
                             bedBolts=[d2])
        self.rectangularWall(y, h, [b, "f", t4, "f"],
                             bedBolts=[d3], move="left")
        self.rectangularWall(x, h, [b, "F", t3, "F"],
                             bedBolts=[d2], move="up only")

        self.rectangularWall(x, y, "ffff", bedBolts=[d2, d3, d2, d3], move="right")
        if self.drawLid(x, y, self.top_edge, [d2, d3]):
            self.rectangularWall(x, y, "ffff", move="left only")
        if self.top_edge in "fF":
            self.ctx.set_source_rgb(1., 0, 0)
            self.rectangularWall(x+4*t, y+4*t, callback=[
                lambda:self.top_hole(x, y, self.top_edge)], move="right")
            self.ctx.set_source_rgb(0, 0, 0)
        self.drawAddOnLid(x, y, self.lid)

        self.close()

