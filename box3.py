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
        self.rectangularWall(y, h, "Feef", bedBolts=d3, move="up")
        self.rectangularWall(y, h, "Feef", bedBolts=d3)
        #self.rectangularWall(x, h, "FFeF", bedBolts=d2, move="left up")
        
        self.rectangularWall(x, y, "efff", bedBolts=[d2, d3, d2, d3], move="left")
        #self.rectangularWall(x, y, "ffff", bedBolts=[d2, d3, d2, d3])

        self.ctx.stroke()
        self.surface.flush()
        self.surface.finish()

t = 6.0
b = Box(380-2*t, 370-2*t, 120-t, thickness=t)
b.edges["f"].settings.setValues(b.thickness, space=3, finger=3,
                                surroundingspaces=1)
b.render()
