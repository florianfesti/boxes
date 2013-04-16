#!/usr/bin/python

from boxes import Boxes

class Lamp(Boxes):
    def __init__(self):
        Boxes.__init__(self, width=1000, height=800)
        self.fingerJointSettings = (5, 5)

    def ring(self, r, w):
        self.ctx.save()
        d = 2*(r+w)
        self.roundedPlate(d, d, r)

        self.moveTo(r+w, w)
        self.corner(360, r)
        self.ctx.restore()

    def base(self, r, w):
        self.ctx.save()
        d = 2*(r+w)
        self.roundedPlate(d, d, r)
        self.moveTo(0, 0)
        self.hexHolesHex(2*(r+w), 5, 3, grow='space')
        self.ctx.restore()

    def side(self, r, w, h):
        self.fingerHoleEdge(w/2.0, 5)
        for i in range(4):
            self.flex(r*0.5*math.pi, h)
            if i < 3:
                self.fingerHoleEdge(w, 5)
        self.fingerHoleEdge(w/2.0, 5)

        self.corner(90)
        self.edge(5)
        self.doveTailJoint(h-10)
        self.edge(5)
        self.corner(90)

        self.fingerHoleEdge(w/2.0, 5)
        for i in range(4):
            self.edge(r*0.5*math.pi)
            if i < 3:
                self.fingerHoleEdge(w, 5)
        self.fingerHoleEdge(w/2.0, 5)

        self.corner(90)
        self.edge(5)
        self.doveTailJoint(h-10, positive=False)
        self.edge(5)
        self.corner(90)

        self.side(r, w, 150)
        self.moveTo(0, 150+40)

    def render(self, r, w):
        """
        r : radius of lamp
        w : width of surrounding ring
        """
        d = 2*(r+w)
        self.ctx.save()
        self.moveTo(20, 20)
        self.ring(r, w)
        self.moveTo(2*(r+w)+20, 0)
        self.base(r, w)

        self.ctx.restore()
        self.moveTo(10, 2*(r+w)+40)
        self.surroundingWall(d, d, r, 150)

        self.moveTo(0, 270)

        #self.hexHolesHex(200, 20, 5)
        #self.hexHolesRectangle(400, 200, 20, 5)

        self.ctx.stroke()
        self.surface.flush()


l = Lamp()
l.render(100, 20)
