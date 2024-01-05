# Copyright (C) 2013-2018 Florian Festi
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


class UnevenHeightBox(Boxes):
    """Box with different height in each corner"""

    ui_group = "Box"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.GroovedSettings)
        self.buildArgParser("x", "y", "outside", bottom_edge="F")
        self.argparser.add_argument(
            "--height0", action="store", type=float, default=50,
            help="height of the front left corner in mm")
        self.argparser.add_argument(
            "--height1", action="store", type=float, default=50,
            help="height of the front right corner in mm")
        self.argparser.add_argument(
            "--height2", action="store", type=float, default=100,
            help="height of the right back corner in mm")
        self.argparser.add_argument(
            "--height3", action="store", type=float, default=100,
            help="height of the left back corner in mm")
        self.argparser.add_argument(
            "--lid", action="store", type=boolarg, default=False,
            help="add a lid (works best with high corners opposing each other)")
        self.argparser.add_argument(
            "--lid_height", action="store", type=float, default=0,
            help="additional height of the lid")
        self.argparser.add_argument(
            "--edge_types", action="store", type=str, default="eeee",
            help="which edges are flat (e) or grooved (z,Z), counter-clockwise from the front")

    def render(self):

        x, y = self.x, self.y
        heights = [self.height0, self.height1, self.height2, self.height3]

        edge_types = self.edge_types
        if len(edge_types) != 4 or any(et not in "ezZ" for et in edge_types):
            raise ValueError("Wrong edge_types style: %s)" % edge_types)

        if self.outside:
            x = self.adjustSize(x)
            y = self.adjustSize(y)
            for i in range(4):
                heights[i] = self.adjustSize(heights[i], self.bottom_edge,
                                             self.lid)

        t = self.thickness
        h0, h1, h2, h3 = heights
        b = self.bottom_edge

        self.trapezoidWall(x, h0, h1, [b, "F", edge_types[0], "F"], move="right")
        self.trapezoidWall(y, h1, h2, [b, "f", edge_types[1], "f"], move="right")
        self.trapezoidWall(x, h2, h3, [b, "F", edge_types[2], "F"], move="right")
        self.trapezoidWall(y, h3, h0, [b, "f", edge_types[3], "f"], move="right")

        with self.saved_context():
            if b != "e":
                self.rectangularWall(x, y, "ffff", move="up")

            if self.lid:
                maxh = max(heights)
                lidheights = [maxh-h+self.lid_height for h in heights]
                h0, h1, h2, h3 = lidheights
                lidheights += lidheights
                edges = ["E" if (lidheights[i] == 0.0 and lidheights[i+1] == 0.0) else "f" for i in range(4)]
                self.rectangularWall(x, y, edges, move="up")

        if self.lid:
            self.moveTo(0, maxh+self.lid_height+self.edges["F"].spacing()+self.edges[b].spacing()+1*self.spacing, 180)
            edge_inverse = {"e": "e", "z": "Z", "Z": "z"}
            edge_types = [edge_inverse[et] for et in edge_types]

            self.trapezoidWall(y, h0, h3, "Ff" + edge_types[3] + "f", move="right" +
                      (" only" if h0 == h3 == 0.0 else ""))
            self.trapezoidWall(x, h3, h2, "FF" + edge_types[2] + "F", move="right" +
                      (" only" if h3 == h2 == 0.0 else ""))
            self.trapezoidWall(y, h2, h1, "Ff" + edge_types[1] + "f", move="right" +
                      (" only" if h2 == h1 == 0.0 else ""))
            self.trapezoidWall(x, h1, h0, "FF" + edge_types[0] + "F", move="right" +
                      (" only" if h1 == h0 == 0.0 else ""))



