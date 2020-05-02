#!/usr/bin/env python3
# Copyright (C) 2013-2020 Florian Festi
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

class Console2(Boxes):
    """Console with slanted panel"""

    ui_group = "Unstable" #"Box"

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=.5)
        self.addSettingsArgs(edges.StackableSettings)

        self.buildArgParser(x=100, y=100, h=100, hi=30, bottom_edge="s")
        self.argparser.add_argument(
            "--angle",  action="store", type=float, default=50,
            help="angle of the front panel (90°=upright)")

    def borders(self):
        x, y, h, hi = self.x, self.y, self.h, self.hi
        t = self.thickness

        panel = min((h-hi)/math.cos(math.radians(90-self.angle)),
                    y/math.cos(math.radians(self.angle)))
        top = y - panel * math.cos(math.radians(self.angle))
        h = hi + panel * math.sin(math.radians(self.angle))

        if top>0.1*t:
            borders = [y, 90, hi, 90-self.angle, panel, self.angle, top,
                       90, h, 90]
        else:
            borders = [y, 90, hi, 90-self.angle, panel, self.angle+90, h, 90]
        return borders

    def latch(self, move=None):
        t = self.thickness
        s = 0.1 * t

        tw, th = 8*t, 3*t

        if self.move(tw, th, move, True):
            return
        
        self.moveTo(0, 1.2*t)
        self.polyline(t, -90, .2*t, 90, 2*t, -90, t, 90, t, 90, t, -90, 3*t,
                      90, t, -90, t, 90, t, 90, 2*t, 90, 0.5*t,
                      -94, 4.9*t, 94, .5*t, 86, 4.9*t, -176, 5*t,
                      -90, 1.0*t, 90, t, 90, 1.8*t, 90)

        self.move(tw, th, move)

    def latch_clamp(self, move=None):
        t = self.thickness
        s = 0.1 * t

        tw, th = 4*t, 4*t

        if self.move(tw, th, move, True):
            return

        self.moveTo(0.5*t)
        self.polyline(t-0.5*s, 90, 2.5*t+.5*s, -90, t+s, -90, 2.5*t+.5*s, 90, t-0.5*s, 90,
                      t, -90, 0.5*t, 90, 2*t, 45, 2**.5*t, 45, 2*t, 45, 2**.5*t, 45, 2*t, 90, 0.5*t, -90, t, 90)

        self.move(tw, th, move)

    @restore
    @holeCol
    def latch_hole(self, posx):
        t = self.thickness
        s = 0.1 * t

        self.moveTo(posx, 2*t, 180)

        path = [1.5*t, -90, t, -90, t-0.5*s, 90]
        path = path + [2*t] + list(reversed(path))
        path = path[:-1] + [3*t] + list(reversed(path[:-1]))

        self.polyline(*path)

    def panel_side(self, l, move=None):
        t = self.thickness
        s = 0.1 * t

        tw, th = l, 3*t

        if self.move(tw, th, move, True):
            return

        self.rectangularHole(3*t, 1.5*t, 3*t, 1.05*t)
        self.rectangularHole(l-3*t, 1.5*t, 3*t, 1.05*t)
        self.rectangularHole(l/2, 1.5*t, 2*t, t)
        self.polyline(*([l, 90, t, 90, t, -90, t, -90, t, 90, t, 90]*2))
    
        self.move(tw, th, move)

    def panel_lock(self, l, move=None):
        t = self.thickness

        l -= 4*t
        tw, th = l, 2.5*t

        if self.move(tw, th, move, True):
            return

        end = [l/2-3*t, -90, 1.5*t, (90, .5*t), t, (90, .5*t),
               t, 90, .5*t, -90, 0.5*t, -90, 0, (90, .5*t), 0, 90,]

        self.moveTo(l/2-t, 2*t, -90)
        self.polyline(*([t, 90, 2*t, 90, t, -90] + end + [l] +
                        list(reversed(end))))
        self.move(tw, th, move)

    def panel_cross_beam(self, l, move=None):
        t = self.thickness

        tw, th = l+2*t, 3*t

        if self.move(tw, th, move, True):
            return

        self.moveTo(t, 0)
        self.polyline(*([l, 90, t, -90, t, 90, t, 90, t, -90, t, 90]*2))

        self.move(tw, th, move)

    def side(self, borders, bottom="s", move=None):

        t = self.thickness
        bottom = self.edges.get(bottom, bottom)
        
        tw =  borders[0] + 2* self.edges["f"].spacing()
        th = borders[-2] + bottom.spacing() + self.edges["f"].spacing()
        if self.move(tw, th, move, True):
            return

        d1 = t * math.cos(math.radians(self.angle))
        d2 = t * math.sin(math.radians(self.angle))
        
        self.moveTo(t, 0)
        bottom(borders[0])
        self.corner(90)
        self.edges["f"](borders[2]+bottom.endwidth()-d1)
        self.edge(d1)
        self.corner(borders[3])
        self.rectangularHole(3*t, 1.5*t, 2.5*t, 1.05*t)
        self.edge(borders[4])
        self.rectangularHole(-3*t, 1.5*t, 2.5*t, 1.05*t)
        if len(borders) == 10:
            self.corner(borders[5])
            self.edge(d2)
            self.edges["f"](borders[6]-d2)
        self.corner(borders[-3])
        self.rectangularHole(4*t, 1.55*t, 1.1*t, 1.1*t)
        self.edge(borders[-2]-t)
        self.edges["f"](t+bottom.startwidth())
        self.corner(borders[-1])
        
        self.move(tw, th, move)
        
    def render(self):
        x, y, h, hi = self.x, self.y, self.h, self.hi
        t = self.thickness
        bottom = self.edges.get(self.bottom_edge)
        d1 = t * math.cos(math.radians(self.angle))
        d2 = t * math.sin(math.radians(self.angle))

        borders = self.borders()
        self.side(borders, bottom, move="right")
        self.side(borders, bottom, move="right")

        self.rectangularWall(borders[0], x, "ffff", move="right") # floor
        self.rectangularWall( #front
            borders[2]-d1, x, ("F", "e", "F", bottom), ignore_widths=[7, 4],
            move="right")

        self.rectangularWall(borders[4], x, "EEEE", move="right") # panel
        if len(borders) == 10: # top
            self.rectangularWall(borders[6]-d2, x, "FEFe", move="right")

        self.rectangularWall( # back wall
            borders[-2]-1.05*t, x, "EeEe",
            callback=[lambda:self.latch_hole(4*t),
                      lambda: self.fingerHolesAt(.5*t, 0, borders[-2]-8.05*t),
                      lambda:self.latch_hole(borders[-2]-1.2*t-4*t),
                      lambda: self.fingerHolesAt(.5*t, 7.05*t, borders[-2]-8.05*t)],
            move="right")
        self.rectangularWall(2*t, borders[-2]-8.05*t, "Eeef", move="right")
        self.rectangularWall(2*t, borders[-2]-8.05*t, "Eeef", move="right")
        self.rectangularWall(t, x, ("F", bottom, "F", "e"), # backwall bottom
                             ignore_widths=[0, 3], move="right")

        self.panel_cross_beam(x-2.05*t, "rotated right")
        self.panel_cross_beam(x-2.05*t, "rotated right")

        # hardware for back wall
        self.latch(move="up")
        self.latch(move="up")
        self.partsMatrix(4, 2, "up", self.latch_clamp)

        # hardware for panel
        self.panel_lock(borders[4], "up")
        self.panel_lock(borders[4], "up")
        self.panel_side(borders[4], "up")
        self.panel_side(borders[4], "up")
