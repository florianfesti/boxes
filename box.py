#!/usr/bin/python

from boxes import *

class Box(Boxes):
    def __init__(self, x, y, h, **kw):
        self.x, self.y, self.h = x, y, h
        Boxes.__init__(self, width=x+y+40, height=y+2*h+50, **kw)

    def render(self):
        x, y, h = self.x, self.y, self.h
        t = self.thickness

        d2 = [Bolts(2)]
        d3 = [Bolts(3)]

        d2 = d3 = None

        self.moveTo(t, t)
        self.rectangularWall(x, h, "FFeF", bedBolts=d2, move="right")
        self.rectangularWall(y, h, "Ffef", bedBolts=d3, move="up")
        self.rectangularWall(y, h, "Ffef", bedBolts=d3)
        self.rectangularWall(x, h, "FFeF", bedBolts=d2, move="left up")
        
        self.rectangularWall(x, y, "ffff", bedBolts=[d2, d3, d2, d3])

        self.ctx.stroke()
        self.surface.flush()
        self.surface.finish()

b = Box(200, 200, 200, thickness=4.0)
b.edges["f"].settings.setValues(b.thickness, space=3, finger=3,
                                surroundingspaces=1)
b.render()
