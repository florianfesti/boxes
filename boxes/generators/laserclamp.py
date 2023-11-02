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

class LaserClamp(Boxes):
    """A clamp to hold down material to a knife table"""

    description = """You need a tension spring of the proper length to make the clamp work.
Increase extraheight to get more space for the spring and to make the
sliding mechanism less likely to bind. You may need to add some wax on the
parts sliding on each other to reduce friction.
"""

    ui_group = "Misc"

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=0)
        self.argparser.add_argument(
            "--minheight",  action="store", type=float, default=25.,
            help="minimal clamping height in mm")
        self.argparser.add_argument(
            "--maxheight",  action="store", type=float, default=50.,
            help="maximal clamping height in mm")
        self.argparser.add_argument(
            "--extraheight",  action="store", type=float, default=0.,
            help="extra height to make operation smoother in mm")

    def topPart(self, l, move=None):
        t = self. thickness

        tw, th = 12*t, l+4*t

        if self.move(tw, th, move, True):
            return

        self.moveTo(8*t, 0)
        self.rectangularHole(t, 2*t+l/2, 1.05*t, l)
        self.polyline(2*t, (90, t), l+1.5*t, (-90, 0.5*t),
                      2*t, -90, 0, (180, 0.5*t), 0,
                      (90, 1.5*t), 9*t,
                      (180, 4*t), 2*t, (-90, t))
        self.hole(-5*t, -3*t, 2.5*t)
        self.polyline(l-5.5*t, (90, t))
        self.move(tw, th, move)

    def bottomPart(self, h_min, h_extra, move=None):
        t = self. thickness

        tw, th = 14*t, h_min+4*t

        if self.move(tw, th, move, True):
            return

        ls = t/2*(2**.5)
        self.moveTo(2*t, 0)
        self.fingerHolesAt(3*t, 2*t, h_min+h_extra, 90)
        if h_extra:
            self.polyline(4*t, (90,t), h_extra-2*t, (-90, t))
        else:
            self.polyline(6*t)
        self.polyline(4*t, (90, 2*t), 3*t, 135, 2*ls, 45, 1*t, -90, 6*t, -90)
        
        self.polyline(h_min, (90, t), 2*t, (90, t),
                      h_min+h_extra-0*t, (-90, t), t, (180, t),
                      0, 90, 0, (-180, 0.5*t), 0 , 90)

        self.move(tw, th, move)

    def render(self):
        t = self. thickness
        h_max, h_min, h_extra = self.maxheight, self.minheight,self.extraheight

        if h_extra and h_extra < 2*t:
            h_extra = 2*t
        
        self.topPart(h_max+h_extra, move="right")
        self.bottomPart(h_min, h_extra, move="right")
        self.roundedPlate(4*t, h_min+h_extra+4*t, edge="e", r=t,
                          extend_corners=False, move="right",
            callback=[lambda: self.fingerHolesAt(1*t, 2*t, h_min+h_extra)])
        self.rectangularWall(1.1*t, h_min+h_extra, "efef")
