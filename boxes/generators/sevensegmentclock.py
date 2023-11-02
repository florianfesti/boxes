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
from .sevensegment import SevenSegmentPattern

class SevenSegmentClock(SevenSegmentPattern):
    """Seven segment clock build with LED stripe"""

    description = """You need a LED stripe that is wound through all segments in an S pattern and then continuing to the next digit while the stripe being upright on its side. Selecting *debug* gives a better idea how things fit together.

Adding a diffuser on top or at the bottom of the segment holes will probably enhance the visuals. Just using paper may be enough.

There is currently not a lot of space for electronics and this generator is still untested. Good luck!
"""

    ui_group = "Misc"
    ui_group = "Unstable"

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.argparser.add_argument(
            "--height",  action="store", type=float, default=100.0,
            help="height of the front panel (with walls if outside is selected) in mm")
        self.argparser.add_argument(
            "--h",  action="store", type=float, default=20.0,
            help="depth (with walls if outside is selected) in mm")
        self.buildArgParser(outside=False)

    def frontCB(self):
        x = self.height
        self.hole(1.27*x, 0.4*x, 0.05*x)
        self.hole(1.27*x, 0.6*x, 0.05*x)
        self.moveTo(0.1*x, 0.1*x)
        for i in range(2):
            for j in range(2):
                self.seven_segments(.8 * x)
                #self.seven_holes(.8 * x)
                self.moveTo(.6 * x)
            self.moveTo(0.1 * x)

    def backCB(self):
        x = self.height
        self.moveTo(0.1*x, 0.1*x)
        for i in range(2):
            for j in range(2):
                self.seven_segment_holes(.8 * x)
                self.moveTo(.6 * x)
            self.moveTo(0.1 * x)


    def render(self):
        height, h = self.height, self.h

        if self.outside:
            height = self.height = self.adjustSize(height)
            h = self.h = self.adjustSize(h)

        t = self.thickness
        y = (3*0.60 + 0.1 + 0.2) * height + 0.55 * 0.8 * height

        self.rectangularWall(height, h, "FFFF", move="right")
        self.rectangularWall(y, h, "FfFf", move="up")
        self.rectangularWall(y, h, "FfFf")
        self.rectangularWall(height, h, "FFFF", move="left up")

        with self.saved_context():
            self.rectangularWall(y, height, "ffff", callback=[self.frontCB], move="right")
            self.rectangularWall(y, height, "ffff", callback=[self.backCB], move="right")
        self.rectangularWall(y, height, "ffff", move="up only")
        self.seven_segment_separators(0.8*height, h, 4)
