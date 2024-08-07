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


class BookHolder(Boxes):
    """Angled display stand for books, ring files, flyers, postcards, or business cards."""
    description = """
Smaller versions for postcards (with a small ledge) and for business cards:

![BookHolder minis (front)](static/samples/BookHolder-minis.jpg)

![BookHolder minis (side)](static/samples/BookHolder-minis-side.jpg)

BookHolder with default parameters (A4 size, landscape, back_support):

![BookHolder (back)](static/samples/BookHolder-back.jpg)
"""


    ui_group = "Misc"

    def __init__(self) -> None:
        super().__init__()

        self.addSettingsArgs(edges.FingerJointSettings)

        # Default size: DIN A4 (210mm * 297mm)
        self.argparser.add_argument(
            "--book_width",  action="store", type=float, default=297.0,
            help="total width of book stand")
        self.argparser.add_argument(
            "--book_height",  action="store", type=float, default=210.0,
            help="height of the front plate")
        self.argparser.add_argument(
            "--book_depth",  action="store", type=float, default=40.0,
            help="larger sizes for books with more pages")
        self.argparser.add_argument(
            "--ledge_height",  action="store", type=float, default=0.0,
            help="part in front to hold the book open (0 to turn off)")
        self.argparser.add_argument(
            "--angle",  action="store", type=float, default=75.0,
            help="degrees between floor and front plate")
        self.argparser.add_argument(
            "--bottom_support",  action="store", type=float, default=20.0,
            help="extra material on bottom to raise book up")
        self.argparser.add_argument(
            "--back_support",  action="store", type=float, default=50.0,
            help="height of additional support in the back (0 to turn off)")
        self.argparser.add_argument(
            "--radius",  action="store", type=float, default=-1.0,
            help="radius at the sharp corners (negative for radius=thickness)")

    def sideWall(self, move=None):

        # main angle
        alpha = self.angle
        # opposite angle
        beta = 90 - alpha

        # 1. Calculate the tall right triangle between front plate and back
        # self.book_height is hypotenuse

        # vertical piece
        a = self.book_height * math.sin(math.radians(alpha))
        # horizontal piece
        b = self.book_height * math.sin(math.radians(beta))

        # 2. Calculate the smaller triangle between bottom of book and front edge
        # self.book_depth is hypotenuse, angles are the same as in other triangle but switched

        # vertical piece
        c = self.book_depth * math.sin(math.radians(beta))
        # horizontal piece
        d = self.book_depth * math.sin(math.radians(alpha))

        # 3. Total dimensions

        # Highest point on the right where the book back rests
        max_height_back = a + self.bottom_support + self.radius
        # Hightest point on the left where the book bottom rests
        max_height_front = c + self.bottom_support + self.radius

        total_height = max(max_height_back, max_height_front)

        offset_s = math.sin(math.radians(alpha)) * self.radius
        offset_c = math.cos(math.radians(alpha)) * self.radius

        total_width = self.radius + offset_c + b + d + offset_s + self.radius

        if self.move(total_width, total_height, move, True):
            return

        # Line on bottom
        self.polyline(total_width, 90)

        # Fingerholes for back support
        if self.back_support > 0:
            posx = self.bottom_support
            posy = 2 * self.thickness
            self.fingerHolesAt(posx, posy, self.back_support, 0)

        # Back line straight up
        self.polyline(max_height_back - offset_c - self.radius, 0)
        self.corner((90+alpha, self.radius))

        # Line for front plate
        self.edges.get("F")(self.book_height)
        self.corner(-90)

        # Line where bottom of book rests
        self.edges.get("F")(self.book_depth)
        self.corner((90+beta, self.radius))

        # Front line straight down
        self.polyline(max_height_front - offset_s - self.radius, 90)

        self.move(total_width, total_height, move)

    def front_ledge(self, move):
        total_height = self.ledge_height + self.thickness
        if self.move(self.width, total_height, move, True):
            return
        self.moveTo(self.radius, 0)

        h = total_height - self.radius
        w = self.width - 2 * self.radius

        self.edges.get("e")(w)
        self.corner((90, self.radius))
        self.edges.get("e")(h)
        self.corner(90)
        self.edges.get("F")(self.width)
        self.corner(90)
        self.edges.get("e")(h)
        self.corner((90, self.radius))

        self.move(self.width, total_height, move)

    def render(self):
        self.width = self.book_width - 2 * self.thickness
        if self.radius < 0:
            self.radius = self.thickness

        # Back support
        if self.back_support > 0:
            self.rectangularWall(self.width, self.back_support, "efef", move="up", label="back support")

        # Front ledge and fingers for lower plate
        e = "e"
        if self.ledge_height > 0:
            self.front_ledge(move="up")
            e = "f"

        # Lower plate for book
        self.rectangularWall(self.width, self.book_depth, e + "fFf", move="up", label="book bottom")

        # Front plate
        self.rectangularWall(self.width, self.book_height, "ffef", move="right", label="book back")

        # Side walls
        self.sideWall(move="right")
        self.sideWall(move="right")
