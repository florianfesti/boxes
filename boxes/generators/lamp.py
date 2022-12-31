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

"""
22x7.5x7cm
D=23cm, d=21cm
d = 8" D = 9"
"""


class RoundedTriangleSettings(edges.Settings):
    absolute_params = {
        "angle": 60,
        "radius": 30,
        "r_hole": 0.0,
    }


class RoundedTriangle(edges.Edge):
    char = "t"

    def __call__(self, length, **kw):
        angle = self.settings.angle
        r = self.settings.radius

        if self.settings.r_hole:
            x = 0.5 * (length - 2 * r) * math.tan(math.radians(angle))
            y = 0.5 * (length)
            self.hole(x, y, self.settings.r_hole)

        l = 0.5 * (length - 2 * r) / math.cos(math.radians(angle))
        self.corner(90 - angle, r)
        self.edge(l)
        self.corner(2 * angle, r)
        self.edge(l)
        self.corner(90 - angle, r)

    def startAngle(self):
        return 90

    def endAngle(self):
        return 90


class Lamp(Boxes):
    webinterface = False

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser(x=220, y=75, h=70)
        self.argparser.add_argument(
            "--radius", action="store", type=float, default="105",
            help="radius of the lamp")
        self.argparser.add_argument(
            "--width", action="store", type=float, default="10",
            help="width of the ring")

    def side(self, y, h):
        return
        self.edges["f"](y)
        self.corner(90)
        self.edges["f"](h)
        self.roundedTriangle(y, 75, 25)
        self.edges["f"](h)
        self.corner(90)

    def render(self):
        """
        r : radius of lamp
        w : width of surrounding ring
        x : length box
        y : width box
        h : height box
        """


        # self.edges["f"].settings = (5, 5) # XXX

        x, y, h = self.x, self.y, self.h
        r, w = self.radius, self.width

        s = RoundedTriangleSettings(self.thickness, angle=72, r_hole=2)
        self.addPart(RoundedTriangle(self, s))

        self.flexSettings = (3, 5.0, 20.0)

        self.edges["f"].settings.setValues(self.thickness, finger=5, space=5, relative=False)
        d = 2 * (r + w)

        self.roundedPlate(d, d, r, move="right", callback=[
            lambda: self.hole(w, r + w, r), ])

        # dist = ((2**0.5)*r-r) / (2**0.5) + 4
        # pos = (w-dist, dist)
        self.roundedPlate(d, d, r, holesMargin=w / 2.0)  # , callback=[
        #        lambda: self.hole(pos[0], pos[1], 7),])
        self.roundedPlate(d, d, r, move="only left up")

        hole = lambda: self.hole(w, 70, 2)
        self.surroundingWall(d, d, r, 120, top='h', bottom='h', callback=[
            None, hole, None, hole], move="up")

        with self.saved_context():
            self.rectangularWall(x, y, edges="fFfF", holesMargin=5, move="right")
            self.rectangularWall(x, y, edges="fFfF", holesMargin=5, move="right")
            # sides
            self.rectangularWall(y, h, "fftf", move="right")
            self.rectangularWall(y, h, "fftf")

        self.rectangularWall(x, y, edges="fFfF", holesMargin=5,
                             move="up only")

        self.rectangularWall(x, h, edges='hFFF', holesMargin=5, move="right")
        self.rectangularWall(x, h, edges='hFFF', holesMargin=5)



