#!/usr/bin/python3
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

class FlexTest(Boxes):
    "Piece for testing different flex settings"
    def __init__(self):
        Boxes.__init__(self)
        self.buildArgParser("x", "y")
        self.argparser.add_argument(
            "--fd",  action="store", type=float, default=0.5,
            help="distance of flex cuts in multiples of thickness")
        self.argparser.add_argument(
            "--fc",  action="store", type=float, default=1.0,
            help="connections of flex cuts in multiples of thickness")
        self.argparser.add_argument(
            "--fw",  action="store", type=float, default=5.0,
            help="width of flex cuts in multiples of thickness")

    def render(self):
        x, y = self.x, self.y
        self.open(x+60, y+20)

        self.edges["X"].settings.setValues(
            self.thickness, relative=True,
            distance=self.fd, connection=self.fc, width=self.fw)

        self.moveTo(5, 5)
        self.edge(10)
        self.flexEdge(x, y)
        self.edge(10)
        self.corner(90)
        self.edge(y)
        self.corner(90)
        self.edge(x+20)
        self.corner(90)
        self.edge(y)
        self.corner(90)

        self.close()

def main():
    f = FlexTest()
    f.parseArgs()
    f.render()

if __name__ == '__main__':
    main()
