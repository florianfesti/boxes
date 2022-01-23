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
from .drillstand import DrillStand

class SlatwallDrillBox(DrillStand):
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

        bottom_angle = math.atan(self.extra_height / x) # radians

        self.xOutsideWall(sh[0], "fFeF", move="up")
        for i in range(1, len(sy)):
            self.xWall(i, move="up")
        self.xOutsideWall(sh[-1], "fCec", move="up")

        self.rectangularWall(x/math.cos(bottom_angle)-t*math.tan(bottom_angle), y, "FeFe", callback=[self.bottomCB], move="up")
        
        self.sideWall(move="right")
        for i in range(1, len(sx)):
            self.yWall(i, move="right")
        self.sideWall(self.extra_height, move="right")
            
