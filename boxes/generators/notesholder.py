#!/usr/bin/env python3
# Copyright (C) 2013-2019 Florian Festi
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
from boxes.edges import Edge

class USlotEdge(Edge):

    def __call__(self, length, bedBolts=None, bedBoltSettings=None, **kw):
        l = length
        d = self.settings
        r = min(d/2., l/12.)
        poly = [l*4/12.-r, (90, r), d-2*r, (-90, r), l/6.-r]
        poly = poly + [0] + list(reversed(poly))
        self.polyline(*poly)

class NotesHolder(Boxes):
    """Box for holding a stack of paper, coasters etc"""

    ui_group = "Box"

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.StackableSettings)
        self.buildArgParser("x", "y", "h", "bottom_edge")
        self.argparser.add_argument(
            "--slots",  action="store", type=str, default="one",
            choices=("one", "two", "four"),
            help="slots for grabbing the notes")

    def render(self):
        x, y, h = self.x, self.y, self.h
        t = self.thickness

        t1 = USlotEdge(self, h)
        t2 = t3 = t4 = "e"
        if self.slots != "one":
            t3 = t1
        if self.slots == "four":
            t2 = t4 = t1

        b = self.edges.get(self.bottom_edge, self.edges["F"])

        with self.saved_context():
            self.rectangularWall(x, h, [b, "F", t1, "F"], move="up")
            self.rectangularWall(x, h, [b, "F", t3, "F"], move="up")

            if self.bottom_edge != "e":
                self.rectangularWall(x, y, "ffff", move="up")

        self.rectangularWall(x, h, [b, "F", t3, "F"], move="right only")
        self.rectangularWall(y, h, [b, "f", t2, "f"], move="up")
        self.rectangularWall(y, h, [b, "f", t4, "f"], move="up")


