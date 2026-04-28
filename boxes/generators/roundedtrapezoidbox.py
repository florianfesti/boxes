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

import boxes
import math

class RoundedTrapezoidBox(boxes.Boxes):
    """Trapezoid box with rounded vertical edges."""

    description = """
The x and y measurements are for a trapazoid with sharp corners. The radii cut the corners so the actual width is smaller for all trapazoid except rectangles.
"""

    ui_group = "Unstable" # "FlexBox"

    def __init__(self) -> None:
        boxes.Boxes.__init__(self)
        self.addSettingsArgs(boxes.edges.FingerJointSettings)
        self.addSettingsArgs(boxes.edges.DoveTailSettings)
        self.addSettingsArgs(boxes.edges.FlexSettings)
        self.buildArgParser(y=100.0, h="100.0")
        self.argparser.add_argument(
            "--x_front", action="store", type=float, default=100.0,
            help="front width (assuming radius == zero) in mm")
        self.argparser.add_argument(
            "--x_back", action="store", type=float, default=100.0,
            help="back width (assuming radius == zero) in mm")

        self.argparser.add_argument(
            "--radius_front_left", action="store", type=float, default=20.0,
            help="radius of front left corner in mm")
        self.argparser.add_argument(
            "--radius_front_right", action="store", type=float, default=20.0,
            help="radius of front right corner in mm")
        self.argparser.add_argument(
            "--radius_back_right", action="store", type=float, default=20.0,
            help="radius of back_right corner in mm")
        self.argparser.add_argument(
            "--radius_back_left", action="store", type=float, default=20.0,
            help="radius of back left corner in mm")

        self.argparser.add_argument(
            "--wall_pieces", action="store", type=int, default=1,
            choices=(1, 2, 4),
            help="number of pieces for outer wall")
        self.argparser.add_argument(
            "--top",  action="store", type=str, default="hole",
            choices=["hole", "lid", "closed",],
            help="style of the top and lid")

    def holeCB(self):
        t = self.thickness

        self.moveTo(0, 2*t)
        self.polygonWall(self.hole_poly, edge="e", turtle=True, correct_corners=False)

    def render(self):
        t = self.thickness

        xf, xb, y, h = self.x_front, self.x_back, self.y, self.h

        r_fl, r_fr, r_br, r_bl = (
            self.radius_front_left,
            self.radius_front_right,
            self.radius_back_right,
            self.radius_back_left)

        a = math.degrees(math.atan((xf-xb)/(2*y)))
        y_l = y_r = y / math.cos(math.radians(a))

        # reduce sides by space used for radius
        d_fl = math.tan(math.radians((90+a)/2)) * r_fl
        d_fr = math.tan(math.radians((90+a)/2)) * r_fr
        d_br = math.tan(math.radians((90-a)/2)) * r_br
        d_bl = math.tan(math.radians((90-a)/2)) * r_bl

        poly = [(xf - d_fl - d_fr) / 2, (90+a, r_fr),
                y_r - d_fr - d_br, (90-a, r_br),
                xb - d_br - d_bl,  (90-a, r_bl),
                y_l - d_bl - d_fl, (90+a, r_fl),
                (xf - d_fl - d_fr) / 2, 0]

        d = 2*t

        # reduce radii for hole
        self.hole_poly = [(v[0], v[1] - d) if isinstance(v, tuple) else v for v in poly]
        # fix radii < 0
        for nr, v in enumerate(self.hole_poly):
            if nr % 2 and isinstance(v, tuple) and v[1] < 0:
                d = v[1] * math.tan(math.radians((v[0])/2))
                self.hole_poly[nr - 1] += d
                self.hole_poly[nr + 1] += d
                self.hole_poly[nr] = (v[0], 0)

        if self.wall_pieces != 1:
            poly[4:5] = [poly[4]/2, 0.0, poly[4]/2]
        if self.wall_pieces == 4:
            poly[8:9] = [poly[8]/2, 0.0, poly[8]/2]
            poly[2:3] = [poly[2]/2, 0.0, poly[2]/2]

        with self.saved_context():
            self.polygonWall(poly, move="right")
            if self.top == "closed":
                self.polygonWall(poly, move="right")
            else:
                self.polygonWall(poly, callback=[self.holeCB], move="right")
            if self.top == "lid":
                self.polygonWall([self.side, (360 / n, self.radius+t)] *n, edge="e", move="right")

        self.polygonWall(poly, move="up only")
        self.moveTo(0, t)
        self.polygonWalls(poly, self.h)
