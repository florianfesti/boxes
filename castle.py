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

class Castle(Boxes):

    def __init__(self):
        Boxes.__init__(self)

    def render(self, t_x=70, t_h=250, w1_x=300, w1_h=120, w2_x=100, w2_h=120):
        self.open(800, 600)
        s = edges.FingerJointSettings(self.thickness, relative=False,
                                      space = 10, finger=10, height=10,
                                      width=self.thickness)
        p = edges.FingerJointEdge(self, s)
        p.char = "p"
        self.addPart(p)
        P = edges.FingerJointEdgeCounterPart(self, s)
        P.char = "P"
        self.addPart(P)

        self.moveTo(0,0)
        self.rectangularWall(t_x, t_h, edges="efPf", move="right", callback=
            [lambda: self.fingerHolesAt(t_x*0.5, 0, w1_h, 90),])
        self.rectangularWall(t_x, t_h, edges="efPf", move="right")
        self.rectangularWall(t_x, t_h, edges="eFPF", move="right", callback=
            [lambda: self.fingerHolesAt(t_x*0.5, 0, w2_h, 90),])
        self.rectangularWall(t_x, t_h, edges="eFPF", move="right")

        self.rectangularWall(w1_x, w1_h, "efpe", move="right")
        self.rectangularWall(w2_x, w2_h, "efpe", move="right")

        self.close()

def main():
    c = Castle()
    c.parseArgs()
    c.render()

if __name__ == '__main__':
    main()
