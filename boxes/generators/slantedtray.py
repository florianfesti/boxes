# Copyright (C) 2013-2023 Florian Festi
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
from functools import partial

class SlantedTray(Boxes):
    """One row tray with high back wall and low front wall"""

    ui_group = "Tray"

    description = """Can be used as a display or for cards or gaming tokens. Lay on the side to get piles to draw from.
    ![Example Use](static/samples/SlantedTray-2.jpg)"""

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)
        # self.addSettingsArgs(edges.StackableSettings)

        self.buildArgParser(sx="40*3", y=40.0, h=40.0, outside=False)
        self.argparser.add_argument(
            "--front_height",  action="store", type=float, default=0.3,
            help="height of the front as fraction of the total height")

    def finger_holes_CB(self, sx, h):
        t = self.thickness
        pos = -0.5 * t
        for x in sx[:-1]:
            pos += x + t
            self.fingerHolesAt(pos, 0, h)

    def render(self):
        # adjust to the variables you want in the local scope
        sx, y, h = self.sx, self.y, self.h
        t = self.thickness

        if self.outside:
            self.sx = sx = self.adjustSize(sx)
            self.y = y = self.adjustSize(y)
            self.h = h = self.adjustSize(h, False)

        front_height = h * self.front_height
        x = sum(sx) + t * (len(sx) - 1)

        self.rectangularWall(
            x,
            h,
            "eFfF",
            move="up",
            callback=[partial(self.finger_holes_CB, sx, h)],
        )

        self.rectangularWall(
            x,
            y,
            "FFfF",
            move="up",
            callback=[partial(self.finger_holes_CB, sx, y)],
        )

        self.rectangularWall(
            x,
            front_height,
            "FFeF",
            move="up",
            callback=[
                partial(self.finger_holes_CB, sx, front_height)
            ],
        )

        for _ in range(len(sx) + 1):
            self.trapezoidWall(y, h, front_height, "ffef", move="right")
