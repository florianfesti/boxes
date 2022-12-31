#!/usr/bin/env python3
# Copyright (C) 2013-2018 Florian Festi
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


class Hook(Boxes):
    """A hook wit a rectangular mouth to mount at the wall"""

    ui_group = "Misc"  # see ./__init__.py for names

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=0.5)
        self.argparser.add_argument("--width", action="store",
            type=float, default=40.,
            help="width of the hook (back plate is a bit wider)")
        self.argparser.add_argument("--height", action="store",
            type=float, default=40.,
            help="inner height of the hook")
        self.argparser.add_argument("--depth",	action="store",
            type=float, default=40.,
            help="inner depth of the hook")
        self.argparser.add_argument("--strength",  action="store",
            type=float, default=20.,
            help="width of the hook from the side")
        self.argparser.add_argument("--angle",  action="store",
            type=float, default=45.,
            help="angle of the support underneeth")

    def render(self):

        self.angle = min(self.angle, 80)
        t = self.thickness
        w = self.width - 2*t # inner width
        d, h, s = self.depth, self.height, self.strength

        self.rectangularWall(w + 4*t, self.height_back, 'Eeee', callback=self.back_callback, move='right')
        self.sidewall(d, h, s, self.angle, move='right')
        self.sidewall(d, h, s, self.angle, move='right')
        self.rectangularWall(d, w, 'FFFf', move='right')
        self.rectangularWall(h - t,  w, 'FFFf', move='right', callback=[
            lambda: self.hole((h - t)/2, w/2, d=17)])
        self.rectangularWall(s-t, w, 'FeFf', move='right')



    def back_callback(self, n):
        if n != 0:
            return

        t = self.thickness
        h = self.h_a + self.strength

        self.fingerHolesAt(1.5*t, 0, h)
        self.fingerHolesAt(self.width + .5*t, 0, h)
        self.fingerHolesAt(2*t, h + t/2, self.width - 2*t, 0)

        x_h = self.width/2 + t

        y1 = h + self.height/2
        y2 = self.strength/2
        y3 = (y1 + y2) / 2

        self.hole(x_h, y1, d=3)
        self.hole(x_h, y2, d=3)
        self.hole(x_h, y3, d=3)
        

    @property
    def height_back(self):
        
        return self.strength + self.height + self.h_a

    @property
    def h_a(self):
        return self.depth * math.tan(math.radians(self.angle))

    def sidewall(self, depth, height, strength, angle=60., move=None):

        t = self.thickness

        h_a = depth * math.tan(math.radians(angle))
        l_a = depth / math.cos(math.radians(angle))

        f_edge = self.edges['f']

        x_total = depth + strength + f_edge.margin()
        y_total = strength + height + h_a

        if self.move(x_total, y_total, move, before=True):
            return


        self.moveTo(f_edge.margin())
        self.polyline(strength, angle, l_a, 90-angle, height+strength, 90)

        f_edge(strength - t)
        self.corner(90)
        f_edge(height - t)

        self.polyline(t, -90, t)

        f_edge(depth)
        self.corner(90)
        f_edge(h_a + strength)
        self.corner(90)

        self.move(x_total, y_total, move)
