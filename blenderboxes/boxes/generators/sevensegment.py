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

class SevenSegmentPattern(Boxes):
    """Holepatterns and walls for a seven segment digit"""

    description = """This pattern is indented to be used with a LED stripe that is wound through all segments in an S pattern while the stripe being upright on its side. It can probably also be used for small pieces of LED stripes connected with short wires for large enough sizes.

Both is currently untested.
"""

    ui_group = "Misc"
    ui_group = "Unstable"

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.argparser.add_argument(
            "--digit",  action="store", type=float, default=100.0,
            help="height of the digit (without walls) in mm")
        self.argparser.add_argument(
            "--h",  action="store", type=float, default=20.0,
            help="height separation walls in mm")

    @restore
    @holeCol
    def segment(self, l, w):
        w2 = w * 2**0.5
        self.moveTo(0, 0, 45)
        self.polyline(w2, -45, l-2*w, -45, w2, -90, w2, -45,
                      l-2*w, -45, w2, -90)

    @restore
    def seven_segments(self, x):
        t = self.thickness
        l = 0.4 * x
        w = 0.05 * x
        d = 0.05 * x
        width = l + 2*w + d # 0.55 * x

        #self.rectangularHole(width/2, x/2, width, x)
        
        for px in [w/2 + d/2 , w/2 + l + 1.5*d]:
            for py in [w + d/2, w + l + 1.5*d]:
                with self.saved_context():
                    self.moveTo(px, py, 90)
                    self.segment(l, w)
        for i in range(3):
            with self.saved_context():
                self.moveTo(w/2 + d, w + i*(l+d))
                self.segment(l, w)

    def seven_segment_holes(self, x):
        t = self.thickness
        l = 0.4 * x
        w = 0.05 * x
        d = 0.05 * x
        width = l + 2*w + d

        for i in range(2):
            self.fingerHolesAt(t/4*2**.5, x/2+w-t/4*2**.5,
                               2**0.5*(width-t) - t/2, -45)
            self.fingerHolesAt(t, t, 2**0.5* (.55*x/2 - t) - t/2, 45)
            self.fingerHolesAt(width/2 + t/2**.5/2,
                               width/2 + t/2**.5/2,
                               2**0.5*(l/2+d/2) - 1.5*t, 45)
            self.fingerHolesAt(-t/2, x/2 + 0.25*t, x/2 - 0.25*t, 90)
            self.fingerHolesAt(-t/2, 0, x/2 - 0.25*t, 90)
            self.fingerHolesAt(-t, -t/2, l + 2*w + d + 2*t, 0)
            self.moveTo(width, x, 180)

    def seven_segment_separators(self, x, h, n=1):
        t = self.thickness
        l = 0.4 * x
        w = 0.05 * x
        d = 0.05 * x
        width = l + 2*w + d # 0.55 * x
        for length in (
                2**0.5*(width-t) - t/2,
                2**0.5* x/4 - t,
                2**0.5*(l/2+d/2) - 1.5*t,
                x/2 - 0.25*t,
                x/2 - 0.25*t,
                l + 2*w + d + 2*t,):
            self.partsMatrix(2*n, 1, "right",
                             self.rectangularWall, length, h, "feee")

    def render(self):
        digit, h = self.digit, self.h
        t = self.thickness

        self.seven_segments(digit)
        self.moveTo(0.55*digit+self.spacing+t, t)
        #self.seven_segments(digit)
        self.seven_segment_holes(digit)
        self.moveTo(0.55*digit+self.spacing+t, -t)
        self.seven_segment_separators(digit, h)
