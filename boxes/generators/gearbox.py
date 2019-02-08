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


class GearBox(Boxes):
    """Gearbox with multiple identical stages"""

    ui_group = "Part"

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.argparser.add_argument(
            "--teeth1", action="store", type=int, default=8,
            help="number of teeth on ingoing shaft")
        self.argparser.add_argument(
            "--teeth2", action="store", type=int, default=20,
            help="number of teeth on outgoing shaft")
        self.argparser.add_argument(
            "--modulus", action="store", type=float, default=3,
            help="modulus of the theeth in mm")
        self.argparser.add_argument(
            "--shaft", action="store", type=float, default=6.,
            help="diameter of the shaft")
        self.argparser.add_argument(
            "--stages", action="store", type=int, default=4,
            help="number of stages in the gear reduction")

    def render(self):

        if self.teeth2 < self.teeth1:
            self.teeth2, self.teeth1 = self.teeth1, self.teeth2

        pitch1, size1, xxx = self.gears.sizes(teeth=self.teeth1, dimension=self.modulus)
        pitch2, size2, xxx = self.gears.sizes(teeth=self.teeth2, dimension=self.modulus)

        t = self.thickness
        x = 1.1 * t * self.stages

        if self.stages == 1:
            y = size1 + size2
            y1 = y / 2 - (pitch1 + pitch2) + pitch1
            y2 = y / 2 + (pitch1 + pitch2) - pitch2
        else:
            y = 2 * size2
            y1 = y / 2 - (pitch1 + pitch2) / 2
            y2 = y / 2 + (pitch1 + pitch2) / 2

        h = max(size1, size2) + t

        b = "F"
        t = "e"  # prepare for close box
        mh = self.shaft

        def sideCB():
            self.hole(y1, h / 2, mh / 2)
            self.hole(y2, h / 2, mh / 2)

        self.moveTo(self.thickness, self.thickness)
        self.rectangularWall(y, h, [b, "f", t, "f"], callback=[sideCB], move="right")
        self.rectangularWall(x, h, [b, "F", t, "F"], move="up")
        self.rectangularWall(x, h, [b, "F", t, "F"])
        self.rectangularWall(y, h, [b, "f", t, "f"], callback=[sideCB], move="left")
        self.rectangularWall(x, h, [b, "F", t, "F"], move="up only")

        self.rectangularWall(x, y, "ffff", move="up")

        profile_shift = 20
        pressure_angle = 20

        for i in range(self.stages - 1):
            self.gears(teeth=self.teeth2, dimension=self.modulus, angle=pressure_angle,
                       mount_hole=mh, profile_shift=profile_shift, move="up")

        self.gears(teeth=self.teeth2, dimension=self.modulus, angle=pressure_angle,
                   mount_hole=mh, profile_shift=profile_shift, move="right")

        for i in range(self.stages):
            self.gears(teeth=self.teeth1, dimension=self.modulus, angle=pressure_angle,
                       mount_hole=mh, profile_shift=profile_shift, move="down")



