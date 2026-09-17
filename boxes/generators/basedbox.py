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
from boxes.lids import _TopEdge


class BasedBox(_TopEdge):
    """Fully closed box on a base"""

    ui_group = "Box"

    description = """This box is more of a building block than a finished item.
Use a vector graphics program (like Inkscape) to add holes or adjust the base
plate. The width of the "brim" can also be adjusted with the **edge_width**
 parameter in the **Finger Joints Settings**.

See ClosedBox for variant without a base.
"""

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(lids.LidSettings)
        self.buildArgParser(
                            "x", "y", "h", "outside", "top_edge")
        # self.buildArgParser(top_edge="feFhcCESŠvtyY", x=100.0, y=100.0, h=100.0, outside=True)


    def render(self):
        x, y, h = self.x, self.y, self.h
        t = self.thickness

        tl, tb, tr, tf = self.topEdges(self.top_edge)
        ba = self.edges.get("F", self.edges["F"])

        if self.outside:
            x = self.adjustSize(x)
            y = self.adjustSize(y)
            self.h = h = self.adjustSize(h, self.top_edge)

        if self.top_edge in "ik":
            self.edges[self.top_edge].settings.style = "flush_inset"
            ignore_widths = [1, 3, 4, 6]

        self.rectangularWall(y, h, ["f", "f", tf, "f"], move="up", label="front")
        self.rectangularWall(y, h, [ba, "f", tb, "f"], move="up", label="back")

        self.rectangularWall(x, y, "hhhh", move="up", label="base")


        self.drawLid(x, y, self.top_edge)
        self.lid(x, y, self.top_edge)

        self.rectangularWall(x, h, ["f", "F", tl, "F"], move="up", label="left")
        self.rectangularWall(x, h, ["f", "F", tr, "F"], move="up", label="right")


