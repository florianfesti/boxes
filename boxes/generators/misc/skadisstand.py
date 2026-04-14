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


class SkadisStand(Boxes):
    """Feet for a Skadis board so it can stand on its own"""

    ui_group = "WallMounted"

    def __init__(self) -> None:
        Boxes.__init__(self)

        #self.addSettingsArgs(edges.StackableSettings) # XXX

        self.argparser.add_argument(
            "--angle",  action="store", type=float, default=70.,
            help="Angle of the board (90 for vertical)")
        self.argparser.add_argument(
            "--foot",  action="store", type=float, default=100.,
            help="length of the horizontal foot behind the board")
        self.argparser.add_argument(
            "--foot_front",  action="store", type=float, default=0.,
            help="Extend a foot to the front side of the board (zero to disable)")
        self.argparser.add_argument(
            "--connectors",  action="store", type=argparseInts, default="1:3",
            help="Positions for the connectors. Values must be all odd or all even.")
        self.argparser.add_argument(
            "--extra_height_top",  action="store", type=float, default=20.,
            help="Extra height above the last connector")
        self.argparser.add_argument(
            "--extra_height_bottom",  action="store", type=float, default=0.,
            help="Extra space below the board")


    def connector_poly(self):
        cons = sorted(self.connectors)
        for i in range(len(cons)):
            if cons[i] % 2 != cons[0] % 2:
                cons[i] += 1
        pos = 0
        poly = [self.extra_height_bottom+5, 0]
        for c in cons:
            poly.extend([(c-pos)*20-10, -90, 4.5, 90, 10, 90, 4.5, -90])
            pos = c
        return poly


    def render(self):
        # adjust to the variables you want in the local scope
        t = self.thickness

        a = self.angle
        f, ff = self.foot, self.foot_front
        h_b, h_t = self.extra_height_bottom, self.extra_height_top
        cons = self.connectors
        r = .2 * f
        w = max(f/10, t)

        h = h_b + h_t + max(cons)*20 + 20
        dr = r*math.tan(math.radians(90-a/2))

        if ff:
            self.roundedPlate(f+ff, 2*w, w, "e", callback=[
                lambda: self.fingerHolesAt(ff-w, w, f-0.5*t, 0)],
                              extend_corners=False, move="up")

        self.polygonWall(
            [f-t/2, (90, t/2), w-t, (90, t/2),
             f-t/2-dr-w*math.tan(math.radians(90-a))-w/math.sin(math.radians(a)), (-180+a, r),
            h-dr-w/math.sin(math.radians(a))-w*math.cos(math.radians(a))-t/2,
            (90, t/2), w-t, (90, t/2),
            h_t+15-t/2] + list(reversed(self.connector_poly())) +
            [180-a],
            edge="feeeeeeeeeeeeeeeeeeeee" if ff else "e", correct_corners=False)
