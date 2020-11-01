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
from boxes.edges import FingerJointBase, FingerJointEdge

from math import sin, pi

class UnevenJointBase(FingerJointBase):
    def calcFingers(self, length, bedBolts):
        space, finger = self.settings.space, self.settings.finger
        fingers = int((length - (self.settings.surroundingspaces - 1) * space) //
                      (space + finger))
        if not finger:
            fingers = 0
        if bedBolts:
            fingers = bedBolts.numFingers(fingers)
        leftover = length - fingers * (space + finger)  # we don't another space

        if fingers <= 0:
            fingers = 0
            leftover = length

        return fingers, leftover

class UnevenFingerJointEdge(FingerJointEdge, UnevenJointBase):
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

        self.edge(leftover, tabs=1)  # Whole point of this class

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

        self.edge(0, tabs=0)  # Whole point of this class

class UnevenFingerJointEdgeCounterPart(UnevenFingerJointEdge):
    """Uneven finger joint edge - other side"""
    char = 'U'
    description = "Uneven Finger Joint (opposing side)"
    positive = False

class Platonic(Boxes):
    """Platonic solids generator"""

    ui_group = "Unstable" # see ./__init__.py for names

    SOLIDS = {
        "Tetrahedron": (4, 3),
        "Cube": (6, 4),
        "Octahedron": (8, 3),
        "Dodecahedron": (12, 5),
        "Icosahedro": (20, 3),
    }

    def __init__(self):
        Boxes.__init__(self)

        # Uncomment the settings for the edge types you use
        # use keyword args to set default values
        self.addSettingsArgs(edges.FingerJointSettings)
        # self.addSettingsArgs(edges.StackableSettings)
        # self.addSettingsArgs(edges.HingeSettings)
        # self.addSettingsArgs(edges.LidSettings)
        # self.addSettingsArgs(edges.ClickSettings)
        # self.addSettingsArgs(edges.FlexSettings)

        # remove cli params you do not need
        self.buildArgParser(x=90, sx="3*50", y=100, sy="3*50", h=100, hi=0)
        # Add non default cli params if needed (see argparse std lib)
        self.argparser.add_argument(
            "--XX",  action="store", type=float, default=0.5,
            help="DESCRIPTION")


    def regularTrianagleWall(self, a, edges="uuuu", move=None):
        self.regularPolygonWall(3, side=a, edges=edges, move=move)



    def render(self):
        # adjust to the variables you want in the local scope
        x, y, h = self.x, self.y, self.h
        a = x  # side length
        t = self.thickness

        solid = "Octahedron"
        faces, corners = self.SOLIDS[solid]


        s = edges.FingerJointSettings(self.thickness, relative=True,
                                      width=self.thickness)
        
        #adjust surrounding spaces, to account for finger width at edge (?)
        # fix_r, fix_h, _ = self.regularPolygon(corners, side=1)
        cutin_fix = s.width/sin(2*pi/corners)/s.space
        print(cutin_fix)
        s.surroundingspaces=0+cutin_fix

        u = UnevenFingerJointEdge(self, s)
        u.char = "u"
        self.addPart(u)

        uc = UnevenFingerJointEdgeCounterPart(self, s)
        uc.char = "U"
        self.addPart(uc)



        d2 = edges.Bolts(2)
        d3 = edges.Bolts(3)

        d2 = d3 = None

        
        for _ in range(faces):
            self.regularPolygonWall(corners, side=a, edges="u", move="right")


