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
from boxes.walledges import _WallMountedBox
from .drillstand import DrillStand


class WallDrillBox(DrillStand, _WallMountedBox):
    """Box for drills with each compartment with a different height"""
    ui_group = "WallMounted"

    def __init__(self) -> None:
        _WallMountedBox.__init__(self) # don't call DrillStand.__init__

        self.addSettingsArgs(edges.StackableSettings, height=1.0, width=3)
        self.buildArgParser(sx="25*6", sy="10:20:30", sh="25:40:60")
        self.argparser.add_argument(
            "--extra_height",  action="store", type=float, default=15.0,
            help="height difference left to right")

    def render(self):
        self.generateWallEdges()

        t = self.thickness
        sx, sy, sh = self.sx, self.sy, self.sh
        self.x = x = sum(sx) + len(sx)*t - t
        self.y = y = sum(sy) + len(sy)*t - t

        bottom_angle = math.atan(self.extra_height / x) # radians

        self.xOutsideWall(sh[0], "hFeF", move="up")
        for i in range(1, len(sy)):
            self.xWall(i, move="up")
        self.xOutsideWall(sh[-1], "hCec", move="up")

        self.rectangularWall(x/math.cos(bottom_angle)-t*math.tan(bottom_angle), y, "fefe", callback=[self.bottomCB], move="up")
        
        self.sideWall(edges="eBf", foot_height=2*t, move="right")
        for i in range(1, len(sx)):
            self.yWall(i, move="right")
        self.sideWall(self.extra_height, foot_height=2*t, edges="eBf", move="right")
