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

class WineRack(Boxes):
    """Honey Comb Style Wine Rack"""
    
    ui_group = "Shelf"

    def __init__(self):
        Boxes.__init__(self)

        # Uncomment the settings for the edge types you use
        self.addSettingsArgs(edges.FingerJointSettings)

        # remove cli params you do not need
        self.buildArgParser(x=400, y=300, h=210)
        # Add non default cli params if needed (see argparse std lib)
        self.argparser.add_argument(
            "--radius",  action="store", type=float, default=46.,
            help="Radius of comb")

    def hexFingerHoles(self, x, y, l, angle=90):
        self.ctx.save()
        self.moveTo(x, y, angle)
        self.moveTo(self.delta, 0, 0)
        self.fingerHolesAt(0, 0, l-2*self.delta, 0)
        self.ctx.restore()

    def wallCB(self, frontwall=False, backwall=False):
        r = self.r
        x, y, h = self.x, self.y, self.h
        dx, dy = self.dx, self.dy
        cx, cy = self.cx, self.cy
        t = self.thickness

        if cy % 2:
            ty = cy // 2 * (2*dy + 2*r) + 2*dy + r
        else:
            ty = cy // 2 * (2*dy + 2*r) + dy

        self.moveTo((x-dx*2*cx)/2, (y-ty) / 2)
        
        for i in range(cy//2 + cy % 2):
            if not frontwall:
                self.hexFingerHoles(0, (2*r+2*dy)*i+dy, r, 90)
            for j in range(cx):
                if not backwall:
                    self.hole(j*2*dx+dx, (2*r+2*dy)*i + r, dx-t)
                if frontwall:
                    continue
                self.hexFingerHoles(j*2*dx+dx, (2*r+2*dy)*i, r, 150)
                self.hexFingerHoles(j*2*dx+dx, (2*r+2*dy)*i, r, 30)
                self.hexFingerHoles(j*2*dx+2*dx, (2*r+2*dy)*i+dy, r, 90)
                self.hexFingerHoles(j*2*dx+dx, (2*r+2*dy)*i+r+2*dy, r, -150)
                self.hexFingerHoles(j*2*dx+dx, (2*r+2*dy)*i+r+2*dy, r, -30)
            if i < cy//2:
                for j in range(cx):
                    if not frontwall:
                        self.hexFingerHoles(j*2*dx+dx, (2*r+2*dy)*i+r+2*dy, r, 90)
                if not backwall:
                    for j in range(1, cx):
                        self.hole(j*2*dx, (2*r+2*dy)*i + 2*r + dy, dx-t)
        if cy % 2:
            pass
        else:
            i = cy // 2
            for j in range(cx):
                if frontwall:
                    break
                if j > 0:
                    self.hexFingerHoles(j*2*dx+dx, (2*r+2*dy)*i, r, 150)
                if j < cx -1:
                    self.hexFingerHoles(j*2*dx+dx, (2*r+2*dy)*i, r, 30)

        
    def render(self):
        x, y, h, radius = self.x, self.y, self.h, self.radius

        t = self.thickness
        r = self.r = 2 * (radius + t) * math.tan(math.pi/6)
        
        self.dx = dx = r * math.cos(math.pi/6) # XXX thickness
        self.dy = dy = r * math.sin(math.pi/6)
        self.cx = cx = int(x // (2*dx))
        self.cy = cy = int((y-dy) // (r+dy))
        self.delta = 3**0.5/6.*t

        self.open()
        self.rectangularWall(x, y, callback=[self.wallCB], move="up")
        self.rectangularWall(x, y, callback=[lambda:self.wallCB(backwall=True)], move="up")
        self.rectangularWall(x, y, callback=[lambda:self.wallCB(frontwall=True)], move="up")
        tc = (cy//2 + cy % 2) * (6 * cx + 1)
        if cy % 2:
            tc -= cx
        else:
            tc += 2 * cx - 2

        self.partsMatrix(tc, cx, "up", self.rectangularWall, r-2*self.delta, h, "fefe")

        self.close()

