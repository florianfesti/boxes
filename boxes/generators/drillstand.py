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

import boxes
from boxes import *


class DrillStand(Boxes):
    """Box for drills with each compartment of a different height"""

    description = """Note: `sh` gives the hight of the rows front to back. It though should have the same number of entries as `sy`. These heights are the one on the left side and increase throughout the row. To have each compartement a bit higher than the previous one the steps in `sh` should be a bit bigger than `extra_height`.

Assembly:

![Parts](static/samples/DrillStand-drawing.png)

Start with putting the slots of the inner walls together. Be especially careful with adding the bottom. It is always assymetrical and flush with the right/lower side while being a little short on the left/higher side to not protrude into the side wall.

|      |      |
| ---- | ---- |
| ![Assembly inner walls](static/samples/DrillStand-assembly-1.jpg) | ![Assembly bottom](static/samples/DrillStand-assembly-2.jpg) |
| Then add the front and the back wall. | Add the very left and right walls last. |
| ![Assembly front and back](static/samples/DrillStand-assembly-3.jpg) | ![Assembly side walls](static/samples/DrillStand-assembly-4.jpg) |
"""

    ui_group = "Misc"

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.StackableSettings, height=1.0, width=3)
        self.addSettingsArgs(edges.FingerJointSettings)

        self.buildArgParser(sx="25*6", sy="10:20:30", sh="25:40:60")
        self.argparser.add_argument(
            "--extra_height",  action="store", type=float, default=15.0,
            help="height difference left to right")

    def yWall(self, nr, move=None):
        t = self.thickness
        x, sx, y, sy, sh = self.x, self.sx, self.y, self.sy, self.sh        
        eh = self.extra_height * (sum(sx[:nr])+ nr*t - t)/x

        tw, th = sum(sy) + t * len(sy) + t, max(sh) + eh

        if self.move(tw, th, move, True):
            return

        self.moveTo(t)
        self.polyline(y, 90)
        self.edges["f"](sh[-1]+eh)
        self.corner(90)
        for i in range(len(sy)-1, 0, -1):
            s1 = max(sh[i]-sh[i-1], 0) + 4*t
            s2 = max(sh[i-1]-sh[i], 0) + 4*t
            
            self.polyline(sy[i], 90, s1, -90, t, -90, s2, 90)
        self.polyline(sy[0], 90)
        self.edges["f"](sh[0] + eh)
        self.corner(90)
        
        self.move(tw, th, move)

    def sideWall(self, extra_height=0.0, foot_height=0.0, edges="šFf", move=None):
        t = self.thickness
        x, sx, y, sy, sh = self.x, self.sx, self.y, self.sy, self.sh
        eh = extra_height
        fh = foot_height

        edges = [self.edges.get(e, e) for e in edges]

        tw = sum(sy) + t * len(sy) + t
        th = max(sh) + eh + fh + edges[0].spacing()

        if self.move(tw, th, move, True):
            return

        self.moveTo(edges[0].margin())

        edges[0](y+2*t)
        self.edgeCorner(edges[0], "e")
        self.edge(fh)
        self.step(edges[1].startwidth() - t)
        edges[1](sh[-1]+eh)
        self.edgeCorner(edges[1], "e")
        for i in range(len(sy)-1, 0, -1):
            self.edge(sy[i])
            if sh[i] > sh[i-1]:
                self.fingerHolesAt(0.5*t, self.burn, sh[i]+eh, 90)
                self.polyline(t, 90, sh[i] - sh[i-1], -90)
            else:
                self.polyline(0, -90, sh[i-1] - sh[i], 90, t)
                self.fingerHolesAt(-0.5*t, self.burn, sh[i-1]+eh)
        self.polyline(sy[0])
        self.edgeCorner("e", edges[2])
        edges[2](sh[0]+eh)
        self.step(t - edges[2].endwidth())
        self.polyline(fh)
        self.edgeCorner("e", edges[0])
        
        self.move(tw, th, move)

    def xWall(self, nr, move=None):
        t = self.thickness
        x, sx, y, sy, sh = self.x, self.sx, self.y, self.sy, self.sh
        eh = self.extra_height

        tw, th = x + 2*t, sh[nr] + eh + t

        a = math.degrees(math.atan(eh / x))
        fa = 1 / math.cos(math.radians(a))

        if self.move(tw, th, move, True):
            return

        
        self.moveTo(t, eh+t, -a)

        for i in range(len(sx)-1):
            self.edges["f"](fa*sx[i])
            h = min(sh[nr - 1], sh[nr])
            s1 = h - 3.95*t + self.extra_height * (sum(sx[:i+1]) + i*t)/x
            s2 = h - 3.95*t + self.extra_height * (sum(sx[:i+1]) + i*t + t)/x

            self.polyline(0, 90+a, s1, -90, t, -90, s2, 90-a)
        self.edges["f"](fa*sx[-1])
        self.polyline(0, 90+a)
        self.edges["f"](sh[nr]+eh)
        self.polyline(0, 90, x, 90)
        self.edges["f"](sh[nr])
        self.polyline(0, 90+a)

        self.move(tw, th, move)

    def xOutsideWall(self, h, edges="fFeF", move=None):
        t = self.thickness
        x, sx, y, sy, sh = self.x, self.sx, self.y, self.sy, self.sh
        
        edges = [self.edges.get(e, e) for e in edges]
        eh = self.extra_height

        tw = x + edges[1].spacing() + edges[3].spacing()
        th = h + eh + edges[0].spacing() + edges[2].spacing()

        a = math.degrees(math.atan(eh / x))
        fa = 1 / math.cos(math.radians(a))

        if self.move(tw, th, move, True):
            return

        
        self.moveTo(edges[3].spacing(), eh+edges[0].margin(), -a)

        self.edge(t*math.tan(math.radians(a)))
        if isinstance(edges[0], boxes.edges.FingerHoleEdge):
            with self.saved_context():
                self.moveTo(0, 0, a)
                self.fingerHolesAt(
                    0, 1.5*t, x*fa - t*math.tan(math.radians(a)), -a)
            self.edge(x*fa - t*math.tan(math.radians(a)))
        elif isinstance(edges[0], boxes.edges.FingerJointEdge):
            edges[0](x*fa - t*math.tan(math.radians(a)))
        else:
            raise ValueError("Only edges h and f supported: ")
        self.corner(a)
        self.edgeCorner(edges[0], "e", 90)
        self.corner(-90)
        self.edgeCorner("e", edges[1], 90)
        edges[1](eh+h)
        self.edgeCorner(edges[1], edges[2], 90)
        edges[2](x)
        self.edgeCorner(edges[2], edges[3], 90)
        edges[3](h)
        self.edgeCorner(edges[3], "e", 90)
        self.corner(-90)
        self.edgeCorner("e", edges[0], 90)

        self.moveTo(0, self.burn+edges[0].startwidth(), 0)
        
        for i in range(1, len(sx)):
            posx = sum(sx[:i]) + i*t - 0.5 * t
            length = h + self.extra_height * (sum(sx[:i]) + i*t - t)/x
            self.fingerHolesAt(posx, h, length, -90)

        self.move(tw, th, move)

    def bottomCB(self):
        t = self.thickness
        x, sx, y, sy, sh = self.x, self.sx, self.y, self.sy, self.sh        
        eh = self.extra_height

        a = math.degrees(math.atan(eh / x))
        fa = 1 / math.cos(math.radians(a))

        posy = -0.5 * t
        for i in range(len(sy)-1):
            posy += sy[i] + t
            posx = -t * math.tan(math.radians(a)) # left side is clipped
            for j in range(len(sx)):
                self.fingerHolesAt(posx, posy, fa*sx[j], 0)
                posx += fa*sx[j] + fa*t

    def render(self):
        t = self.thickness
        sx, sy, sh = self.sx, self.sy, self.sh
        self.x = x = sum(sx) + len(sx)*t - t
        self.y = y = sum(sy) + len(sy)*t - t

        bottom_angle = math.atan(self.extra_height / x) # radians

        self.xOutsideWall(sh[0], "hFeF", move="up")
        for i in range(1, len(sy)):
            self.xWall(i, move="up")
        self.xOutsideWall(sh[-1], "hfef", move="up")

        self.rectangularWall(x/math.cos(bottom_angle)-t*math.tan(bottom_angle), y, "fefe", callback=[self.bottomCB], move="up")
        
        self.sideWall(foot_height=self.extra_height+2*t, move="right")
        for i in range(1, len(sx)):
            self.yWall(i, move="right")
        self.sideWall(self.extra_height, 2*t, move="right")
            
