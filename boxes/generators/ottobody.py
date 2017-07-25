#!/usr/bin/env python3
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


class OttoBody(Boxes):
    """Otto LC - a laser cut chassis for Otto DIY - body"""

    ui_group = "Unstable"

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.ChestHingeSettings)


    def bottomCB(self):
        self.hole(6, self.y/2, 6)
        self.hole(6, self.y/2-6, 3)
        self.hole(self.x-6, self.y/2, 6)
        self.hole(self.x-6, self.y/2-6, 3)

        #self.rectangularHole(20, self.y/2, 4, 30, 1.5)
        #self.rectangularHole(self.x-20, self.y/2, 4, 30, 1.5)
        self.rectangularHole(self.x/2, self.y/2, 10, 5, 1.5)

        self.rectangularHole(self.x-7, self.y-6.5, 7, 4)

        self.moveTo(0, self.y-12)
        self.hexHolesCircle(12, (1, 2, 'circle'))

    def leftBottomCB(self):
        self.hole(7, self.y-7, 6)

        self.hole(6, self.y/2+9, 0.9)
        self.rectangularHole(6, self.y/2-5.5, 12, 23)
        self.hole(6, self.y/2-20, 0.9)
    
    def rightBottomCB(self):
        self.rectangularHole(7, self.y-6.5, 11.6, 5.6)

        self.hole(8, self.y/2+9, 0.9)
        self.rectangularHole(8, self.y/2-5.5, 12, 23)
        self.hole(8, self.y/2-20, 0.9)

    def eyeCB(self):
        self.hole(self.x/2+13,self.hl/2, 8)
        self.hole(self.x/2-13,self.hl/2, 8)

    def IOCB(self):
        self.rectangularHole(26, 19, 14, 12)
        # self.rectangularHole(42.2, 10.2, 9.5, 11.5)

    def render(self):
        self.open()

        self.x = x = 60.
        self.y = y = 60.
        self.h = h = 35.
        self.hl = hl = 30.
        
        t = self.thickness

        hx = self.edges["O"].startwidth()

        e1 = edges.CompoundEdge(self, "Fe", (h-hx, hx))
        e2 = edges.CompoundEdge(self, "eF", (hx, h-hx))
        e_back = ("F", e1, "e", e2)
        
        self.moveTo(hx)
        self.rectangularWall(x, h-hx, "FfOf", ignore_widths=[2], move="up")
        self.rectangularWall(x, hl-hx, "pfFf", ignore_widths=[1], move="up")
        self.moveTo(-hx)        
        self.rectangularWall(x, h-hx, "Ffof", ignore_widths=[5], move="up")
        self.rectangularWall(x, hl-hx, "PfFf", ignore_widths=[6],
                             callback=[None, None, self.IOCB], move="up")
        self.rectangularWall(y, h, "FFeF", move="up")
        self.rectangularWall(y, h, e_back, move="up")
        self.rectangularWall(y, hl, "FFeF", callback=[self.eyeCB], move="up")
        self.rectangularWall(y, hl-hx, "FFqF", move="up")

        self.rectangularWall(x, y, "ffff", move="up")
        self.rectangularWall(x, y, "ffff", callback=[self.bottomCB], move="up")

        self.rectangularWall(y, 14, callback=[None, self.leftBottomCB], move="up")
        self.rectangularWall(y, 14, callback=[None, self.rightBottomCB], move="up")

        self.close()


