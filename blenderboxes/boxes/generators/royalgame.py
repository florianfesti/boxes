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

class RoyalGame(Boxes):
    """The Royal Game of Ur"""

    ui_group = "Misc"

    description = """Most of the blue lines need to be engraved by cutting with high speed and low power. But there are three blue holes that actually need to be cut: The grip hole in the lid and two tiny rectangles on the top and bottom for the lid to grip into.

![Lid Details](static/samples/RoyalGame-2.jpg)

![All pieces](static/samples/RoyalGame-3.jpg)

"""

    def __init__(self) -> None:
        Boxes.__init__(self)


        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser(x=200)

    def dice(self, size, num=1, move=None):

        s = size
        r = s / 20.0
        dr = r * 2
        h = s/2*3**0.5
        t = self.thickness
        tw, th = (num + 0.5) * size, size

        if self.move(tw, th, move, True):
            return

        self.moveTo(r, 0)
        for i in range(2*num):
            self.polyline((s-t)/2-dr, 90, h/2-r, -90, t, -90, h/2-r, 90, (s-t)/2-dr, (120, r), s-2*dr, (120, r), s-2*dr, (120, r))
            self.ctx.stroke()
            if i % 2:
                self.moveTo(.5*s - 2*dr, s, 180)
            else:
                self.moveTo(1.5*s -2*dr, s, 180)

        self.move(tw, th, move)

    def five(self, x, y, s):
        self.hole(x, y, 0.05*s)
        self.hole(x, y, 0.12*s)
        for dx in (-1, 1):
            for dy in (-1, 1):
                self.hole(x+dx*.25*s, y+dy*.25*s, 0.05*s)
                self.hole(x+dx*.25*s, y+dy*.25*s, 0.12*s)

    @restore
    @holeCol
    def _castle(self, x, y, s):
        l = s/7*2**0.5
        self.moveTo(x-s/2 + s/14, y-s/2, 45)
        self.polyline(*([l, -90, l, 90]*3 + [l/2, 90])*4)
        
    def castle(self, x, y, s):
        self._castle(x, y, 0.9*s)
        self._castle(x, y, 0.5*s)
        self.five(x, y, 0.4*s)

    def castles(self, x, y, s):
        for dx in (-1, 1):
            for dy in (-1, 1):
                self._castle(x+dx*0.25*s, y+dy*0.25*s, 0.4*s)
                self.five(x+dx*0.25*s, y+dy*0.25*s, 0.3*s)

    @restore
    @holeCol
    def rosette(self, x, y, s):
        self.moveTo(x, y, 22.5)
        with self.saved_context():
            self.moveTo(0.1*s, 0, -30)
            for i in range(8):
                self.polyline(0, (60, 0.35*s), 0, 120, 0, (60, 0.35*s), 0,
                              -120, 0, (45, 0.1*s), 0, -120)
        self.moveTo(0, 0, -22.5)
        self.moveTo(0.175*s, 0)
        for i in range(8):
            self.polyline(0, (67.5, 0.32*s), 0, 90, 0, (67.5, 0.32*s), 0, -180)

    @holeCol
    def eyes(self, x, y, s):
        for dx in (-1, 1):
            for dy in (-1, 1):
                posx = x+dx*0.3*s
                posy = y+dy*0.25*s
                self.rectangularHole(posx, posy, 0.4*s, 0.5*s)
                self.hole(posx, posy, 0.05*s)
                with self.saved_context():
                    self.moveTo(posx, posy-0.2*s, 60)
                    self.corner(60, 0.4*s)
                    self.corner(120)
                    self.corner(60, 0.4*s)
                    self.corner(120)
                    self.moveTo(0, 0, -60)
                    self.moveTo(0, -0.05*s, 60)
                    self.corner(60, 0.5*s)
                    self.corner(120)
                    self.corner(60, 0.5*s)

        for i in range(4):
            self.rectangularHole(x, y + (i-1.5)*s*0.25, 0.12*s, 0.12*s)

    def race(self, x, y, s):
        for dx in range(4):
            for dy in range(4):
                posx = (dx-1.5) * s / 4.5 + x
                posy = (dy-1.5) * s / 4.5 + y
                self.rectangularHole(posx, posy, s/5, s/5)
                if dx in (1, 2) and dy in (0,3):
                    continue
                self.hole(posx, posy, s/20)

    def top(self):

        patterns = [
            [self.castle, self.rosette, None, None, self.eyes, self.five, self.eyes, self.rosette],
            [self.five, self.eyes, self.castles, self.five, self.rosette, self.castles, self.five, self.race]]

        s = self.size
        for x in range(8):
            for y in range(3):
                if x in [2, 3] and y != 1:
                    continue
                posx = (0.5+x) * s
                posy = (0.5+y) * s
                self.rectangularHole(posx, posy, 0.9*s, 0.9*s)
                pattern = patterns[y % 2][x]
                if pattern:
                    pattern(posx, posy, 0.9*s)

    def player1(self):
        for i in range(3):
            self.hole(0, 0, r=self.size * (i+2) / 12)

    def player2(self, x=0, y=0):
        s = self.size
        self.hole(x, y, 0.07*s)
        for dx in (-1, 1):
            for dy in (-1, 1):
                self.hole(x+dx*.2*s, y+dy*.2*s, 0.07*s)
                      
    def render(self):

        x = self.x
        t = self.thickness
        self.size = size = x / 8.0
        h = size/2 * 3**0.5
        y = 3 * size

        self.rectangularWall(x, h, "FLFF", move="right")
        self.rectangularWall(y, h, "nlmE", callback=[
            lambda:self.hole(y/2, h/2, d=0.6*h)], move="up")
        self.rectangularWall(y, h, "FfFf")
        self.rectangularWall(x, h, "FeFF", move="left up")

        self.rectangularWall(x, y, "fMff", move="up")
        self.rectangularWall(x, y, "fNff", callback=[self.top,], move="up")

        
        self.partsMatrix(7, 7, "up", self.parts.disc, 0.8*size, callback=self.player1)
        self.partsMatrix(7, 7, "up", self.parts.disc, 0.8*size, callback=self.player2)

        self.dice(size, 4, move="up")
        self.dice(size, 4, move="up")
        
