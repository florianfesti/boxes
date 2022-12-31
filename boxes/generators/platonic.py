#!/usr/bin/env python3
# Copyright (C) 2020 Norbert Szulc
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
from boxes.edges import FingerJointEdge


class UnevenFingerJointEdge(FingerJointEdge):
    """Uneven finger joint edge """
    char = 'u'
    description = "Uneven Finger Joint"
    positive = True

    def __call__(self, length, bedBolts=None, bedBoltSettings=None, **kw):
        # copied from original

        positive = self.positive

        s, f, thickness = self.settings.space, self.settings.finger, self.settings.thickness

        p = 1 if positive else -1

        fingers, leftover = self.calcFingers(length, bedBolts)

        if not positive:
            play = self.settings.play
            f += play
            s -= play
            leftover -= play

        shift = (f + s) / 2 # we shift all fingers to make them un even
        if (leftover < shift): 
            leftover = shift

        self.edge((leftover + shift)/2, tabs=1)  # Whole point of this class

        l1,l2 = self.fingerLength(self.settings.angle)
        h = l1-l2

        d = (bedBoltSettings or self.bedBoltSettings)[0]

        for i in range(fingers):
            if i != 0:
                if not positive and bedBolts and bedBolts.drawBolt(i):
                    self.hole(0.5 * s,
                              0.5 * self.settings.thickness, 0.5 * d)

                if positive and bedBolts and bedBolts.drawBolt(i):
                    self.bedBoltHole(s, bedBoltSettings)
                else:
                    self.edge(s)

            if positive and self.settings.style == "springs":
                self.polyline(
                    0, -90 * p, 0.8*h, (90 * p, 0.2*h),
                    0.1 * h, 90, 0.9*h, -180, 0.9*h, 90,
                    f - 0.6*h,
                    90, 0.9*h, -180, 0.9*h, 90, 0.1*h,
                (90 * p, 0.2 *h), 0.8*h, -90 * p)
            else:
                self.polyline(0, -90 * p, h, 90 * p, f, 90 * p, h, -90 * p)

        self.edge((leftover - shift)/2, tabs=1)  # Whole point of this class

# Unstable
class UnevenFingerJointEdgeCounterPart(UnevenFingerJointEdge): 
    """Uneven finger joint edge - other side"""
    char = 'U'
    description = "Uneven Finger Joint (opposing side)"
    positive = False

class Platonic(Boxes):
    """Platonic solids generator"""

    ui_group = "Unstable" # see ./__init__.py for names
    description = """![Icosahedron](static/samples/Platonic-Icosahedron.jpg)
"""

    SOLIDS = {
        "tetrahedron": (4, 3),
        "cube": (6, 4),
        "octahedron": (8, 3),
        "dodecahedron": (12, 5),
        "icosahedro": (20, 3),
    }

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=0)

        self.buildArgParser(x=60, outside=True)  # x should be treated as edge length, TODO: change that
        self.argparser.add_argument(
            "--type",  action="store", type=str, default=list(self.SOLIDS)[0],
            choices=list(self.SOLIDS),
            help="type of platonic solid")


    def render(self):
        # adjust to the variables you want in the local scope
        e = self.x
        t = self.thickness
        faces, corners = self.SOLIDS[self.type]

        u = UnevenFingerJointEdge(self, self.edges["f"].settings)
        self.addPart(u)

        uc = UnevenFingerJointEdgeCounterPart(self, self.edges["f"].settings)
        self.addPart(uc)

        for _ in range(faces):
            self.regularPolygonWall(corners, side=e, edges="u", move="right")


