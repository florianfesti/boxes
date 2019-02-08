#!/usr/bin/env python3
# Copyright (C) 2013-2017 Florian Festi
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

class NemaMount(Boxes):
    """Mounting braket for a Nema motor"""

    ui_group = "Part"

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.argparser.add_argument(
            "--size", action="store", type=int, default=8,
            choices=list(sorted(self.nema_sizes.keys())),
            help="Nema size of the motor")

    def render(self):
        motor, flange, holes, screws = self.nema_sizes.get(
            self.size, self.nema_sizes[8])
        t = self.thickness

        x = y = h = motor + 2*t


        self.rectangularWall(x, y, "ffef", callback=[
            lambda: self.NEMA(self.size, x/2, y/2)], move="right")
        self.rectangularTriangle(x, h, "fFe", num=2, move="right")
        self.rectangularWall(x, h, "FFeF", callback=[

            lambda:self.rectangularHole((x-holes)/2, y/2, screws, holes,
                                        screws/2),
            None,
            lambda:self.rectangularHole((x-holes)/2, y/2, screws, holes,
                                        screws/2)],
                             move="right")
        self.moveTo(t, 0)
        self.fingerHolesAt(0.5*t, t, x, 90)
        self.fingerHolesAt(1.5*t+x, t, x, 90)
        self.fingerHolesAt(t, 0.5*t, x, 0)

