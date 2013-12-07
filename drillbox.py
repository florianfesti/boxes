#!/usr/bin/python

from boxes import *

class Box(Boxes):
    def __init__(self, x, y, h, **kw):
        self.x, self.y, self.h = x, y, h
        Boxes.__init__(self, width=x+y+40, height=3*y+2*h+50, **kw)


    def holesx(self):
        self.fingerHolesAt(0, 5, self.x, angle=0)
        self.fingerHolesAt(0, 25, self.x, angle=0)

    def holesy(self):
        self.fingerHolesAt(0, 5, self.y, angle=0)
        self.fingerHolesAt(0, 25, self.y, angle=0)


    def drillholes(self):
        for i in range(6):
            for j in range(4):
                for k in range(3):
                    r = (12.5-2*i-0.5*j) * 0.5
                    self.hole(i*20+10, j*60+k*20+10, r+0.05)

    def description(self):
        self.ctx.set_font_size(6)
        for i in range(4):
            for j in range(6):
                self.rectangularHole(i*60+30, 20*j+10, 58, 14+1*j)
                self.ctx.save()
                self.ctx.move_to(i*60+14, 19*j+6)
                d = 2.5-0.5*i+2*j
                self.ctx.scale(1,-1)
                self.ctx.show_text("%.1f" % d)
                self.ctx.restore()

    def render(self):
        x, y, h = self.x, self.y, self.h
        t = self.thickness

        self.moveTo(t, t)
        self.rectangularWall(x, h, "FfeF", callback=[self.holesx],move="right")
        self.rectangularWall(y, h, "FfeF", callback=[self.holesy], move="up")
        self.rectangularWall(y, h, "FfeF", callback=[self.holesy])
        self.rectangularWall(x, h, "FfeF", callback=[self.holesx],
                             move="left up")
        
        self.rectangularWall(x, y, "ffff", move="up")
        self.rectangularWall(x, y, "ffff", callback=[self.drillholes],
                             move="up")
        self.rectangularWall(x, y, "ffff", callback=[self.drillholes,
                                                     self.description],
                             move="up")

        self.ctx.stroke()
        self.surface.flush()
        self.surface.finish()

b = Box(120, 240, 60, thickness=4.0)
b.edges["f"].settings.setValues(b.thickness, space=3, finger=3,
                                surroundingspaces=1)
b.render()
