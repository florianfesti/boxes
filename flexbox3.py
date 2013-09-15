#!/usr/bin/python

from boxes import *
import math

class FlexBox(Boxes):
    def __init__(self, x, y, z, r=None, d=1.0, h=5.0, thickness=3.0):
        self.x = x
        self.y = y
        self.z = z
        self.r = r or min(x, y)/2.0
        self.d = d
        self.h = h
        self.c4 = c4 = math.pi * r * 0.5 * 0.95
        self.latchsize = 8*thickness

        width = 2*x + y - 3*r + 2*c4 + 15*thickness + 3*10 # lock
        height = y + z + 8*thickness

        Boxes.__init__(self, width, height, thickness=thickness)
        self.edges["f"].settings.setValues(
            self.thickness, finger=2, space=2, surroundingspaces=1)

        s = FingerJointSettings(self.thickness, surroundingspaces=1)
        g = FingerJointEdge(self, s)
        g.char = "g"
        self.addPart(g)
        G = FingerJointEdgeCounterPart(self, s)
        G.char = "G"
        self.addPart(G)
        
    def rectangleCorner(self, edge1=None, edge2=None):
        edge1 = self.edges.get(edge1, edge1)
        edge2 = self.edges.get(edge2, edge2)
        if edge2:
            self.edge(edge2.width())
        self.corner(90)
        if edge1:
            self.edge(edge1.width())

    @restore
    def flexBoxSide(self, x, y, r, callback=None):
        self.cc(callback, 0)
        self.fingerJointEdge(x)
        self.corner(90, 0)
        self.cc(callback, 1)
        self.fingerJointEdge(y-r)
        self.corner(90, r)
        self.cc(callback, 2)
        self.edge(x-r)
        self.corner(90, 0)
        self.cc(callback, 3)
        self.fingerJointEdge(y)
        self.corner(90)

    def surroundingWall(self):
        x, y, z, r, d = self.x, self.y, self.z, self.r, self.d
        
        self.edges["F"](y-r, False)
        self.flexEdge(self.c4, z+2*self.thickness)
        self.corner(-90)
        self.edge(d)
        self.corner(90)
        self.edges["f"](x-r+d)
        self.corner(90)
        self.edges["f"](z+2*self.thickness+2*d)
        self.corner(90)
        self.edges["f"](x-r+d)
        self.corner(90)
        self.edge(d)
        self.corner(-90)
        self.edge(self.c4)
        self.edges["F"](y-r)
        self.corner(90)
        self.edge(self.thickness)
        self.edges["f"](z)
        self.edge(self.thickness)
        self.corner(90)

    @restore
    def lidSide(self):
        x, y, z, r, d, h = self.x, self.y, self.z, self.r, self.d, self.h
        t = self.thickness
        r2 = r+t if r+t <=h+t else h+t
        self.moveTo(self.thickness, self.thickness)
        self.edge(h+self.thickness-r2)
        self.corner(90, r2)
        self.edge(r-r2+2*t)
        self.edges["F"](x-r)
        self.rectangleCorner("F", "f")
        self.edges["g"](h)
        self.rectangleCorner("f", "e")
        self.edge(x+2*t)

    def render(self):
        x, y, z, r, d, h = self.x, self.y, self.z, self.r, self.d, self.h

        self.moveTo(2*self.thickness, self.thickness+2*d)
        self.ctx.save()
        self.surroundingWall()
        self.moveTo(x+y-2*r+self.c4+self.thickness, -2*d-self.thickness)
        self.rectangularWall(x, z, edges="FFFF", move="right")
        self.rectangularWall(h, z+2*(d+self.thickness),
                             edges="GeGF", move="right")
        self.lidSide()
        self.moveTo(2*h+5*self.thickness, 0)
        self.ctx.scale(-1, 1)
        self.lidSide()

        self.ctx.restore()
        self.moveTo(0, z+4*self.thickness+2*d)
        self.flexBoxSide(x, y, r)
        self.moveTo(2*x+3*self.thickness, 2*d)
        self.ctx.scale(-1, 1)
        self.flexBoxSide(x, y, r)
        self.ctx.scale(-1, 1)
        self.moveTo(2*self.thickness, -self.thickness)
        self.rectangularWall(z, y, edges="fFeF")
        self.ctx.stroke()
        self.surface.finish()


if __name__=="__main__":
    b = FlexBox(100, 40, 100, r=20, h=10, thickness=4.0)
    b.render()
