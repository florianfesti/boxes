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

class Shoe(Boxes):
    """Shoe shaped box"""

    description = """Shoe shaped box with flat sides and rounded top. 
    Works best if flex if under slight compression. 
    Make sure that the following conditions are met: 
    y > tophole + r + fronttop; 
    height > frontheight."""

    ui_group = "Misc"

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.FlexSettings)
 
        self.argparser.add_argument(
            "--width",  action="store", type=float, default=65,
            help="width of the shoe")
        self.argparser.add_argument(
            "--length",  action="store", type=float, default=175,
            help="length front to back")
        self.argparser.add_argument(
            "--height",  action="store", type=float, default=100,
            help="height at the back of the shoe")
        self.argparser.add_argument(
            "--frontheight",  action="store", type=float, default=35,
            help="height at the front of the shoe")
        self.argparser.add_argument(
            "--fronttop",  action="store", type=float, default=20,
            help="length of the flat part at the front of the shoe")
        self.argparser.add_argument(
            "--tophole",  action="store", type=float, default=75,
            help="length of the opening at the top")
        self.argparser.add_argument(
            "--radius",  action="store", type=float, default=30,
            help="radius of the bend")


    def render(self):
        x, y, h = self.width, self.length, self.height
        t = self.thickness

        hf = self.frontheight
        yg = self.tophole
        tf = self.fronttop
        r=self.radius

        if (hf > h):
            # Give an error because the result will be wrong with possible unconnected paths
            raise ValueError("Height at front of shoe must be less than height at back of shoe.")

        stretch = (self.edges["X"].settings.stretch)

        self.ctx.save()
        self.rectangularWall(y, x, "FFFF", move="up", label="Bottom")
        lf,a=self.shoeside(y,h,hf,yg,tf,r, move="up", label="Side")
        self.shoeside(y,h,hf,yg,tf,r, move="mirror up", label="Side")
        self.ctx.restore()
        self.rectangularWall(y, x, "FFFF", move="right only")
        self.rectangularWall(x, h, "ffef", move="up", label="Back")
        self.rectangularWall(x, hf, "ffff", move="up", label="front")
        dr = a*(r-t)/stretch
        self.shoelip(x, tf, dr, lf, label="top")

        
    def shoelip(self, x, tf, dr, lf, move=None, label=""):

        w = self.edges["F"].spacing()

        th = tf + dr + lf + self.edges["F"].spacing() + self.edges["e"].spacing()
        tw = x + 2*w
        if self.move(tw, th, move, True, label=label):
            return

        self.moveTo(self.edges["F"].spacing(), self.edges["e"].spacing())

        self.edges["F"](x)
        self.edgeCorner("F", "F")
        self.edges["F"](tf)
        self.edges["X"](dr, h=x+2*w)
        self.edges["F"](lf)
        self.edgeCorner("F", "e")
        self.edges["e"](x)
        self.edgeCorner("e", "F")
        self.edges["F"](lf)
        self.edges["E"](dr)
        self.edges["F"](tf)
        self.edgeCorner("F", "F")

        self.move(tw, th, move, label=label)

    def shoeside(self, y, h, hf, yg, tf, r, move=None, label=""):
        import math

        tx = y + 2 * self.edges.get('F').spacing()
        ty = h + self.edges.get('f').spacing() + self.edges.get("e").spacing()
        
        if self.move(tx, ty, move, before=True):
            return

        lf = math.sqrt((h-hf)**2+(y-yg-tf)**2)
        af = 90-math.degrees(math.atan((h-hf)/(y-yg-tf)))

        atemp = math.degrees(math.atan((h-hf-r)/(y-yg-tf)))
        dtemp = math.sqrt((h-hf-r)**2+(y-yg-tf)**2)
        lf = math.sqrt(dtemp**2-r**2)
        af = 90-atemp-math.degrees(math.atan(r/lf))

        self.moveTo(self.edges.get('f').margin(), self.edges.get("f").margin())

        self.edges.get('f')(y)
        self.edgeCorner(self.edges["f"],self.edges["F"],90)
        self.edges.get('F')(hf)
        self.edgeCorner(self.edges["F"],self.edges["f"],90)
        self.edges.get('f')(tf)
        self.corner(af-90,r)
        self.edges.get('f')(lf)
        self.edgeCorner(self.edges["f"],self.edges["e"],90-af)
        self.edges.get('e')(yg)
        self.edgeCorner(self.edges["e"],self.edges["F"],90)
        self.edges.get('F')(h)
        self.edgeCorner(self.edges["F"],self.edges["f"],90)

        self.move(tx, ty, move, label=label)

        return lf,math.radians(90-af)
