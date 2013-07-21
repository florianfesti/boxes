#!/usr/bin/python

from boxes import *

class Printer(Boxes):

    """Work in progress"""
    def __init__(self, r=250, h=400, d_c=100):
        Boxes.__init__(self, 1000, 800, thickness=5.0, burn=0.05)
        self.r = r
        self.h = h
        self.d_c = d_c
        # idler
        self.D_i = 22.0
        self.d_i = 8.0
        self.w_i = 5.0 # includes washers


    def mainPlate(self, nr):
        r = self.r
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
            self.fingerHolesAt(25, 0, 25)
            self.fingerHolesAt(75, 0, 25)
            self.edge(d_c)
            self.hole(0, 5, 0.3)
            self.corner(120, 10)

    def render(self):
        self.ctx.save()
        for i in range(3):
            # motor mounts
            self.rectangularWall(70, 70, edges="feee", callback=[
                    lambda: self.NEMA(23, 35, 35),],
                                 move="right")
            # winch bucks
            self.rectangularWall(70, 50, edges="feee", callback=[
                    lambda: self.hole(35, 35, 8.5),], move="right")
        self.ctx.restore()
        self.moveTo(0, 90)
        self.ctx.save()
        # idler bucks
        for i in range(12):
            self.rectangularWall(30, 30, edges="feee", callback=[
                    lambda: self.hole(15, 15, 3),], move="right")

        for i in range(6):
            def holes():
                self.hole(3, 3, 1.5)
                self.hole(8, 3, 1.5)
            self.rectangularWall(25, 6, edges="feee", callback=[holes,],
                                 move="right")
        self.ctx.restore()
        self.moveTo(0, 40)

        self.rectangularWall(2*self.r-10, 2*self.r-10, edges="ffff",
                             callback=self.mainPlate, move="right")
                        
        self.head()

        self.ctx.stroke()
        self.surface.finish()

p = Printer()
p.render()
