#!/usr/bin/env python3
# Copyright (C) 2013-2016 Florian Festi
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

class FrontEdge(edges.BaseEdge):
    """An edge with room to get your fingers around cards"""
    def __call__(self, length, **kw):
        depth = self.settings.y * 2 / 3
        t = self.settings.thickness
        r = min(depth-t, length/4)
        self.edge(length/4-t, tabs=2)
        self.corner(90, t)
        self.edge(depth-t-r, tabs=2)
        self.corner(-90, r)
        self.edge(length/2 - 2*r)
        self.corner(-90, r)
        self.edge(depth-t-r, tabs=2)
        self.corner(90, t)
        self.edge(length/4-t, tabs=2)


class Dispenser(Boxes):
    """Dispenser for stackable (flat) items of same size"""

    description = """Set *bottomheight* to 0 for a wall mounting variant.
Please add mounting holes yourself."""
    
    ui_group = "Misc"

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.StackableSettings)

        self.buildArgParser(x=100, y=100, h=100)

        self.argparser.add_argument(
            "--slotheight",  action="store", type=float, default=10.0,
            help="height of the dispenser slot / items (in mm)")
        self.argparser.add_argument(
            "--bottomheight",  action="store", type=float, default=0.0,
            help="height underneath the dispenser (in mm)")
        self.argparser.add_argument(
            "--sideedges",  action="store", type=ArgparseEdgeType("Fh"),
            choices=list("Fh"), default="F",
            help="edges used for holding the front panels and back")


    def render(self):
        x, y, h, hs = self.x, self.y, self.h, self.slotheight
        hb = self.bottomheight
        t = self.thickness

        se = self.sideedges
        fe = FrontEdge(self, self)

        hb = max(0, hb-self.edges["š"].spacing())
        th = h + (hb+t if hb else 0.0)
        hh = hb + 0.5*t

        with self.saved_context():
            self.rectangularWall(x, y, [fe, "f", "f", "f"],
                                 label="Floor", move="right")
            self.rectangularWall(x, y, "eeee", label="Lid bottom", move="right")
            self.rectangularWall(x, y, "EEEE", label="Lid top", move="right")


        self.rectangularWall(x, y, "ffff", move="up only")
            
        if hb:
            frontedge = edges.CompoundEdge(self, "Ef", (hb+t+hs, h-hs))
            self.rectangularWall(
                y, th, ("š", frontedge, "e", "f"), ignore_widths=[6],
                callback=[lambda:self.fingerHolesAt(0, hh, y, 0)],
                label="Left wall", move="right mirror")
            self.rectangularWall(
                x, th, ["š", se, "e", se], ignore_widths=[1, 6],
                callback=[lambda:self.fingerHolesAt(0, hh, x, 0)],
                label="Back wall", move="right")
            self.rectangularWall(
                y, th, ("š", frontedge, "e", "f"), ignore_widths=[6],
                callback=[lambda:self.fingerHolesAt(0, hh, y, 0)],
                label="Right wall", move="right")

        else:
            frontedge = edges.CompoundEdge(self, "Ef", (hs, h-hs))
            self.rectangularWall(
                y, th, ("h", frontedge, "e", "f"),
                label="Left wall", ignore_widths=[6], move="right mirror")
            self.rectangularWall(
                x, th, ["h", se, "e", se], ignore_widths=[1, 6],
                label="Back wall", move="right")
            self.rectangularWall(
                y, th, ("h", frontedge, "e", "f"),
                label="Right wall", ignore_widths=[6], move="right")

        self.rectangularWall(x/3, h-hs, "eee" + se,
                             label="Left front", move="right")
        self.rectangularWall(x/3, h-hs, "eee" + se,
                             label="Right front", move="mirror right")

