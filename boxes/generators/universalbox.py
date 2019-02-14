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
        self.addTopEdgeSettings(roundedtriangle={"outset" : 1})
        self.addSettingsArgs(edges.FlexSettings)
        self.buildArgParser("top_edge", "bottom_edge", "x", "y", "h")
        self.argparser.add_argument(
            "--lid",  action="store", type=str, default="default (none)",
            choices=("default (none)", "chest", "flat"),
            help="additional lid (for straight top_edge only)")
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


        t1, t2, t3, t4 = self.topEdges(self.top_edge)
        b = self.edges.get(self.bottom_edge, self.edges["F"])

        d2 = Bolts(2)
        d3 = Bolts(3)

        d2 = d3 = None


        with self.saved_context():
            self.rectangularWall(x, h, [b, "F", t1, "F"],
                                 bedBolts=[d2], move="up")
            self.rectangularWall(x, h, [b, "F", t3, "F"],
                                 bedBolts=[d2], move="up")

            if self.bottom_edge != "e":
                self.rectangularWall(x, y, "ffff", bedBolts=[d2, d3, d2, d3], move="up")
            if self.top_edge in "fF":
                self.set_source_color(Color.RED)
                self.rectangularWall(x+4*t, y+4*t, callback=[
                    lambda:self.top_hole(x, y, self.top_edge)], move="up")
                self.set_source_color(Color.BLACK)
            self.drawAddOnLid(x, y, self.lid)

        self.rectangularWall(x, h, [b, "F", t3, "F"],
                             bedBolts=[d2], move="right only")
        self.rectangularWall(y, h, [b, "f", t2, "f"],
                             bedBolts=[d3], move="up")
        self.rectangularWall(y, h, [b, "f", t4, "f"],
                             bedBolts=[d3], move="up")


