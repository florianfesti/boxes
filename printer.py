#!/usr/bin/python
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

class Printer(Boxes):

    """Work in progress"""
    def __init__(self, r=250, h=400, d_c=100):
        Boxes.__init__(self, 650, 600, thickness=5.0, burn=0.05)
        self.edges["f"].settings.setValues(self.thickness, surroundingspaces=0)
        self.r = r
        self.h = h
        self.d_c = d_c
        # idlers
        self.D_i = 17.0
        self.d_i = 5.0
        self.w_i = 7.0 # includes washers


    def mainPlate(self, nr):
        r = self.r
        t2 = 0.5 * self.thickness
        if nr:
            return
        self.moveTo(r-5, r, -90)
        self.hole(0, 0, r-80)

        D_i2 = self.D_i / 2
        w_i2 = self.w_i / 2

        d_c2 = self.d_c/2
        for i in range(6):
            self.ctx.save()
            self.moveTo(0, 0, i*60)
            # winches
            if i % 2:
                self.fingerHolesAt(r-80, (d_c2+20), 70, angle=0)
                self.fingerHolesAt(r-80, -(d_c2+20), 70, angle=0)
                if i==5:
                    self.fingerHolesAt(r-70+t2, -(d_c2+20+t2), 40, angle=-90)
                else:
                    self.fingerHolesAt(r-70+t2, (d_c2+20+t2), 40, angle=90)
            # idler buck
            else:
                d = 0.5*(self.thickness)+w_i2
                for y in (-d-d_c2, d-d_c2, -d+d_c2, d+d_c2):
                    self.fingerHolesAt(r-30, y, 30, angle=0)
                self.hole(r-15+D_i2, -self.d_c/2, 0.4)
                self.hole(r-15+D_i2, self.d_c/2, 0.4)
            self.ctx.restore()


    def head(self):
        d_c = self.d_c

        self.moveTo(self.spacing+10, self.spacing)
        for i in range(3):
            self.hole(0, 5, 0.3)
            self.fingerHolesAt(25, 0, 20)
            self.fingerHolesAt(75, 0, 20)
            self.edge(d_c)
            self.hole(0, 5, 0.3)
            self.corner(120, 10)


    def support(self, x, y, edges="ff", pair=False, callback=None, move=None):
        if len(edges) != 2:
            raise ValueError("Two edges required")
        edges = [self.edges.get(e, e,) for e in edges]

        overallwidth = x + edges[0].spacing() + self.edges["e"].spacing()
        overallheight = y + edges[1].spacing() + self.edges["e"].spacing()

        r = 2*self.thickness

        if pair:
            overallwidth+= edges[0].spacing() + r - self.edges["e"].spacing()
            overallheight+= edges[1].spacing() + r - self.edges["e"].spacing()

        if self.move(overallwidth, overallheight, move, before=True):
            return

        self.ctx.save()
        self.moveTo(edges[0].margin(), edges[1].margin())

        angle = math.degrees(math.atan((y-r)/float(x-r)))

        self.cc(callback, 0)
        edges[1](x)
        self.corner(90)
        #self.edge(self.thickness)
        self.corner(90-angle, r)
        self.edge(((x-r)**2+(y-r)**2)**0.5)
        self.corner(angle, r)
        #self.edge(self.thickness)
        self.corner(90)
        self.cc(callback, 0)
        edges[0](y)
        self.corner(90)
        self.ctx.restore()

        if pair:
            self.ctx.save()
            self.moveTo(overallwidth, overallheight, 180)
            self.support(x, y, edges, False, callback)
            self.ctx.restore()

        self.move(overallwidth, overallheight, move)

    def render(self):
        self.ctx.save()
        for i in range(3):
            # motor mounts
            self.rectangularWall(70, 70, edges="feee", callback=[
                    lambda: self.NEMA(23, 35, 35),],
                                 move="right")
            # winch bucks
            self.rectangularWall(50, 70, edges="efee", callback=[
                    None,
                    lambda: self.hole(35, 35, 8.5),
                    None,
                    lambda: self.fingerHolesAt(10, 0, 50)], move="right")
        self.support(40, 50, move="right", pair=True)
        self.support(40, 50, move="right")
        self.ctx.restore()
        self.moveTo(0, 80)
        self.ctx.save()
        # idler bucks
        for i in range(12):
            self.rectangularWall(30, 30, edges="feee", callback=[
                    lambda: self.hole(15, 15, 3),], move="right")
        # Cable adjustment blocks
        self.ctx.save()
        for i in range(6):
            def holes():
                self.hole(5, 4, 1.5)
                self.hole(15, 4, 1.5)
            self.rectangularWall(20, 8, edges="feee", callback=[holes,],
                                 move="right")
        self.ctx.restore()
        self.moveTo(0, 20)
        # Cable adjustment glyders
        for i in range(6):
            self.rectangularWall(8, 10, move="right", callback=[
                    lambda: self.hole(4, 4, 1.5),
                    None,
                    lambda: self.hole(4, 1.5, 0.4)])
            self.rectangularWall(8, 10, move="right", callback=[
                    lambda: self.nutHole("M3", 4, 4),
                    None,
                    lambda: self.hole(4, 1.5, 0.4)])

        self.ctx.restore()
        self.moveTo(0, 40)

        # mainPlate
        self.rectangularWall(2*self.r-10, 2*self.r-10, edges="ffff",
                             callback=self.mainPlate, move="right")
                        
        self.head()
        self.close()

p = Printer()
p.render()
