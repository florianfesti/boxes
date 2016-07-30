#!/usr/bin/python3
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

class MotorEdge(edges.BaseEdge):
    #def margin(self):
    #    return 30
    def __call__(self, l, **kw):
        self.polyline(
            l-165, 45,
            25*2**0.5, -45,
            60, -45,
            25*2**0.5, 45,
            55)

class OutsetEdge(edges.OutSetEdge):
    def startwidth(self):
        return 20

class HangerEdge(edges.BaseEdge):
    char = "H"
    def margin(self):
        return 40

    def __call__(self, l, **kw):
        self.fingerHolesAt(0, -0.5*self.thickness, l, angle=0)
        self.polyline(0, -90,
                      30, 90,
                      70, 135,
                      2**0.5*12, 45,
                      35, -45,
                      2**0.5*4, -90,
                      2**0.5*4, -45,
                      l -28, 45,
                      2**0.5*5, 45, 5, -90)

class RollerEdge(edges.BaseEdge):
    def margin(self):
        return 20
    def __call__(self, l, **kw):
        m = 40+100
        self.polyline((l-m)/2.0, -45,
                      2**0.5*20, 45,
                      100, 45,
                      2**0.5*20, -45,
                      (l-m)/2.0)

class RollerEdge2(edges.BaseEdge):
    def margin(self):
        return self.thickness

    def __call__(self, l, **kw):
        a = 30
        f = 1/math.cos(math.radians(a))
        self.edges["f"](70)
        self.polyline(0, a, f*25, -a, l-190, -a, f*25, a, 0)
        self.edges["f"](70)

