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
        self.rectangularWall(x, h, "FfeF", bedBolts=[d2], move="right")
        self.rectangularWall(y, h, "FfeF", bedBolts=[d3], move="up")
        self.rectangularWall(y, h, "FfeF", bedBolts=[d3])
        self.rectangularWall(x, h, "FfeF", bedBolts=[d2], move="left up")
        
        self.rectangularWall(x, y, "ffff", bedBolts=[d2, d3, d2, d3])

        self.ctx.stroke()
        self.surface.flush()
        self.surface.finish()

b = Box(100, 150, 70)
b.edges["f"].settings.setValues(b.thickness, space=3, finger=2)
b.render()
