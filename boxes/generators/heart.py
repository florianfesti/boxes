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

class HeartBox(Boxes):
    """Box in the form of a heart"""

    ui_group = "FlexBox"

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, finger=1.0,space=1.0)
        self.addSettingsArgs(edges.FlexSettings)
        self.buildArgParser(x=150, h=50)
        self.argparser.add_argument(
            "--top",  action="store", type=str, default="closed",
            choices=["closed", "hole", "lid",],
            help="style of the top and lid")

    def CB(self):
        x = self.x
        t = self.thickness

        l = 2/3. * x - t
        r = l/2. - t
        d = 2 *t

        if self.top == "closed":
            return
        
        for i in range(2):
            self.moveTo(t, t)
            self.polyline((l, 2), (180, r), (d, 1), -90,
                          (d, 1), (180, r), (l, 2), 90)
            l -= t
            r -= t
            d += t
            if self.top == "hole":
                return

    def render(self):
        x, h = self.x, self.h
        t = self.thickness

        l = 2/3. * x
        r = l/2. - 0.5*t
        
        borders = [l, (180, r), t, -90, t, (180, r), l, 90]
        self.polygonWalls(borders, h)
        self.rectangularWall(0, h, "FFFF", move="up only")
        self.polygonWall(borders, callback=[self.CB], move="right")
        self.polygonWall(borders, move="mirror right")
        if self.top == "lid":
            self.polygonWall([l+t, (180, r+t), 0, -90, 0, (180, r+t), l+t, 90], 'e')
