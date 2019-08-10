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

class SlatwallDrillBox(Boxes):
    """Box for drills with each compartment with a different height"""

    ui_group = "SlatWall"

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.SlatWallSettings)

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

    def sideWall(self, extra_height=0.0, move=None):
        t = self.thickness
        x, sx, y, sy, sh = self.x, self.sx, self.y, self.sy, self.sh
        eh = extra_height

        tw, th = sum(sy) + t * len(sy) + t, max(sh) + eh

        if self.move(tw, th, move, True):
            return

        self.moveTo(t)
        self.polyline(y+t, 90)
        self.edges["B"](sh[-1]+eh)
        self.polyline(0, 90, t)
        for i in range(len(sy)-1, 0, -1):
            self.edge(sy[i])
            if sh[i] > sh[i-1]:
                self.fingerHolesAt(0.5*t, self.burn, sh[i]+eh, 90)
                self.polyline(t, 90, sh[i] - sh[i-1], -90)
            else:
                self.polyline(0, -90, sh[i-1] - sh[i], 90, t)
                self.fingerHolesAt(-0.5*t, self.burn, sh[i-1]+eh)
        self.polyline(sy[0], 90)
        self.edges["f"](sh[0]+eh)
        self.corner(90)
        
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

        edges[0](x*fa)
        self.corner(a)
        self.edgeCorner(edges[0], edges[1], 90)
        edges[1](eh+h)
        self.edgeCorner(edges[1], edges[2], 90)
        edges[2](x)
        self.edgeCorner(edges[2], edges[3], 90)
        edges[3](h)
        self.edgeCorner(edges[3], edges[0], 90)

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
            posx = 0
            for j in range(len(sx)):
                self.fingerHolesAt(posx, posy, fa*sx[j], 0)
                posx += fa*sx[j] + fa*t

    def render(self):
        # Add slat wall edges
        s = edges.SlatWallSettings(self.thickness, True,
                                   **self.edgesettings.get("SlatWall", {}))
        s.edgeObjects(self)
        self.slatWallHolesAt = edges.SlatWallHoles(self, s)

        t = self.thickness
        sx, sy, sh = self.sx, self.sy, self.sh
        self.x = x = sum(sx) + len(sx)*t - t
        self.y = y = sum(sy) + len(sy)*t - t

        self.xOutsideWall(sh[0], "fFeF", move="up")
        for i in range(1, len(sy)):
            self.xWall(i, move="up")
        self.xOutsideWall(sh[-1], "fCec", move="up")

        self.rectangularWall((x**2+self.extra_height**2)**0.5, y, "FeFe", callback=[self.bottomCB], move="up")
        
        self.sideWall(move="right")
        for i in range(1, len(sx)):
            self.yWall(i, move="right")
        self.sideWall(self.extra_height, move="right")
            
