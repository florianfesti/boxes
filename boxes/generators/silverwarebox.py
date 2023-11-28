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

from boxes import Boxes, restore


class Silverware(Boxes):
    """
    Cuttlery stand with carrying grip
    using flex for rounded corners
    """

    ui_group = "Unstable"


    def __init__(self) -> None:
        Boxes.__init__(self)

        self.buildArgParser(x=250, y=154, h=120)

        self.argparser.add_argument(
            "--cornerradius", action="store", type=int, default=30,
            help="Radius of the corners")
        self.argparser.add_argument(
            "--handleheight", action="store", type=int, default=150,
            help="Height of the handle")
        self.argparser.add_argument(
            "--handlewidth", action="store", type=int, default=120,
            help="Width of the handle")


    ####################################################################
    ### Parts
    ####################################################################

    def basePlate(self, x, y, r):
        self.roundedPlate(x, y, r, extend_corners=False, callback=[
            lambda: self.fingerHolesAt(x / 3.0 - r, 0, 0.5 * (y - self.thickness)),
            lambda: self.fingerHolesAt(x / 6.0, 0, 0.5 * (y - self.thickness)),
            lambda: self.fingerHolesAt(y / 2.0 - r, 0, x),
            lambda: self.fingerHolesAt(x / 2.0 - r, 0, 0.5 * (y - self.thickness))
        ])

    def wall(self, x=100, y=100, h=100, r=0):
        self.surroundingWall(x, y, r, h, top="E", bottom='h', callback={
            0: lambda: self.fingerHolesAt(x / 6.0, 0, h - 10),
            4: lambda: self.fingerHolesAt(x / 3.0 - r, 0, h - 10),
            1: lambda: self.fingerHolesAt(y / 2.0 - r, 0, h - 10),
            3: lambda: self.fingerHolesAt(y / 2.0 - r, 0, h - 10),
            2: lambda: self.fingerHolesAt(x / 2.0 - r, 0, h - 10),
        },
                             move="up")

    @restore
    def centerWall(self, x, h):
        self.moveTo(self.edges["f"].spacing(), self.edges["f"].spacing())
        for i in range(2, 5):
            self.fingerHolesAt(i * x / 6.0, 0, h - 10)

        self.edges["f"](x)
        self.corner(90)
        self.edges["f"](h - 10)
        self.corner(90)

        self.handle(x, self.handleheight, self.handlewidth)

        self.corner(90)
        self.edges["f"](h - 10)
        self.corner(90)
        self.ctx.stroke()

    ##################################################
    ### main
    ##################################################

    def render(self):
        x = self.x
        y = self.y
        h = self.h
        r = self.cornerradius

        t = self.thickness
        b = self.burn

        self.wall(x, y, h, r)
        self.centerWall(x, h)
        self.moveTo(x + 2 * self.edges["f"].spacing())

        l = (y - t) / 2.0

        for _ in range(3):
            self.rectangularWall(l, h - 10, edges="ffef", move="right")

        self.moveTo(-3.0 * (l + 2 * t + 8 * b), h - 10 + 2 * t + 8 * b)
        self.basePlate(x, y, r)

