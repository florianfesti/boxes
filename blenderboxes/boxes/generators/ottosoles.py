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

class OttoSoles(Boxes):
    """Foam soles for the OttO bot"""

    ui_group = "Misc"

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.buildArgParser(x=58., y=38.)
        self.argparser.add_argument(
            "--width",  action="store", type=float, default=4.,
            help="width of sole stripe")
        self.argparser.add_argument(
            "--chamfer",  action="store", type=float, default=5.,
            help="chamfer at the corners")
        self.argparser.add_argument(
            "--num",  action="store", type=int, default=2,
            help="number of soles")


    def render(self):
        x, y = self.x, self.y
        c = self.chamfer
        c2 = c * 2**0.5
        w = min(self.width, c2 / 2. / math.tan(math.radians(22.5)))
        w = self.width
        w2 = w * 2**0.5 - c2 / 2
        d = w * math.tan(math.radians(22.5))

        
        self.edges["d"].settings.setValues(w, size=0.4, depth=0.3,
                                           radius=0.05)

        self.moveTo(0, y, -90)

        for i in range(self.num*2):
            if c2 >= 2 * d:
                self.polyline((c2, 1), 45, (y-2*c, 1), 45, c2/2., 90)
                self.edges["d"](w)
                self.polyline(0, 90, c2/2-d, -45, (y-2*c-2*d, 1), -45,
                              (c2-2*d, 1), -45,
                              (x-2*c-2*d, 1), -45, c2/2-d, 90)
                self.edges["D"](w)
                self.polyline(0, 90, c2/2., 45, (x-2*c, 1), 45)
                self.moveTo(0, w + c2/2. + 2*2**0.5*self.burn)
            else:
                self.polyline((c2, 1), 45, (y-2*c, 1), 45, c2/2., 90)
                self.edges["d"](w2)
                self.polyline(0, 45, (y-2*w, 1), -90, (x-2*w, 1), 45)
                self.edges["D"](w2)
                self.polyline(0, 90, c2/2., 45, (x-2*c, 3), 45)
                self.moveTo(0, w * 2**0.5 + 2*2**0.5*self.burn)
