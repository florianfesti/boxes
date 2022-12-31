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


class SlotEdge(edges.Edge):

    def __call__(self, length, **kw):
        t, n = self.settings.thickness, self.settings.n
        r, h = self.settings.radius, self.settings.h
        sh = self.settings.sh # distance side to center

        li = 2 * sh * math.tan(math.radians(90/n)) # side inner 2x polygone
        ls2 = t / math.tan(math.radians(180/n))
        ls1 = t / math.cos(math.radians(90-(180/n)))

        lo = (length-li-2*ls1)/2

        li = li - 2*ls2 # correct for overlap of wall
        
        d = h/2
        
        if li > 0:
            poly = [lo-1, (90, 1), d+t-1, -90, ls1+ls2, -90, d-t, (90, t)]
        self.polyline(*(poly + [li-2*t] + list(reversed(poly))))

    def startwidth(self):
        return self.settings.thickness


class RegularStarBox(Boxes):
    """Regular polygon boxes that form a star when closed"""

    ui_group = "Box"


    description = """![Open box](static/samples/RegularStarBox-2.jpg)"""

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser("h", "outside")
        self.argparser.add_argument(
            "--radius",  action="store", type=float, default=50.0,
            help="inner radius if the box (center to corners)")
        self.argparser.add_argument(
            "--n",  action="store", type=int, default=5,
            choices=(3, 4, 5),
            help="number of sides")

    def render(self):

        r, h, n = self.radius, self.h, self.n

        if self.outside:
            self.r = r = r - self.thickness / math.cos(math.radians(360/(2*n)))
            self.h = h = self.adjustSize(h)

        t = self.thickness

        fingerJointSettings = copy.deepcopy(self.edges["f"].settings)
        fingerJointSettings.setValues(self.thickness, angle=360./n)
        fingerJointSettings.edgeObjects(self, chars="gGH")

        self.edges["e"] = SlotEdge(self, self)

        r, sh, side  = self.regularPolygon(n, radius=r)
        self.sh = sh

        with self.saved_context():
            self.regularPolygonWall(corners=n, r=r, edges='F', move="right")
            self.regularPolygonWall(corners=n, r=r, edges='F', move="right")

        self.regularPolygonWall(corners=n, r=r, edges='F', move="up only")

        for s in range(2):
            with self.saved_context():
                if n % 2:
                    for i in range(n):
                        self.rectangularWall(side, h, move="right",
                                             edges="fgeG")
                else:
                    for i in range(n//2):
                        self.rectangularWall(side, h, move="right",
                                                 edges="fGeG")
                        self.rectangularWall(side, h, move="right",
                                             edges="fgeg")

            self.rectangularWall(side, h, move="up only",
                                 edges="fgeG")
