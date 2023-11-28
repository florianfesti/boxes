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

try:
    from gettext import gettext as _
except ImportError:
    def _(message: str) -> str:
        return message

from boxes import *


class OttoBody(Boxes):
    """Otto LC - a laser cut chassis for Otto DIY - body"""

    ui_group = "Misc"

    def __init__(self) -> None:
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

        # switch
        self.rectangularHole(self.x-7, self.y-2.8, 7, 4)

        self.moveTo(0, self.y-12)
        self.hexHolesCircle(12, HexHolesSettings(
            self, diameter=2, distance=2, style='circle'))

    def leftBottomCB(self):
        self.hole(7, self.y-7, 6)

        self.hole(6, self.y/2+9, 0.9)
        self.rectangularHole(6, self.y/2-5.5, 12, 23)
        self.hole(6, self.y/2-20, 0.9)
    
    def rightBottomCB(self):
        self.hole(7, self.y-5, 2)

        self.hole(8, self.y/2+9, 0.9)
        self.rectangularHole(8, self.y/2-5.5, 12, 23)
        self.hole(8, self.y/2-20, 0.9)

    def eyeCB(self):
        self.hole(self.x/2+13,self.hl/2, 8)
        self.hole(self.x/2-13,self.hl/2, 8)

    def frontCB(self):
        t = self.thickness
        self.rectangularHole(0.5*t, 2+t, t, 2.5)
        self.rectangularHole(self.x-0.5*t, 2+t, t, 2.5)

    def IOCB(self):
        self.rectangularHole(26, 18, 12, 10)
        # self.rectangularHole(42.2, 10.2, 9.5, 11.5)

    def buttonCB(self):
        px, py = 7.5, 7.5

        self.rectangularHole(px, py-2.25, 5.2, 2.5)
        self.rectangularHole(px, py+2.25, 5.2, 2.5)

    def PCB_Clip(self, x , y, move=None):

        if self.move(x+4, y, move, True):
            return
        self.moveTo(1.5)
        self.polyline(x-1.5, 90, (y, 2), 90, x, 85, (y-2-4, 2), -30, 2, 120, 1, -90, 2, (180, 1.), y-7, -175, y-5)

        self.move(x+4, y, move)

    def PCB_Clamp(self, w, s, h, move=None):
        t = self. thickness
        f = 2**0.5
        
        if self.move(w+4, h+8+t, move, True):
            return
        self.polyline(w, 90, s, -90, 1, (90, 1), (h-s-1, 2), 90, w-2, 90,
                      h-8, (-180, 1), h-8+3*t, 135, f*(4), 90, f*2, -45,
                      (h+t, 2))
        self.move(w+4, h+8+t, move)

    def render(self):

        self.x = x = 60.
        self.y = y = 60.
        self.h = h = 35.
        self.hl = hl = 30.
        
        t = self.thickness

        hx = self.edges["O"].startwidth()
        hx2 = self.edges["P"].startwidth()

        e1 = edges.CompoundEdge(self, "Fe", (h-hx, hx))
        e2 = edges.CompoundEdge(self, "eF", (hx, h-hx))
        e_back = ("F", e1, "e", e2)

        # sides
        self.moveTo(hx)
        self.rectangularWall(x, h-hx, "FfOf", ignore_widths=[2], move="up", label=_("Left bottom side"))
        self.rectangularWall(x, hl-hx2, "pfFf", ignore_widths=[1], move="up", label=_("Left top side"))
        self.moveTo(-hx)        
        self.rectangularWall(x, h-hx, "Ffof", ignore_widths=[5], callback=[
            lambda: self.rectangularHole(y-7.5, h-4-7.5, 6.2, 7.)],
                             move="up", label=_("Right bottom side"))
        self.rectangularWall(x, hl-hx2, "PfFf", ignore_widths=[6],
                             callback=[None, None, self.IOCB], move="up",
                             label=_("Right top side"))

        # lower walls
        self.rectangularWall(y, h, "FFeF", callback=[
            None, None, self.frontCB], move="up",
            label=_("Lower front"))
        self.rectangularWall(y, h, e_back, move="up",
            label=_("Lower back"))

        # upper walls
        self.rectangularWall(y, hl, "FFeF", callback=[self.eyeCB], move="up", label=_("Upper front"))
        self.rectangularWall(y, hl-hx2, "FFqF", move="up", label=_("Upper back"))

        # top
        self.rectangularWall(x, y, "ffff", move="up", label=_("Top"))
        # bottom
        self.rectangularWall(x, y, "ffff", callback=[self.bottomCB], move="up", label=_("Bottom"))
        # PCB mounts
        with self.saved_context():
            self.PCB_Clamp(y-53.5, 4.5, hl, move="right")
            self.PCB_Clamp(y-50, 4.5, hl, move="right")
            self.PCB_Clip(3.5, hl, move="right")
            self.rectangularWall(15, 15, callback=[self.buttonCB])
        self.PCB_Clamp(y-53.5, 4.5, hl, move="up only")
        # servo mounts
        self.moveTo(0, 50)
        self.rectangularWall(y, 14, callback=[None, None, None,
                                              self.leftBottomCB], move="up",
                             label=_("Servo mount"))
        self.rectangularWall(y-5.6, 14, callback=[
            None, None, None, self.rightBottomCB], move="up",
            label=_("Servo mount"))



