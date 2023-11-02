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
from boxes.walledges import _WallMountedBox

class WallRollHolder(_WallMountedBox):
    """Holder for kitchen rolls or other rolls"""

    description = """Needs a dowel or pipe as axle."""
    
    ui_group = "WallMounted"

    def __init__(self) -> None:
        super().__init__()

        self.argparser.add_argument(
            "--width",  action="store", type=float, default=275,
            help="length of the axle in mm")
        self.argparser.add_argument(
            "--diameter",  action="store", type=float, default=120,
            help="maximum diameter of the roll in mm (choose generously)")
        self.argparser.add_argument(
            "--height",  action="store", type=float, default=80,
            help="height of mounting plate in mm")
        self.argparser.add_argument(
            "--axle",  action="store", type=float, default=25,
            help="diameter of the axle in mm including play")

    def side(self, move=None):
        d = self.diameter
        a = self.axle
        h = self.height
        t = self.thickness

        tw, th = h, (d + a) / 2 + 3 * t + self.edges["B"].spacing()

        if self.move(tw, th, move, True):
            return

        self.moveTo(0, self.edges["B"].margin())
        self.edges["B"](h)
        self.fingerHolesAt(-(a/2+3*t), self.burn+self.edges["B"].endwidth(), d/2, 90)
        self.polyline(0, 90, self.edges["B"].endwidth() + d/2,
                      (90, a/2 + 3*t))

        r = a/2 + 3*t
        a = math.atan2(float(d/2), (h-a-6*t))
        alpha = math.degrees(a)

        self.corner(alpha, r)
        self.edge(((h-2*r)**2+(d/2)**2)**0.5)
        self.corner(90-alpha, r)
        self.edge(self.edges["B"].startwidth())
        self.corner(90)
        
        self.move(tw, th, move)

    def backCB(self):
        t = self.thickness
        a = self.axle
        h = self.height
        w = self.width

        plate = w + 2*t + h/2
        
        self.wallHolesAt(h/4+t/2-3*t, 0, h, 90)
        self.fingerHolesAt(h/4-3*t, h-3*t-a/2, h/4, 180)

        self.wallHolesAt(h/4+t/2+t-3*t+w, 0, h, 90)
        self.fingerHolesAt(h/4+2*t-3*t+w, h-3*t-a/2, h/4, 0)

    def rings(self):
        a = self.axle
        r = a/2
        t = self.thickness
        
        self.moveTo(0, a+1.5*t, -90)
        for i in range(2):
            self.polyline(r-1.5*t, (180, r+3*t), 0, (180, 1.5*t), 0,
                          (-180, r), r-1.5*t, (180, 1.5*t))
            self.moveTo(a-t, a+12*t, 180)
                          
                      
    def render(self):

        self.generateWallEdges()

        t = self.thickness
        w = self.width
        d = self.diameter
        a = self.axle
        h = self.height

        self.height = h = max(h, a+10*t)

        self.side(move="right")
        self.side(move="right")

        self.rectangularTriangle(h/4, d/2, "ffe", num=2, r=3*t, move="right")

        self.roundedPlate(w+h/2+2*t, h, edge="e", r=3*t,
                          extend_corners=False,
                          callback=[self.backCB], move="right")
        self.rings()
