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

class Coffin(Boxes):
    """Box with both ends cornered"""

    ui_group = "Box"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser("x", "outside", h=30)
        self.argparser.add_argument(
            "--width", action="store", type=float, default=0.40,
            help="width at the shoulders as fraction of the total length")
        self.argparser.add_argument(
            "--top_width", action="store", type=float, default=0.25,
            help="width at the head as fraction of the total length")
        self.argparser.add_argument(
            "--bottom_width", action="store", type=float, default=0.25,
            help="width at the feet as fraction of the total length")
        self.argparser.add_argument(
            "--shoulder_height", action="store", type=float, default=0.7,
            help="widest point as fraction of the total length")
        self.argparser.add_argument(
            "--cross", action="store", type=float, default=0.2,
            help="size of cross as fraction of the total length")

        #self.argparser.add_argument(
        #    "--top",  action="store", type=str, default="none",
        #    choices=["none", "angled hole", "angled lid", "angled lid2"],
        #    help="style of the top and lid")

    def crossCB(self):
        c = (self.x+2*self.thickness)  * self.cross

        if not c:
            return

        self.moveTo(self.yb/2, self.xb-1.2*c)
        poly = [0.05*c, 90, 0.9*c, -90, 0.45*c, 90, 0.1*c, 90, 0.45*c, -90,
                0.45*c, 90, 0.1*c]
        self.polyline(*(poly + list(reversed(poly[:-1]))))

    def render(self):

        x, xb = self.x, self.x*self.shoulder_height
        xt = x - xb
        yb, y, yt = x*self.bottom_width, x*self.width, x*self.top_width
        t = self.thickness

        if self.outside:
            self.x = x = self.adjustSize(x)
            self.xb = xb = self.adjustSize(xb, None)
            self.y = y = self.adjustSize(y)
            self.yb = yb = self.adjustSize(yb)
            self.yt = yt = self.adjustSize(yt)

        ab = math.degrees(math.atan((y-yb)/2/xb))
        at = math.degrees(math.atan((y-yt)/2/xt))
        lb = xb / math.cos(math.radians(ab))
        lt = xt / math.cos(math.radians(at))

        poly = (yb, 90-ab, lb, ab+at, lt, 90-at, yt, 90-at, lt, at+ab, lb, 90-ab)

        self.polygonWall(poly, "f", move="right")
        self.polygonWall(poly, "f", callback=[self.crossCB], move="right")

        self.polygonWalls(poly, self.h)
