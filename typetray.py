#!/usr/bin/python

from boxes import *

class BottomEdge(FingerJointEdge):
    def __init__(self, boxes, sections, slot=0):
        FingerJointEdge.__init__(self, boxes, None)
        self.sections = sections
        self.slot = slot

    def _slot(self):
        if self.slot:
            self.boxes.corner(90)
            self.boxes.edge(self.slot)
            self.boxes.corner(-90)
            self.boxes.edge(self.thickness)
            self.boxes.corner(-90)
            self.boxes.edge(self.slot)
            self.boxes.corner(90)
        else:
            self.boxes.edge(self.thickness)

    def __call__(self, l, **kw):
        for x in self.sections[:-1]:
            self.boxes.fingerJointEdge(x)
            self._slot()
        self.boxes.fingerJointEdge(self.x[-1])

class TopEdge(BottomEdge):
    

    margin = Edge.margin
    width = Edge.width

    def __call__(self, l, **kw):
        for x in self.sections[:-1]:
            self.boxes.edge(x)
            self._slot()
        self.boxes.edge(self.x[-1])

class TypeTray(Boxes):
    def __init__(self, x, y, h, **kw):
        self.x, self.y, self.h = x, y, h
        Boxes.__init__(self, width=sum(x)+sum(y)+50, height=sum(y)+2*h+50, **kw)

    def xSlots(self):
        posx = -0.5 * self.thickness
        for x in self.x[:-1]:
            posx += x + self.thickness
            posy = 0
            for y in self.y:
                self.fingerHolesAt(posx, posy, y)
                posy += y + self.thickness

    def ySlots(self):
        posy = -0.5 * self.thickness
        for y in self.y[:-1]:
            posy += y + self.thickness
            posx = 0
            for x in self.x:
                self.fingerHolesAt(posy, posx, x)
                posx += x + self.thickness

    def xHoles(self):
        posx = -0.5 * self.thickness
        for x in self.x[:-1]:
            posx += x + self.thickness
            self.fingerHolesAt(posx, 0, self.h)

    def yHoles(self):
        posy = -0.5 * self.thickness
        for y in self.y[:-1]:
            posy += y + self.thickness
            self.fingerHolesAt(posy, 0, self.h)


    def render(self):
        x = sum(self.x) + self.thickness * (len(self.x)-1)
        y = sum(self.y) + self.thickness * (len(self.y)-1)
        h = self.h
        t = self.thickness

        self.moveTo(t, t)
        self.rectangularWall(x, h, "Ffef", callback=[self.xHoles,],
                             move="right")
        self.rectangularWall(y, h, "FFeF",  callback=[self.yHoles,],
                             move="up")
        self.rectangularWall(y, h, "FFeF", callback=[self.yHoles,])
        self.rectangularWall(x, h, "Ffef", callback=[self.xHoles,],
                             move="left up")
        
        self.rectangularWall(x, y, "ffff",
                             callback=[self.xSlots, self.ySlots],
                             move="right")

        for i in range(len(self.x)-1):
            e = [BottomEdge(self, self.y, 0.5*h), "f", "e", "f"]
            self.rectangularWall(y, h, e,
                                 move="up")
        for i in range(len(self.y)-1):
            e = [BottomEdge(self, self.x), "f",
                 TopEdge(self, self.x, 0.5*h), "f"]
            self.rectangularWall(x, h, e,
                                 move="up")

        self.ctx.stroke()
        self.surface.flush()
        self.surface.finish()

b = TypeTray([100, 100], [50, 50, 100, 100], 50, thickness=4.0)
b.edges["f"].settings.setValues(b.thickness, space=3, finger=3,
                                surroundingspaces=1)
b.render()
