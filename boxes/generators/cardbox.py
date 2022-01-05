#!/usr/bin/env python3
# Copyright (C) 2013-2014 Florian Festi
# Copyright (C) 2018 jens persson <jens@persson.cx>
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

from boxes import edges, Boxes


class InsetEdgeSettings(edges.Settings):
    """Settings for InsetEdge"""
    absolute_params = {
        "thickness": 0,
    }


class InsetEdge(edges.BaseEdge):
    """An edge with space to slide in a lid"""
    def __call__(self, length, **kw):
        t = self.settings.thickness
        self.corner(90)
        self.edge(t, tabs=2)
        self.corner(-90)
        self.edge(length, tabs=2)
        self.corner(-90)
        self.edge(t, tabs=2)
        self.corner(90)


class FingerHoleEdgeSettings(edges.Settings):
    """Settings for FingerHoleEdge"""
    absolute_params = {
        "wallheight": 0,
    }


class FingerHoleEdge(edges.BaseEdge):
    """An edge with room to get your fingers around cards"""
    def __call__(self, length, **kw):
        depth = self.settings.wallheight-self.thickness-10
        self.edge(length/2-10, tabs=2)
        self.corner(90)
        self.edge(depth, tabs=2)
        self.corner(-180, 10)
        self.edge(depth, tabs=2)
        self.corner(90)
        self.edge(length/2-10, tabs=2)


class CardBox(Boxes):
    """Box for storage of playing cards"""
    ui_group = "Box"

    description = """
#### Building instructions

Place inner walls on floor first (if any). Then add the outer walls. Glue the two walls without finger joins to the inside of the side walls. Make sure there is no squeeze out on top, as this is going to form the rail for the lid.

Add the top of the rails to the sides and the grip rail to the lid.

Details of the lid and rails

![Details](static/samples/CardBox-detail.jpg)

Whole box (early version still missing grip rail on the lid):
"""

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser(h=30)
        self.argparser.add_argument(
            "--cardwidth",  action="store", type=float, default=65,
            help="Width of the cards")
        self.argparser.add_argument(
            "--cardheight",  action="store", type=float, default=90,
            help="Height of the cards")
        self.argparser.add_argument(
            "--num",  action="store", type=int, default=2,
            help="number of compartments")

    @property
    def boxwidth(self):
        return self.num * (self.cardwidth + self.thickness) + self.thickness

    def divider_bottom(self):
        t = self.thickness
        c = self.cardwidth
        y = self.cardheight

        for i in range(1, self.num):
            self.fingerHolesAt(0.5*t + (c+t)*i, 0, y, 90)

    def divider_back_and_front(self):
        t = self.thickness
        c = self.cardwidth
        y = self.h
        for i in range(1, self.num):
            self.fingerHolesAt(0.5*t + (c+t)*i, 0, y, 90)

    def render(self):
        h = self.h
        t = self.thickness

        x = self.boxwidth
        y = self.cardheight

        s = InsetEdgeSettings(thickness=t)
        p = InsetEdge(self, s)
        p.char = "a"
        self.addPart(p)

        s = FingerHoleEdgeSettings(thickness=t, wallheight=h)
        p = FingerHoleEdge(self, s)
        p.char = "A"
        self.addPart(p)

        with self.saved_context():
            self.rectangularWall(x-t*.2, y, "eeFe", move="right", label="Lid")
            self.rectangularWall(x, y, "ffff", callback=[self.divider_bottom],
                                 move="right", label="Bottom")
        self.rectangularWall(x, y, "eEEE", move="up only")
        self.rectangularWall(x-t*.2, t, "fEeE", move="up", label="Lid Lip")

        with self.saved_context():
            self.rectangularWall(x, h+t, "FFEF",
                                 callback=[self.divider_back_and_front],
                                 move="right",
                                 label="Back")
            self.rectangularWall(x, h+t, "FFaF",
                                 callback=[self.divider_back_and_front],
                                 move="right", 
                                 label="Front")
        self.rectangularWall(x, h+t, "EEEE", move="up only")


        with self.saved_context():
            self.rectangularWall(y, h+t, "FfFf", move="right", label="Outer Side Left")
            self.rectangularWall(y, h+t, "FfFf", move="right", label="Outer Side Right")
        self.rectangularWall(y, h+t, "fFfF", move="up only")

        with self.saved_context():
            self.rectangularWall(y, h, "Aeee", move="right", label="Inner Side Left")
            self.rectangularWall(y, h, "Aeee", move="right", label="Inner Side Right")
        self.rectangularWall(y, h, "eAee", move="up only")

        with self.saved_context():
            self.rectangularWall(y, t, "eefe", move="right", label="Lip Left")
            self.rectangularWall(y, t, "feee", move="right", label="Lip Right")
        self.rectangularWall(y, t*2, "efee", move="up only")

        for i in range(self.num - 1):
            self.rectangularWall(h, y, "fAff", move="right", label="Divider")

