#!/usr/bin/python

from boxes import *
import math

class FlexBox(Boxes):
    def __init__(self, x, y, z, r=None, thickness=3.0):
        self.x = x
        self.y = y
        self.z = z
        self.r = r or min(x, y)/2.0
        self.c4 = c4 = math.pi * r * 0.5
        self.latchsize = 8*thickness

        width = 2*x + y - 3*r + 2*c4 + 6*thickness + self.latchsize # lock
        height = y + z + 8*thickness

        Boxes.__init__(self, width, height, thickness=thickness)
        
    @restore
    def flexBoxSide(self, x, y, r, callback=None):
        self.cc(callback, 0)
        self.fingerJoint(x)
        self.corner(90, 0)
        self.cc(callback, 1)
        self.fingerJoint(y-r)
        self.corner(90, r)
        self.cc(callback, 2)
        self.edge(x-2*r)
        self.corner(90, r)
        self.cc(callback, 3)
        self.latch(self.latchsize)
        self.cc(callback, 4)
        self.fingerJoint(y-r-self.latchsize)
        self.corner(90)

    def surroundingWall(self):
        x, y, z, r = self.x, self.y, self.z, self.r
        
        self.fingerJoint(y-r, False)
        self.flex(self.c4, z+2*self.thickness)
        self.edge(x-2*r)
        self.flex(self.c4, z+2*self.thickness)
        self.latch(self.latchsize, False)
        self.edge(z+2*self.thickness)
        self.latch(self.latchsize, False, True)
        self.edge(self.c4)
        self.edge(x-2*r)
        self.edge(self.c4)
        self.fingerJoint(y-r, False)        
        self.corner(90)
        self.edge(self.thickness)
        self.fingerJoint(z)
        self.edge(self.thickness)
        self.corner(90)

    def render(self):
        self.moveTo(2*self.thickness, self.thickness)
        self.ctx.save()
        self.surroundingWall()
        self.moveTo(self.x+self.y-3*self.r+2*self.c4+self.latchsize+1*self.thickness, 0)
        self.rectangularWall(self.x, self.z, edges="FFFF")
        self.ctx.restore()
        self.moveTo(0, self.z+4*self.thickness)
        self.flexBoxSide(self.x, self.y, self.r)
        self.moveTo(2*self.x+3*self.thickness, 0)
        self.ctx.scale(-1, 1)
        self.flexBoxSide(self.x, self.y, self.r)
        self.ctx.scale(-1, 1)
        self.moveTo(2*self.thickness, 0)
        self.rectangularWall(self.z, self.y-self.r-self.latchsize, edges="fFeF")
        self.ctx.stroke()
        self.surface.flush()


if __name__=="__main__":
    b = FlexBox(200, 200, 200, r=50)
    b.render()
