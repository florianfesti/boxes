#!/usr/bin/python

from boxes import Boxes

class Lamp(Boxes):
    def __init__(self):
        Boxes.__init__(self, width=1000, height=1000)
        self.fingerJointSettings = (5, 5)

    def ring(self, r, w):
        self.ctx.save()
        d = 2*(r+w)
        self.roundedPlate(d, d, r)

        self.moveTo(r+w, w)
        self.corner(360, r)
        self.ctx.restore()

    def holder(self, l):
        self.ctx.line_to(l/2.0,-l/2.0)
        self.ctx.line_to(l, 0)
        self.moveTo(l, 0)

    def render(self, r, w, x, y, h):
        """
        r : radius of lamp
        w : width of surrounding ring
        """
        d = 2*(r+w)
        self.ctx.save()
        self.moveTo(20, 20)
        self.ring(r, w)
        self.moveTo(2*(r+w)+20, 0)
        self.roundedPlate(d, d, r, holesMargin=w/2.0)

        self.ctx.restore()
        self.moveTo(10, 2*(r+w)+40)
        self.surroundingWall(d, d, r, 150, top='h', bottom='h')
        self.moveTo(0, 150+20)

        self.rectangularWall(x, y, edges="fFfF", holesMargin=5)
        self.moveTo(x+20, 0)
        self.rectangularWall(x, y, edges="fFfF", holesMargin=5)
        self.moveTo(x+20, 0)
        self.rectangularWall(y, h, edges="ffff", holesMargin=5)

        self.moveTo(0, y+20)
        self.rectangularWall(y, h, edges="ffff", holesMargin=5)
        self.moveTo(-x-20, 0)
        self.rectangularWall(x, h, edges=['h', 'F', (self.holder, 20), 'F'], holesMargin=5)
        self.moveTo(-x-20, 0)
        self.rectangularWall(x, h, edges='hFFF', holesMargin=5)

        self.ctx.stroke()
        self.surface.flush()


l = Lamp()
l.render(100, 20, 250, 140, 120)
