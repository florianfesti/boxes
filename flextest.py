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


    def render(self, x, y):
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

x = 40
y = 100
f = FlexTest(x+30, y+10, thickness=5.0, burn=0.05)
# (1.5, 3.0, 15.0) # line distance, connects, width
f.flexSettings = (2, 4.0, 16.0)
f.render(x, y)

