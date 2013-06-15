#!/usr/bin/python

from boxes import *

class Box(Boxes):
    def __init__(self, x, y, h):
        self.x, self.y, self.h = x, y, h
        Boxes.__init__(self, width=x+y+40, height=y+2*h+50)

    def render(self):
        x, y, h = self.x, self.y, self.h
        t = self.thickness

        d2 = Bolts(2)
        d3 = Bolts(3)

        self.moveTo(t, t)
        self.rectangularWall(x, h, "FfeF", bedBolts=[d2])
        self.moveTo(x+3*t, 0)
        self.rectangularWall(y, h, "FfeF", bedBolts=[d3])
        self.moveTo(-x-3*t, h+3*t)

        self.rectangularWall(x, h, "FfeF", bedBolts=[d2])
        self.moveTo(x+3*t, 0)
        self.rectangularWall(y, h, "FfeF", bedBolts=[d3])
        self.moveTo(-x-2*t, h+5*t)
        
        self.rectangularWall(x, y, "ffff", bedBolts=[d2, d3, d2, d3])

        self.ctx.stroke()
        self.surface.flush()


b = Box(100, 150, 70)
b.render()
