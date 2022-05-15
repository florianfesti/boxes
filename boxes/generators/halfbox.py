#!/usr/bin/env python3
# Copyright (C) 2013-2016 Florian Festi
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

class HalfBox(Boxes):
    """Configurable half of a box which can be: a bookend, a hanging shelf, an angle clamping jig, ..."""

    description = """This can be used to create:

* a hanging shelf:
![HalfBox as hanging shelf](static/samples/HalfBox_Shelf_usage.jpg)

* an angle clamping jig:
![HalfBox as an angle clamping jig](static/samples/HalfBox_AngleJig_usage.jpg)

* a bookend:
![HalfBox as a bookend](static/samples/HalfBox_Bookend_usage.jpg)

and many more...

"""
    ui_group = "Box"

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, finger=2.0,space=2.0)
        self.addSettingsArgs(edges.MountingSettings)
        self.buildArgParser(x=100, sy="50:50", h=100)

        self.argparser.add_argument("--Clamping",  action="store", type=boolarg, default=False, help="add clamping holes")
        self.argparser.add_argument("--ClampingSize",   action="store", type=float, default=25.0, help="diameter of clamping holes")
        self.argparser.add_argument("--Mounting",  action="store", type=boolarg, default=False, help="add mounting holes")
        self.argparser.add_argument("--Sturdy",  action="store", type=boolarg, default=False, help="create sturdy construction (e.g. shelf, clamping jig, ...)")
            
    def polygonWallExt(self, borders, edge="f", turtle=False, callback=None, move=None):
        # extended polygon wall. 
        # same as polygonWall, but with extended border parameters
        # each border dataset consists of
        #   length
        #   turn angle
        #   radius of turn (without radius correction)
        #   edge type
        
        for i in range(0, len(borders), 4):
            self.cc(callback, i)
            length = borders[i]
            next_angle = borders[i+1]
            next_radius = borders[i+2]
            next_edge = borders[i+3]

            e = self.edges.get(next_edge, next_edge)
            if i == 0:
                self.moveTo(0,e.margin(),0)
            e(length)
            if self.debug:
                self.hole(0, 0, 1, color=Color.ANNOTATIONS)
            self.corner(next_angle, tabs=0, radius=next_radius)

    def xHoles(self):
        posy = -0.5 * self.thickness
        for y in self.sy[:-1]:
            posy += y + self.thickness
            self.fingerHolesAt(posy, 0, self.x)

    def hHoles(self):
        posy = -0.5 * self.thickness
        for y in reversed(self.sy[1:]):
            posy += y + self.thickness
            self.fingerHolesAt(posy, 0, self.h)
        
    def render(self):
        # adjust to the variables you want in the local scope
            
        x, h = self.x, self.h
        d = self.ClampingSize
        t = self.thickness
        
        # triangle with sides: x (horizontal), h (upwards) and l
        # angles: 90° between x & h
        #           b between h & l
        #           c between l & x
                
        l = math.sqrt(x * x + h * h)
        b = math.degrees(math.asin(x / l))
        c = math.degrees(math.asin(h / l))
        if x > h:
            if 90 + b + c < 179:
                b = 180 - b
        else:
            if 90 + b + c < 179:
                c = 180 - c

        # small triangle top: 2*t, h1, l1        
        h1 = (2*t)/x*h
        l1 = (2*t)/x*l

        # small triangle left: x2, 2*t, l2        
        x2 = (2*t)/h*x
        l2 = (2*t)/h*l
        
        # render your parts here
    
        if self.Sturdy:
            width = sum(self.sy) + (len(self.sy) - 1) * t
            self.rectangularWall(x, width, "fffe", callback=[None, self.xHoles, None, None], move="right", label="bottom")
            self.rectangularWall(h, width, "fGfF" if self.Mounting else "fefF", callback=[None, None, None, self.hHoles], move="up", label="back")
            self.rectangularWall(x, width, "fffe", callback=[None, self.xHoles, None, None], move="left only", label="invisible")
            
            for i in range(2):
                self.move(x+x2+2*t + self.edges["f"].margin(), h+h1+2*t + self.edges["f"].margin(), "right", True, label="side " + str(i))
                self.polygonWallExt(borders=[x2, 0, 0, "e", x, 0, 0, "h",2*t, 90, 0, "e", 2*t, 0, 0, "e", h, 0, 0, "h",h1, 180-b, 0, "e", l+l1+l2, 180-c, 0, "e"])
                if self.Clamping:
                    self.hole(0, 0, 1, color=Color.ANNOTATIONS)
                    self.rectangularHole(x/2+x2,2*t+d/2,dx=d,dy=d,r=d/8)
                    self.rectangularHole((x+x2+2*t)-2*t-d/2,h/2+2*t,dx=d,dy=d,r=d/8)
                self.move(x+x2+2*t + self.edges["f"].margin(), h+h1+2*t + self.edges["f"].margin(), "right", False, label="side " + str(i))

            if len(self.sy) > 1:
                for i in range((len(self.sy) - 1)):
                    self.move(x + self.edges["f"].margin(), h + self.edges["f"].margin(), "right", True, label="support " + str(i))
                    self.polygonWallExt(borders=[x, 90, 0, "f", h, 180-b, 0, "f", l, 180-c, 0, "e"])
                    if self.Clamping:
                        self.rectangularHole(x/2,d/2-t/2,dx=d,dy=d+t,r=d/8)
                        self.rectangularHole(x-d/2+t/2,h/2,dx=d+t,dy=d,r=d/8)
                    self.move(x + self.edges["f"].margin(), h + self.edges["f"].margin(), "right", False, label="support " + str(i))
        else:
            self.sy.insert(0,0)
            self.sy.append(0)
            width = sum(self.sy) + (len(self.sy) - 1) * t
            self.rectangularWall(x, width, "efee", callback=[None, self.xHoles, None, None], move="right", label="bottom")
            self.rectangularWall(h, width, "eGeF" if self.Mounting else "eeeF", callback=[None, None, None, self.hHoles], move="up", label="side")
            self.rectangularWall(x, width, "efee", callback=[None, self.xHoles, None, None], move="left only", label="invisible")

            for i in range((len(self.sy) - 1)):
                self.move(x + self.edges["f"].margin(), h + self.edges["f"].margin(), "right", True, label="support " + str(i))
                self.polygonWallExt(borders=[x, 90, 0, "f", h, 180-b, 0, "f", l, 180-c, 0, "e"])
                if self.Clamping:
                    self.rectangularHole(x/2,d/2,dx=d,dy=d,r=d/8)
                    self.rectangularHole(x-d/2,h/2,dx=d,dy=d,r=d/8)
                self.move(x + self.edges["f"].margin(), h + self.edges["f"].margin(), "right", False, label="support " + str(i))
