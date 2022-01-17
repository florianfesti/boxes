#!/usr/bin/env python3
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

class JointPanel(Boxes):
    """Create pieces larger than your laser cutter by joining them with Dove Tails"""

    description = """This can be used to just create a big panel in a smaller laser cutter. But the actual use is to split large parts into multiple smaller pieces. Copy the outline onto the sheet and then use the pieces to cut it into multiple parts that each can fit your laser cutter. Note that each piece must be cut with the sheet surrounding it to ensure the burn correction (aka kerf) is correct. Depending on your vector graphics software you may need to duplicate your part multiple times and then generate the intersection between one copy and each rectangular part.

The Boxes.py drawings assume that the laser is cutting in the center of the line and the width of the line represents the material that is cut away. Make sure your changes work the same way and you do not cutting away the kerf.

Small dove tails make it easier to fit parts in without problems. Lookout for pieces cut loose where the dove tails meet the edge of the parts. Move your part if necessary to avoid dove tails or details of your part colliding in a weird way.

For plywood this method works well with a very stiff press fit. Aim for needing a hammer to join the pieces together. This way they will feel like they have been welder together.

"""
    
    ui_group = "Misc"

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(
            edges.DoveTailSettings, size=1, depth=.5, radius=.1)
        self.buildArgParser(sx="400/2", sy="400/3")
        self.argparser.add_argument(
            "--separate",  action="store", type=boolarg, default=False,
            help="draw pieces apart so they can be cut to form a large sheet")

    def render(self):
        sx, sy = self.sx, self.sy
        t = self.thickness

        for ny, y in enumerate(sy):
            t0 = "e" if ny == 0 else "d"
            t2 = "e" if ny == len(sy) - 1 else "D"
            with self.saved_context():
                for nx, x in enumerate(sx):
                    t1 = "e" if nx == len(sx) - 1 else "d"
                    t3 = "e" if nx == 0 else "D"
                    self.rectangularWall(x, y, [t0, t1, t2, t3])
                    if self.separate:
                        self.rectangularWall(x, y, [t0, t1, t2, t3],
                                             move="right only")
                    else:
                        self.moveTo(x)
            if self.separate:
                self.rectangularWall(x, y, [t0, t1, t2, t3],
                                    move="up only")
            else:
                self.moveTo(0, y - self.edges["d"].spacing() if ny == 0 else y)
