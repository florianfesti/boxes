#!/usr/bin/python3
# Copyright (C) 2013-2014 Florian Festi
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from boxes import *

class TypeTray(Boxes):
    def __init__(self):
        Boxes.__init__(self)
        self.buildArgParser("sx", "sy", "h", "hi")

    def xSlots(self):
        posx = -0.5 * self.thickness
        for x in self.sx[:-1]:
            posx += x + self.thickness
            posy = 0
            for y in self.sy:
                self.fingerHolesAt(posx, posy, y)
                posy += y + self.thickness

    def ySlots(self):
        posy = -0.5 * self.thickness
        for y in self.sy[:-1]:
            posy += y + self.thickness
            posx = 0
            for x in self.sx:
                self.fingerHolesAt(posy, posx, x)
                posx += x + self.thickness

    def xHoles(self):
        posx = -0.5 * self.thickness
        for x in self.sx[:-1]:
            posx += x + self.thickness
            self.fingerHolesAt(posx, 0, self.hi)

    def yHoles(self):
        posy = -0.5 * self.thickness
        for y in self.sy[:-1]:
            posy += y + self.thickness
            self.fingerHolesAt(posy, 0, self.hi)

    def fingerHole(self):
        dx = 50
        dy = 30
        x = sum(self.sx) + self.thickness * (len(self.sx)-1)
        self.moveTo(0.5*(x-dx), 5)
        self.edge(dx)
        self.corner(180, 0.5*dy)
        self.edge(dx)
        self.corner(180, 0.5*dy)
        #self.hole(0.5*x-30, 15, 10)
        #self.hole(0.5*x+30, 15, 10)

    def render(self):
        x = sum(self.sx) + self.thickness * (len(self.sx)-1)
        y = sum(self.sy) + self.thickness * (len(self.sy)-1)
        h = self.h
        hi = self.hi = self.hi or h
        t = self.thickness

        self.open(width=x+y+10*t, height=y+(len(self.sx)+len(self.sy))*h+50)
        self.edges["f"].settings.setValues(self.thickness, space=3, finger=3,
                                           surroundingspaces=0.5)

        self.moveTo(t, t)
        # outer walls
        self.rectangularWall(x, h, "Ffef", callback=[
            self.xHoles, None, self.fingerHole],
                             move="right")
        self.rectangularWall(y, h, "FFeF",  callback=[self.yHoles,],
                             move="up")
        self.rectangularWall(y, h, "FFeF", callback=[self.yHoles,])
        self.rectangularWall(x, h, "Ffef", callback=[self.xHoles,],
                             move="left up")
        
        # floor
        self.rectangularWall(x, y, "ffff",
                             callback=[self.xSlots, self.ySlots],
                             move="right")
        # Inner walls
        for i in range(len(self.sx)-1):
            e = [SlottedEdge(self, self.sy, "f", slots=0.5*hi), "f", "e", "f"]
            self.rectangularWall(y, hi, e,
                                 move="up")
        for i in range(len(self.sy)-1):
            e = [SlottedEdge(self, self.sx, "f"), "f",
                 SlottedEdge(self, self.sx[::-1], "e", slots=0.5*hi), "f"]
            self.rectangularWall(x, hi, e,
                                 move="up")
        self.close()

if __name__ == '__main__':
    b = TypeTray()
    b.parseArgs()
    b.render()
