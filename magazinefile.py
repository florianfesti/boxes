#!/usr/bin/python

from boxes import *

class Box(Boxes):
    def __init__(self, x, y, h, h2):
        self.x, self.y, self.h, self.h2 = x, y, h, h2
        Boxes.__init__(self, width=x+y+40, height=y+2*h+50,
                       thickness=4.0)

    def side(self, w, h, h2):
        r = min(h-h2, w) / 2.0
        if (h-h2) > w:
            r = w / 2.0
            lx = 0
            ly = (h-h2) - w
        else:
            r = (h - h2) / 2.0
            lx = (w - 2*r) / 2.0
            ly = 0

        e_w = self.edges["F"].width()
        self.moveTo(3, 3)
        self.edge(e_w)
        self.edges["F"](w)
        self.edge(e_w)
        self.corner(90)
        self.edge(e_w)
        self.edges["F"](h2)
        self.corner(90)
        self.edge(e_w)
        self.edge(lx)
        self.corner(-90, r)
        self.edge(ly)
        self.corner(90, r)
        self.edge(lx)        
        self.edge(e_w)
        self.corner(90)
        self.edges["F"](h)
        self.edge(e_w)
        self.corner(90)


    def render(self):
        x, y, h, h2 = self.x, self.y, self.h, self.h2
        t = self.thickness

        self.ctx.save()
        self.rectangularWall(x, h, "Ffef", move="up")
        self.rectangularWall(x, h2, "Ffef", move="up")

        self.rectangularWall(y, x, "ffff")
        self.ctx.restore()

        self.rectangularWall(x, h, "Ffef", move="right only")
        self.side(y, h, h2)
        self.moveTo(y+15, h+h2+15, 180)
        self.side(y, h, h2)

        self.ctx.stroke()
        self.surface.flush()
        self.surface.finish()

b = Box(80, 235, 300, 150)
b.edges["f"].settings.setValues(b.thickness, space=2, finger=2)
b.render()
