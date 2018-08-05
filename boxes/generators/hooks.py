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
import math

HEIGHT = 5
GRID = 25


class Hook(Boxes):  # Change class name!
    """DESCRIPTION"""

    webinterface = False  # Change to make visible in web interface
    ui_group = "Unstable"  # see ./__init__.py for names

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=0.5)

    def render(self):
        self.open()

        self.render_back()
        self.render_sidewall(move='right')
        self.render_sidewall(move='right')
        self.render_plates()

        self.close()


    def back_callback(self, n):
        if n != 0:
            return

        t = self.t
        h = self.y_a - t

        self.fingerHolesAt(t/2, 0, h)
        self.fingerHolesAt(self.w_back - t/2, 0, h)
        self.fingerHolesAt(t, h + self.t/2, self.w_hook, 0)

        x_h = self.w_hook/2 + t

        y1 = h + self.y_o/2
        y2 = self.y_o/2
        y3 = (y1 + y2) / 2

        self.hole(x_h, y1, d=3)
        self.hole(x_h, y2, d=3)
        self.hole(x_h, y3, d=3)
        
    @property
    def t(self):
        return self.thickness

    @property
    def w_hook(self):
        return 40

    @property
    def w_back(self):
        return self.w_hook + 2*self.t

    def render_back(self):
        self.rectangularWall(self.w_back, self.y_ges, 'eEeE', callback=self.back_callback, move='right')

    @property
    def y_ges(self):
        return 100

    @property
    def y_o(self):
        return 30

    @property
    def y_a(self):
        return self.y_ges - self.y_o

    @property
    def x_o(self):
        return 40
        
    @property
    def x_plus(self):
        return 20

    def render_sidewall(self, move=None):
        
        x_ges = self.x_o + self.x_plus + self.t
        x_u = 10

        x_a = x_ges - x_u

        a = math.degrees(math.atan(self.y_a/x_a))
        l_a = math.sqrt(self.y_a**2 + x_a**2)

        if self.move(x_ges, self.y_ges, move, before=True):
            return

        f_edge = self.edges['f']
        turn = self.corner

        self.moveTo(f_edge.margin())
        self.polyline(x_u, a, l_a, 90-a, self.y_o-self.t, 90)

        f_edge(self.x_plus)
        turn(90)
        f_edge(self.y_o - self.t)

        self.polyline(self.t, -90, self.t)

        f_edge(self.x_o)
        turn(90)
        f_edge(self.y_a - self.t)
        turn(90)

        self.move(x_ges, self.y_ges, move)


    def bitholder_cb(self, n):
        if n != 0:
            return

        self.hole((self.y_o - self.t)/2, self.w_hook/2, d=17)


    def render_plates(self):
        self.rectangularWall(self.x_o, self.w_hook, 'FFFf', move='right')
        self.rectangularWall(self.y_o - self.t,  self.w_hook, 'FFFf', move='right', callback=self.bitholder_cb)
        self.rectangularWall(self.x_plus, self.w_hook, 'FeFf', move='right')