class Rotary(Boxes):
    """Rotary Attachment for engraving cylindrical objects in a laser cutter"""
    def __init__(self):
        Boxes.__init__(self)
        # remove cli params you do not need
        #self.buildArgParser("x", "sx", "y", "sy", "h", "hi")
        # Add non default cli params if needed (see argparse std lib)
        self.argparser.add_argument(
            "--diameter",  action="store", type=float, default=72.,
            help="outer diameter of the wheels")
        self.argparser.add_argument(
            "--rubberthickness",  action="store", type=float, default=5.,
            help="diameter of the strings of the O rings")
        self.argparser.add_argument(
            "--axle",  action="store", type=float, default=6.,
            help="diameter of the axles")


    def mainPlate(self):
        # Motor block outer side
        t = self.thickness
        d = self.diameter
        a = self.axle
        self.hole(1.0*d, 0.6*d, a/2.)
        #self.hole(1.0*d, 0.6*d, d/2.)
        self.hole(2.0*d+5, 0.6*d, a/2.)
        #self.hole(2.0*d+5, 0.6*d, d/2.)
        # Main beam
        self.rectangularHole(1.5*d+2.5, 3.6, 32, 7.1)

    def frontPlate(self):
        # Motor block inner side with motor mount
        t = self.thickness
        d = self.diameter
        a = self.axle
        self.hole(1.0*d, 0.6*d, a/2.)
        #self.hole(1.0*d, 0.6*d, d/2.)
        self.hole(2.0*d+5, 0.6*d, a/2.)
        #self.hole(2.0*d+5, 0.6*d, d/2.)
        # Main beam
        self.rectangularHole(1.5*d+2.5, 3.6, 32, 7.1)
        # Motor
        mx = 2.7*d+20
        self.rectangularHole(mx, 0.6*d, 36+20, 36, r=36/2.0)

        for x in (-1, 1):
            for y in (-1,1):
                self.rectangularHole(mx+x*25, 0.6*d+y*25, 20, 4, r=2)

    def link(self, x, y, a, middleHole=False, move=None):
        t = self. thickness
        overallwidth = x + y
        overallheight = y
        ra = a/2.0
        if self.move(overallwidth, overallheight, move, before=True):
            return

        self.moveTo(y/2.0, 0)
        self.hole(0, y/2., ra)
        self.hole(x, y/2., ra)
        if middleHole:
            self.hole(x/2., y/2., ra)
        self.edge(10)
        self.edges["F"](60)
        self.polyline(x-70, (180, y/2.), x, (180, y/2.))
        self.ctx.stroke()

        self.move(overallwidth, overallheight, move)

    def holderBaseCB(self):
        self.hole(20, 30, self.a/2)
        self.rectangularHole(self.hl-70, self.hh-10, 110, self.a, r=self.a/2)
        self.rectangularHole(self.hl/2, 3.6, 32, 7.1)

    def holderTopCB(self):
        self.fingerHolesAt(0, 30-0.5*self.thickness, self.hl, 0)
        d = self.diameter/2.0 + 1
        y = -0.6*self.diameter + 2*self.hh
        print(y)
        self.hole(self.hl/2+d, y, self.axle/2.0)
        self.hole(self.hl/2-d, y, self.axle/2.0)
        self.hole(self.hl/2+d, y, self.diameter/2.0)
        self.hole(self.hl/2-d, y, self.diameter/2.0)

    def render(self):
        # adjust to the variables you want in the local scope
        t = self.thickness
        d = self.diameter
        a = self.a = self.axle
        # Initialize canvas
        self.open()
        #self.spacing = 0.1 * t

        # Change settings of default edges if needed. E.g.:
        self.edges["f"].settings.setValues(self.thickness, space=2, finger=2,
                                        surroundingspaces=1)
        self.addPart(HangerEdge(self, None))
        # render your parts here
        self.moveTo(5*t, 5*t)
        # Holder
        hw = self.hw = 60.
        hh = self.hh = 40.
        hl = self.hl = 240
        # Base
        self.rectangularWall(hl, hh, edges="hfef", callback=[self.holderBaseCB, None, lambda:self.rectangularHole(hl/2+50, hh-t/2-1, 60, t+2)], move="up")
        self.rectangularWall(hl, hh, edges="hfef", callback=[self.holderBaseCB], move="up")
        self.rectangularWall(hl, hw, edges="ffff", callback=[
            lambda: self.hole(hl/2-16-20, 25, 5)], move="up")
        self.ctx.save()
        self.rectangularWall(hw, hh, edges="hFeF", callback=[
            lambda: self.hole(hw/2, 15, 4)],move="right")
        self.rectangularWall(hw, hh, edges="hFeF", move="right")
        # Top
        th = 30
        #  sides
        self.rectangularWall(hw+20, th, edges="fFeF", move="right",
                             callback=[lambda:self.fingerHolesAt(20-0.5*t,0,th)])
        self.rectangularWall(hw+20, th, edges="fFeF", move="right",
                             callback=[lambda:self.fingerHolesAt(20-0.5*t,0,th)])
        self.ctx.restore()
        self.rectangularWall(hw, hh, edges="hFeF", move="up only")
        outset = OutsetEdge(self, None)
        roller2 = RollerEdge2(self, None)
        self.rectangularWall(hl, th, edges=[roller2, "f", "e", "f"], callback=[
            lambda:self.hole(20, 15, a/2), None, lambda:self.rectangularHole(50, th-15, 70, a, r=a/2)], move="up")
        self.rectangularWall(hl, th, edges=[roller2, "f", "e", "f"], callback=[
            lambda:self.hole(20, 15, a/2), None, lambda:self.rectangularHole(50, th-15-t, 70, a, r=a/2)], move="up")
        self.rectangularWall(hl, th, edges=[roller2, "f", RollerEdge(self, None), "f"], callback=[
            self.holderTopCB], move="up")
        self.rectangularWall(hl, 20-t, edges="feee", move="up")
        tl = 70
        self.rectangularWall(tl, hw+20, edges="FeFF", move="right",
                             callback=[None, lambda:self.fingerHolesAt(20-0.5*t,0, tl)])
        self.rectangularWall(tl, hw+20, edges="FeFF", move="",
                             callback=[None, lambda:self.fingerHolesAt(20-0.5*t,0, tl)])
        self.rectangularWall(tl, hw+20, edges="FeFF", move="left up only",
                             callback=[None, lambda:self.fingerHolesAt(20-0.5*t,0, tl)])

        # Links
        self.link(hl-40, 25, a, True, move="up")
        self.link(hl-40, 25, a, True, move="up")
        self.link(hl-40, 25, a, True, move="up")
        self.link(hl-40, 25, a, True, move="up")

        self.ctx.save()
        self.rectangularWall(hw-2*t-2, 60, edges="efef",move="right")
        self.rectangularWall(hw-4*t-4, 60, edges="efef",move="right")
        # Spindel auxiliaries 
        self.parts.waivyKnob(50, callback=lambda:self.nutHole("M8"), move="right")
        self.parts.waivyKnob(50, callback=lambda:self.nutHole("M8"), move="right")
        self.ctx.restore()
        self.rectangularWall(hw-2*t-4, 60, edges="efef",move="up only")

        self.ctx.save()
        slot = edges.SlottedEdge(self, [(30-t)/2, (30-t)/2], slots=15)
        self.rectangularWall(30, 30, edges=["e", "e", slot, "e"],
            callback=[lambda:self.hole(7, 23, self.axle/2)], move="right")
        self.rectangularWall(30, 30, edges=["e", "e", slot, "e"],
            callback=[lambda:self.hole(7, 23, self.axle/2)], move="right")
        slot = edges.SlottedEdge(self, [10, 20, 10], slots=15)
        self.rectangularWall(40+2*t, 30, edges=[slot, "e", "e", "e"],
            callback=[lambda:self.hole(20+t, 15, 4)], move="right")
        for i in range(3):
            self.rectangularWall(20, 30,
            callback=[lambda:self.nutHole("M8", 10, 15)], move="right")
        self.rectangularWall(20, 30,
            callback=[lambda:self.hole(10, 15, 4)], move="right")
            
        self.ctx.restore()
        self.rectangularWall(30, 30, move="up only")
        # Other side
        ow = 10
        self.rectangularWall(3.6*d, 1.1*d, edges="hfFf", callback=[
            lambda:self.rectangularHole(1.8*d, 3.6, 32, 7.1)], move="up")
        self.rectangularWall(3.6*d, 1.1*d, edges="hfFf", callback=[
            lambda:self.rectangularHole(1.8*d, 3.6, 32, 7.1)], move="up")
        self.rectangularWall(3.6*d, ow, edges="ffff", move="up")
        self.rectangularWall(3.6*d, ow, edges="ffff", move="up")
        self.ctx.save()
        self.rectangularWall(ow, 1.1*d, edges="hFFH", move="right")
        self.rectangularWall(ow, 1.1*d, edges="hFFH", move="right")
        self.ctx.restore()
        self.rectangularWall(ow, 1.1*d, edges="hFFH", move="up only")
        
        # Motor block
        mw = 40
        self.rectangularWall(3.6*d, 1.1*d, edges=["h", "f", MotorEdge(self, None),"f"], callback=[self.mainPlate], move="up")
        self.rectangularWall(3.6*d, 1.1*d, edges=["h", "f", MotorEdge(self, None),"f"], callback=[self.frontPlate], move="up")
        self.rectangularWall(3.6*d, mw, edges="ffff", move="up")
        self.ctx.save()
        self.rectangularWall(mw, 1.1*d, edges="hFeH", move="right")
        self.rectangularWall(mw, 1.1*d, edges="hFeH", move="right")

        self.pulley(88, "GT2_2mm", r_axle=a/2.0,move="right")
        self.pulley(88, "GT2_2mm", r_axle=a/2.0,move="right")
        self.ctx.restore()
        self.rectangularWall(mw, 1.1*d, edges="hFeH", move="up only")
        self.axle = 19
        for i in range(3):
            self.parts.disc(self.diameter-2*self.rubberthickness,
                            hole=self.axle, move="right")
        self.parts.disc(self.diameter-2*self.rubberthickness,
                        hole=self.axle, move="up right")
        for i in range(3):
            self.parts.disc(self.diameter-2*self.rubberthickness,
                            hole=self.axle, move="left")
        self.parts.disc(self.diameter-2*self.rubberthickness,
                        hole=self.axle, move="left up")
        for i in range(3):
            self.parts.disc(self.diameter-2*self.rubberthickness+4,
                            hole=self.axle, move="right")
        self.parts.disc(self.diameter-2*self.rubberthickness+4,
                        hole=self.axle, move="right up")

        self.close()

def main():
    b = Box()
    b.parseArgs()
    b.render()

if __name__ == '__main__':
    main()
