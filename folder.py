#!/usr/bin/python

from boxes import *
import math

class Folder(Boxes):

    def __init__(self, x, y, h, r=0):
        Boxes.__init__(self, width=2*x+3*h+20, height=y+20)
        self.x = x
        self.y = y
        self.h = h
        self.r = r

    def render(self):
        x, y, r, h = self.x, self.y, self.r, self.h
        c2 = math.pi * h
        self.moveTo(r+self.thickness, self.thickness)
        self.edge(x-r)
        self.flexEdge(c2, y)
        self.edge(x-r)
        self.corner(90, r)
        self.edge(y-2*r)
        self.corner(90, r)
        self.edge(2*x-2*r+c2)
        self.corner(90, r)
        self.edge(y-2*r)
        self.corner(90, r)
        
        self.ctx.stroke()
        self.surface.flush()
        self.surface.finish()

f = Folder(240, 350, 20, 15)
f.render()
