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

class TrayInsert(Boxes):
    """Tray insert without floor and outer walls - allows only continuous walls"""

    description = """## Tray/Box insert dividers.
Tray insert with extra margin for that perfect fit.

You can specify the grid sizes with the standard `(sx, sy)` format, which allows nice
variable rows and columns.  If you  check the `outside` box, the full outside of the
tray insert ends up being the sum of all the sx/sy values.  However, if you want a
consistent cell size, and uncheck outside, then the overall dimensinos end up
larger by `(n-1)*thickenss`, to make space for your walls.

You can specify the `x` and `y` parameters if you like, just make them larger than
what the sum of `(sx, sy)` would end up with, and the walls be automatically extended to
to exactly fill the inside of your tray or box.

So, for example, if you're fitting `30mm x 40mm` items and want them to
fit inside a `250mm x 300mm` box, you can specify

    sx = 30*8
    sy = 40*7
    uncheck outside
    x=250
    y=300

This frees your mind into separately thinking about the cell size vs the overall box size.

![Tray Extra](static/samples/TrayInsert-3.jpg)
    """
    ui_group = "Tray"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.buildArgParser("sx", "sy", "h", "outside")
        self.argparser.add_argument(
            "--x", action="store", type=float, default=-1,
            help="X dimension of tray/box that this fits into")
        self.argparser.add_argument(
            "--y", action="store", type=float, default=-1,
            help="Y dimension of tray/box that this fits into.  ")


    def render(self):

        if self.outside:
            self.sx = self.adjustSize(self.sx, False, False)
            self.sy = self.adjustSize(self.sy, False, False)

        t = self.thickness
        x = sum(self.sx) + t * (len(self.sx) - 1)
        y = sum(self.sy) + t * (len(self.sy) - 1)
        h = self.h

        if self.x > x:
            delta = self.x-x
            if delta > 2 * t:
                # add extra walls
                self.sx = [delta/2-t, *self.sx, delta/2-t]
            else:
                # the user is asking for less than a thickness of extra.  just add
                # it to the outside walls without creating new walls
                self.sx[0] += delta/2
                self.sx[-1] += delta/2
            x = self.x

        if self.y > y:
            delta = self.y-y
            if delta > 2 * t:
                # add extra walls
                self.sy = [delta/2-t, *self.sy, delta/2-t]
            else:
                # the user is asking for less than a thickness of extra.  just add
                # it to the outside walls without creating new walls
                self.sy[0] += delta/2
                self.sy[-1] += delta/2
            y = self.y

        # Inner walls
        for i in range(len(self.sx) - 1):
            e = [edges.SlottedEdge(self, self.sy, slots=0.5 * h), "e", "e", "e"]
            self.rectangularWall(y, h, e, move="up")

        for i in range(len(self.sy) - 1):
            e = ["e", "e", edges.SlottedEdge(self, self.sx[::-1], "e", slots=0.5 * h), "e"]
            self.rectangularWall(x, h, e, move="up")
