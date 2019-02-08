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
        depth = self.settings.wallheight-self.thickness*2-10
        self.edge(length/2-10, tabs=2)
        self.corner(90)
        self.edge(depth, tabs=2)
        self.corner(-180, 10)
        self.edge(depth, tabs=2)
        self.corner(90)
        self.edge(length/2-10, tabs=2)


class CardBox(Boxes):
    """Box for storage of playingcards"""
    ui_group = "Box"

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
        y = self.h - self.thickness
        for i in range(1, self.num):
            self.fingerHolesAt(0.5*t + (c+t)*i, 0, y, 90)

    def render(self):
        self.open()
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
            # Lid
            self.rectangularWall(x-t*.2, y, "Feee", move="right")
            # Bottom
            self.rectangularWall(x, y, "ffff", callback=[self.divider_bottom],
                                 move="right")

        self.rectangularWall(x, y, "EEEE", move="up only")

        with self.saved_context():
            # Back
            self.rectangularWall(x, h, "FFEF",
                                 callback=[self.divider_back_and_front],
                                 move="right")
            # Front
            self.rectangularWall(x, h, "FFaF",
                                 callback=[self.divider_back_and_front],
                                 move="right")

        self.rectangularWall(x, h, "EEEE", move="up only")

        #lip of the lid
        self.rectangularWall(x-t*.2, t, "fEeE", move="up")

        # Outer sides
        self.rectangularWall(h, y, "fFfF", move="right")
        self.rectangularWall(h, y, "fFfF", move="right")

        # Inner sides
        self.rectangularWall(h-t, y, "eAee", move="right")
        self.rectangularWall(h-t, y, "eAee", move="right")

        # Lips
        self.rectangularWall(t, y, "eeef", move="right")
        self.rectangularWall(t, y, "efee", move="right")

        # Divider
        for i in range(self.num - 1):
            self.rectangularWall(h-t, y, "fAff", move="right")

