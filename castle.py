#!/usr/bin/python
from boxes import *

class Castle(Boxes):

    def __init__(self):
        Boxes.__init__(self, 800, 600)
        s = FingerJointSettings(self.thickness, relative=False,
                                space = 10, finger=10, height=10,
                                width=self.thickness)
        p = FingerJointEdge(self, s)
        p.char = "p"
        self.addPart(p)
        P = FingerJointEdgeCounterPart(self, s)
        P.char = "P"
        self.addPart(P)

    def render(self, t_x=70, t_h=250, w1_x=300, w1_h=120, w2_x=100, w2_h=120):
        self.moveTo(0,0)
        self.rectangularWall(t_x, t_h, edges="efPf", move="right", callback=
            [lambda: self.fingerHolesAt(t_x*0.5, 0, w1_h, 90),])
        self.rectangularWall(t_x, t_h, edges="efPf", move="right")
        self.rectangularWall(t_x, t_h, edges="eFPF", move="right", callback=
            [lambda: self.fingerHolesAt(t_x*0.5, 0, w2_h, 90),])
        self.rectangularWall(t_x, t_h, edges="eFPF", move="right")

        self.rectangularWall(w1_x, w1_h, "efpe", move="right")
        self.rectangularWall(w2_x, w2_h, "efpe", move="right")

        self.ctx.stroke()
        self.surface.finish()


c = Castle()
c.render()
