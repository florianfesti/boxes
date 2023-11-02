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

class Gears(Boxes):
    """Gears"""

    ui_group = "Part"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.argparser.add_argument(
            "--teeth1",  action="store", type=int, default=12,
            help="number of teeth")
        self.argparser.add_argument(
            "--shaft1", action="store", type=float, default=6.,
            help="diameter of the shaft 1")
        self.argparser.add_argument(
            "--dpercentage1", action="store", type=float, default=75,
            help="percent of the D section of shaft 1 (100 for round shaft)")

        self.argparser.add_argument(
            "--teeth2",  action="store", type=int, default=32,
            help="number of teeth in the other size of gears")
        self.argparser.add_argument(
            "--shaft2", action="store", type=float, default=0.0,
            help="diameter of the shaft2 (zero for same as shaft 1)")
        self.argparser.add_argument(
            "--dpercentage2", action="store", type=float, default=0,
            help="percent of the D section of shaft 1 (0 for same as shaft 1)")

        self.argparser.add_argument(
            "--modulus",  action="store", type=float, default=2,
            help="size of teeth (diameter / #teeth) in mm")
        self.argparser.add_argument(
            "--pressure_angle",  action="store", type=float, default=20,
            help="angle of the teeth touching (in degrees)")
        self.argparser.add_argument(
            "--profile_shift",  action="store", type=float, default=20,
            help="in percent of the modulus")

    def render(self):
        # adjust to the variables you want in the local scope
        t = self.thickness

        self.teeth1 = max(2, self.teeth1)
        self.teeth2 = max(2, self.teeth2)

        if not self.shaft2:
            self.shaft2 = self.shaft1
        if not self.dpercentage2:
            self.dpercentage2 = self.dpercentage1

        self.gears(teeth=self.teeth2, dimension=self.modulus,
                   angle=self.pressure_angle, profile_shift=self.profile_shift,
                   callback=lambda:self.dHole(0, 0, d=self.shaft2,
                                              rel_w=self.dpercentage2/100.),
                   move="up")
        r2, d2, d2 = self.gears.sizes(
            teeth=self.teeth2, dimension=self.modulus,
            angle=self.pressure_angle, profile_shift=self.profile_shift)

        self.gears(teeth=self.teeth1, dimension=self.modulus,
                   angle=self.pressure_angle, profile_shift=self.profile_shift,
                   callback=lambda:self.dHole(0, 0, d=self.shaft1,
                                              rel_w=self.dpercentage1/100.),
                   move="up")
        r1, d1, d1 = self.gears.sizes(
            teeth=self.teeth1, dimension=self.modulus,
            angle=self.pressure_angle, profile_shift=self.profile_shift)
        r = max(self.shaft1, self.shaft2)/2
        self.hole(t+r, t+r, self.shaft1/2)
        self.hole(t+r+r1+r2, t+r, self.shaft2/2)
        self.moveTo(0, 2*r+t)

        self.text(f"Pitch radius 1: {r1:.1f}mm\n"
                  f"Outer diameter 1: {d1:.1f}mm\n"
                  f"Pitch radius 2: {r2:.1f}mm\n"
                  f"Outer diameter 2: {d2:.1f}mm\n"
                  f"Axis distance: {r1 + r2:.1f}mm\n",
                  align="bottom left")
