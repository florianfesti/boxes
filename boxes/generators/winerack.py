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

    def __init__(self) -> None:
        Boxes.__init__(self)

        # Uncomment the settings for the edge types you use
        self.addSettingsArgs(edges.FingerJointSettings)

        # remove cli params you do not need
        self.buildArgParser(x=400, y=300, h=210)
        # Add non default cli params if needed (see argparse std lib)
        self.argparser.add_argument(
            "--radius",  action="store", type=float, default=46.,
            help="Radius of comb")
        self.argparser.add_argument(
            "--walls", action="store", type=str, default="all",
            choices=("minimal", "no_verticals", "all"),
            help="which of the honey comb walls to add")

    def hexFingerHoles(self, x, y, l, angle=90):
        with self.saved_context():
            self.moveTo(x, y, angle)
            self.moveTo(self.delta, 0, 0)
            self.fingerHolesAt(0, 0, l-2*self.delta, 0)

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

        wmin = self.walls == "minimal"
        
        for i in range(cy//2 + cy % 2):
            if not frontwall and self.walls == "all":
                self.hexFingerHoles(0, (2*r+2*dy)*i+dy, r, 90)
            for j in range(cx):
                if not backwall:
                    self.hole(j*2*dx+dx, (2*r+2*dy)*i + r, dx-t)
                if frontwall:
                    continue
                self.hexFingerHoles(j*2*dx+dx, (2*r+2*dy)*i, r, 150)
                self.hexFingerHoles(j*2*dx+dx, (2*r+2*dy)*i, r, 30)
                if self.walls == "all":
                    self.hexFingerHoles(j*2*dx+2*dx, (2*r+2*dy)*i+dy, r, 90)
                if wmin and i == cy//2: # top row
                    continue
                if j>0 or not wmin:
                    self.hexFingerHoles(j*2*dx+dx, (2*r+2*dy)*i+r+2*dy, r, -150)
                if j<cx-1 or not wmin:
                    self.hexFingerHoles(j*2*dx+dx, (2*r+2*dy)*i+r+2*dy, r, -30)
            if i < cy//2:
                for j in range(cx):
                    if not frontwall and self.walls == "all":
                        self.hexFingerHoles(j*2*dx+dx, (2*r+2*dy)*i+r+2*dy, r, 90)
                if not backwall:
                    for j in range(1, cx):
                        self.hole(j*2*dx, (2*r+2*dy)*i + 2*r + dy, dx-t)
        if cy % 2:
            pass
        else:
            i = cy // 2
            for j in range(cx):
                if frontwall or wmin:
                    break
                if j > 0:
                    self.hexFingerHoles(j*2*dx+dx, (2*r+2*dy)*i, r, 150)
                if j < cx -1:
                    self.hexFingerHoles(j*2*dx+dx, (2*r+2*dy)*i, r, 30)

        
    def render(self):
        x, y, h, radius = self.x, self.y, self.h, self.radius

        t = self.thickness
        r = self.r = 2 * (radius + t) * math.tan(math.pi/6)
        
        self.dx = dx = r * math.cos(math.pi/6)
        self.dy = dy = r * math.sin(math.pi/6)
        self.cx = cx = int((x-2*t) // (2*dx))
        self.cy = cy = int((y-dy-t) // (r+dy))
        self.delta = 3**0.5/6.*t

        self.rectangularWall(x, y, callback=[self.wallCB], move="up")
        self.rectangularWall(x, y, callback=[lambda:self.wallCB(backwall=True)], move="up")
        self.rectangularWall(x, y, callback=[lambda:self.wallCB(frontwall=True)], move="up")
        if self.walls == "all":
            tc = (cy//2 + cy % 2) * (6 * cx + 1)
        else:
            tc = (cy//2 + cy % 2) * (4 * cx)

        if self.walls == "minimal":
            tc -= 2 * (cy//2) # roofs of outer cells

        if cy % 2:
            if self.walls == "all":
                tc -= cx
        else:
            if self.walls != "minimal":
                tc += 2 * cx - 2 # very top row

        self.partsMatrix(tc, cx, "up", self.rectangularWall, r-2*self.delta, h, "fefe")


