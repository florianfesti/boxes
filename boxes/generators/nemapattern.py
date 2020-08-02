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

class NemaPattern(Boxes):
    """Mounting holes for a Nema motor"""

    ui_group = "Holes"

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.argparser.add_argument(
            "--size", action="store", type=int, default=8,
            choices=list(sorted(self.nema_sizes.keys())),
            help="Nema size of the motor")
        self.argparser.add_argument(
            "--screwholes", action="store", type=float, default=0.0,
            help="Size of the screw holes in mm - 0 for default size")

    def render(self):
        motor, flange, holes, screws = self.nema_sizes.get(
            self.size, self.nema_sizes[8])

        self.NEMA(self.size, motor/2, motor/2, screwholes=self.screwholes)
