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

class ShutterBox(Boxes):
    """Box with a rolling shutter made of flex"""

    ui_group = "FlexBox"

    description = """Beware of the rolling shutter effect! Use wax on sliding surfaces.

![Inside](static/samples/ShutterBox-3.jpg)

![Detail](static/samples/ShutterBox-2.jpg)
"""

    def side(self, l, h, r, style, move=None):
        t = self.thickness
        
        if self.move(l+2*t, h+2*t, move, True):
            return

        self.moveTo(t, t)

        self.ctx.save()

        n = self.n
        a = 90. / n
        ls = 2*math.sin(math.radians(a/2)) * (r-2.5*t)

        #self.hole(l-r, r, r-2.5*t)
        if style == "double":
            #self.hole(r, r, r-2.5*t)
            self.ctx.save()
            self.fingerHolesAt(r, 2*t, l-2*r, 0)
            self.moveTo(r, 2.5*t, 180 - a/2)
            for i in range(n):
                self.fingerHolesAt(0, 0.5*t, ls, 0)
                self.moveTo(ls, 0, -a)
            if h - 2*r > 2*t:
                self.moveTo(0, 0, a/2)
                self.fingerHolesAt(0, 0.5*t, h - 2*r, 0)
            self.ctx.restore()
        else:
            self.fingerHolesAt(0, 2*t, l-r, 0)
        self.moveTo(l-r, 2.5*t, a/2)
        for i in range(n):
            self.fingerHolesAt(0, -0.5*t, ls, 0)
            self.moveTo(ls, 0, a)
        if h - 2*r > 2*t:
            self.moveTo(0, 0, -a/2)
            self.fingerHolesAt(0, -0.5*t, h - 2*r, 0)
        self.ctx.restore()

        self.edges["f"](l)
        self.corner(90)
        self.edges["f"](h-r)
        self.polyline(0, -90, t, 90, 0, (90, r+t))
        if style == "single":
            self.polyline(l-r, 90, t)
            self.edges["f"](h)
        else:
            self.polyline(l-2*r, (90, r+t), 0, 90, t, -90)
            self.edges["f"](h-r)
        
        self.move(l+2*t, h+2*t, move)

    def cornerRadius(self, r, two=False, move=None):
        s = self.spacing
        if self.move(r, r+s, move, True):
            return
        for i in range(2 if two else 1):
            self.polyline(r, 90, r, 180, 0, (-90, r), 0 ,-180)
            self.moveTo(r, r+s, 180)
        self.move(r, r+s, move)

    def rails(self, l, r, move=None):
        t = self.thickness
        s = self.spacing
        tw, th = l+2.5*t+3*s, r+1.5*t+3*s

        if self.move(tw, th, move, True):
            return

        self.moveTo(2.5*t+s, 0)
        self.polyline(l-r, (90, r+t), 0, 90, t, 90, 0, (-90, r), l-r, 90, t, 90)
        self.moveTo(-t-s, t+s)
        self.polyline(l-r, (90, r+t), 0, 90, t, 90, 0, (-90, r), l-r, 90, t, 90)
        self.moveTo(0.5*t, t+s)
        self.polyline(l-r, (90, r-1.5*t), 0, 90, t, 90, 0, (-90, r-2.5*t), l-r, 90, t, 90)
        self.moveTo(-t-s, t+s)
        self.polyline(l-r, (90, r-1.5*t), 0, 90, t, 90, 0, (-90, r-2.5*t), l-r, 90, t, 90)
            
        self.move(tw, th, move)

    def rails2(self, l, r, move=None):
        t = self.thickness
        s = self.spacing
        tw, th = l+2.5*t+3*s, 2*r+t

        if self.move(tw, th, move, True):
            return

        self.moveTo(r+t, 0)
        for i in range(2):
            self.polyline(l-2*r, (90, r+t), 0, 90, t, 90, 0, (-90, r), l-2*r,
                          (-90, r), 0, 90, t, 90, 0, (90, r+t))
            self.moveTo(0, 1.5*t)
            self.polyline(l-2*r, (90, r-1.5*t), 0, 90, t, 90, 0, (-90, r-2.5*t), l-2*r,
                          (-90, r-2.5*t), 0, 90, t, 90, 0, (90, r-1.5*t))
            self.moveTo(0, r)

        self.move(tw, th, move)


    def door(self, l, h, move=None):
        t = self.thickness
        if self.move(l, h, move, True):
            return
        self.fingerHolesAt(t, t, h-2*t)
        self.edge(2*t)
        self.edges["X"](l-2*t, h)
        self.polyline(0, 90, h, 90, l, 90, h, 90)
        self.move(l, h, move)

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=0.5)
        self.addSettingsArgs(edges.FlexSettings, distance=.75, connection=2.)

        self.buildArgParser(x=150, y=100, h=100)
        self.argparser.add_argument(
            "--radius",  action="store", type=float, default=40.0,
            help="radius of the corners")
        self.argparser.add_argument(
            "--style",  action="store", type=str, default="single",
            choices=["single", "double"],
            help="Number of rounded top corners")


    def render(self):
        x, y, h, r = self.x, self.y, self.h, self.radius
        style = self.style

        self.n = n = 3
        
        if not r:
            self.radius = r = h / 2
        self.radius = r = min(r, h/2)

        t = self.thickness
        self.ctx.save()
        self.side(x, h, r, style, move="right")
        self.side(x, h, r, style, move="right")
        if style == "single":
            self.rectangularWall(y, h, "fFEF", move="right")
        else:
            self.rectangularWall(y, h-r, "fFeF", move="right")
        self.rectangularWall(y, h-r, "fFeF", move="right")

        if style == "double":
            self.cornerRadius(r, two=True, move="right")

        self.cornerRadius(r, two=True, move="right")
        if style == "single":
            self.rails(x, r, move="right")
        else:
            self.rails2(x, r, move="right")

        self.ctx.restore()
        self.side(x, h, r, style, move="up only")

        self.rectangularWall(x, y, "FFFF", move="right")
        
        if style == "single":
            self.door(x-r+0.5*math.pi*r + 3*t, y-0.2*t, move="right")
        else:
            self.door(x-2*r+math.pi*r + 3*t, y-0.2*t, move="right")

        self.rectangularWall(2*t, y-2.2*t, edges="eeef", move="right")
        

        a = 90. / n
        ls = 2*math.sin(math.radians(a/2)) * (r-2.5*t)

        edges.FingerJointSettings(t, angle=a).edgeObjects(self, chars="aA")
        edges.FingerJointSettings(t, angle=a/2).edgeObjects(self, chars="bB")


        if style == "double":
            if h - 2*r > 2*t:
                self.rectangularWall(h - 2*r, y, "fBfe", move="right")
                self.rectangularWall(ls, y, "fAfb", move="right")
            else:
                self.rectangularWall(ls, y, "fAfe", move="right")

            for i in range(n-2):
                self.rectangularWall(ls, y, "fAfa", move="right")

            self.rectangularWall(ls, y, "fBfa", move="right")

            self.rectangularWall(x-2*r, y, "fbfb", move="right")
        else:
            self.rectangularWall(x-r, y, "fbfe", move="right")
        
        self.rectangularWall(ls, y, "fafB", move="right")
        
        for i in range(n-2):
            self.rectangularWall(ls, y, "fafA", move="right")

            
        if h - 2*r > 2*t:
            self.rectangularWall(ls, y, "fbfA", move="right")
            self.rectangularWall(h - 2*r, y, "fefB", move="right")
        else:
            self.rectangularWall(ls, y, "fefA", move="right")

