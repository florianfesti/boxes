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
import inspect

class ChestLid(Boxes):

    def getR(self, x, angle=0):
        t = self.thickness
        d = x - 2*math.sin(math.radians(angle)) * (3*t)

        r = d / 2.0 / math.cos(math.radians(angle))
        return r

    def side(self, x, angle=0, move=""):
        if "a" not in self.edges:
            s = edges.FingerJointSettings(self.thickness, True,
                                          finger=1.0, space=1.0)
            s.edgeObjects(self, "aA.")

        t = self.thickness
        r = self.getR(x, angle)
        if self.move(x+2*t, 0.5*x+3*t, move, True):
            return

        self.moveTo(t, 0)
        self.edge(x)
        self.corner(90+angle)
        self.edges["a"](3*t)
        self.corner(180-2*angle, r)
        self.edges["a"](3*t)
        self.corner(90+angle)

        self.move(x+2*t, 0.5*x+3*t, move, False)

    def top(self, x, y, angle=0, move=None):
        if "a" not in self.edges:
            s = edges.FingerJointSettings(self.thickness, True,
                                          finger=1.0, space=1.0)
            s.edgeObjects(self, "aA.")

        t = self.thickness
        l = math.radians(180-2*angle) * self.getR(x, angle)

        tw = l + 6*t
        th = y+2*t

        if self.move(tw, th, move, True):
            return

        self.edges["A"](3*t)
        self.edges["X"](l, y+2*t)
        self.edges["A"](3*t)
        self.corner(90)
        self.edge(y+2*t)
        self.corner(90)
        self.edges["A"](3*t)
        self.edge(l)
        self.edges["A"](3*t)
        self.corner(90)
        self.edge(y+2*t)
        self.corner(90)

        self.move(tw, th, move)

    def drawAddOnLid(self, x, y, style):
        if style == "flat":
            self.rectangularWall(x, y, "eeee", move="right")
            self.rectangularWall(x, y, "EEEE", move="up")
        elif style == "chest":
            self.side(x, move="right")
            self.side(x, move="up")
            self.side(x, move="left only")
            self.top(x, y, move="up")
        else:
            return False
        return True

class TopEdge(Boxes):

    def addTopEdgeSettings(self):
        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.StackableSettings)
        self.addSettingsArgs(edges.HingeSettings)
        self.addSettingsArgs(edges.CabinetHingeSettings)
        self.addSettingsArgs(edges.LidSettings)
        self.addSettingsArgs(edges.ClickSettings)

    def topEdges(self, top_edge):
        t1 = t2 = t3 = t4 = self.edges.get(top_edge, self.edges["e"])

        if t1.char == "i":
            t2 = t4 = "e"
            t3 = "j"
        elif t1.char == "k":
            t2 = t4 = "e"
        elif t1.char == "L":
            t1 = "M"
            t2 = "e"
            t3 = "N"
        elif t1.char == "v":
            t2 = t3 = t4 = "e"

        return [t1, t2, t3, t4]

    def drawLid(self, x, y, top_edge, bedBolts=[None, None]):
        d2, d3 = bedBolts
        if top_edge == "c":
            self.rectangularWall(x, y, "CCCC", bedBolts=[d2, d3, d2, d3], move="up")
        elif top_edge == "f":
            self.rectangularWall(x, y, "FFFF", move="up")
        elif top_edge == "L":
            self.rectangularWall(x, y, "nlmE", move="up")
        elif top_edge == "i":
            self.rectangularWall(x, y, "IEJe", move="up")
        elif top_edge == "k":
            outset =  self.edges["k"].settings.outset
            self.edges["k"].settings.setValues(self.thickness, outset=True)
            lx = x/2.0-0.1*self.thickness
            self.edges['k'].settings.setValues(self.thickness, grip_length=5)
            self.rectangularWall(lx, y, "IeJe", move="right")
            self.rectangularWall(lx, y, "IeJe", move="up")
            self.rectangularWall(lx, y, "IeJe", move="left only")
            self.edges["k"].settings.setValues(self.thickness, outset=outset)
        elif top_edge == "v":
            self.rectangularWall(x, y, "VEEE", move="up")
            self.edges["v"].parts(move="up")
        else:
            return False
        return True

class Box2(TopEdge, ChestLid):
    """Box various options for different stypes and lids"""

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


    def render(self):
        x, y, h = self.x, self.y, self.h

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
        self.drawAddOnLid(x, y, self.lid)

        self.close()

def main():
    b = Box2()
    b.parseArgs()
    b.render()

if __name__ == '__main__':
    main()
