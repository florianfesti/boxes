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

from boxes.walledges import _WallMountedBox


class WallHook(_WallMountedBox):
    """Hook to install on a wall"""

    def __init__(self) -> None:
        super().__init__()

        self.buildArgParser(h=100)
        self.argparser.add_argument(
            "--width",  action="store", type=float, default=10.0,
            help="width of the back panel")
        self.argparser.add_argument(
            "--hook_inside_diameter",  action="store", type=float, default=40.0,
            help="Hook's inside diameter")
        self.argparser.add_argument(
            "--hook_thickness",  action="store", type=float, default=20.0,
            help="Hook's thickness")

    def side(self, move=None):
        t = self.thickness
        h = self.h
        hid = self.hook_inside_diameter
        ht = self.hook_thickness

        total_length = hid + (ht * 2)
        radius = hid / 2
        outside_radius = radius + ht
        bottom_length = total_length - outside_radius - t

        tw = self.edges["b"].spacing() + total_length

        if self.move(tw, h, move, True):
            return

        self.moveTo(self.edges["b"].margin())
        self.polyline(
            self.edges["b"].startWidth() + bottom_length,
            (90, outside_radius),
            0,
            (180, ht / 2), # U-turn with diameter of hook's thickness
            0,
            (-90, radius),
            0,
            (-90, radius),
            h - radius - ht - ht,
            (90, ht),
            0,
            90
        )

        self.edges["b"](h)

        self.fingerHolesAt(-(ht / 2), 10, total_length - outside_radius, 90)
        self.fingerHolesAt(-outside_radius - (ht / 2), total_length - (ht /2 ), ht, 0)

        self.move(tw, h, move)

    def render(self):
        self.generateWallEdges()

        t = self.thickness
        h = self.h
        w = self.width
        ht = self.hook_thickness
        hid = self.hook_inside_diameter
        total_length = hid + (ht * 2)

        radius = hid / 2
        outside_radius = radius + ht

        self.side(move="up")
        self.side(move="right mirror")

        self.moveTo(self.edges["b"].spacing(), 0)
        self.flangedWall(w, h, flanges=[10, 2*t, 0, 2*t], edges="eeee",
                         r=2*t,
                         callback=[lambda:(self.wallHolesAt(1.5*t, 0, h, 90), self.wallHolesAt(w+2.5*t, 0, h, 90))], move="right")

        self.moveTo(0, -5)
        self.rectangularWall(w, ht, "efef", move="left down")

        self.moveTo(0, -5)
        self.rectangularWall(w, total_length - outside_radius, "efef", move="down")
