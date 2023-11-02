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
from boxes import edges

class LegEdge(edges.BaseEdge):

    def __call__(self, l, **kw):
        d0 = (l - 12.0) /2
        self.hole(l/2, 6, 3.0)
        self.polyline(d0, 90, 0, (-180, 6), 0, 90, d0)

class OttoLegs(Boxes):
    """Otto LC - a laser cut chassis for Otto DIY - legs"""

    ui_group = "Misc"

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, finger=1.0, space=1.0,
                             surroundingspaces=1.0)
        self.argparser.add_argument(
            "--anklebolt1",  action="store", type=float, default=3.0,
            help="diameter for hole for ankle bolts - foot side")
        self.argparser.add_argument(
            "--anklebolt2",  action="store", type=float, default=2.6,
            help="diameter for hole for ankle bolts - leg side")
        self.argparser.add_argument(
            "--length",  action="store", type=float, default=34.0,
	    help="length of legs (34mm min)")

    def foot(self, x, y, ly, l, r=5., move=None):
        if self.move(x, y, move, True):
            return

        t = self.thickness
        w = ly + 5.5 + 2 * t
        self.fingerHolesAt(x/2 - w/2, 0, l, 90)
        self.fingerHolesAt(x/2 + w/2, 0, l, 90)
        self.moveTo(r, 0)

        for l in (x, y, x, y):
            self.polyline((l - 2*r, 2), 45, r*2**0.5, 45)
        
        self.move(x, y, move)

    def ankles(self, x, h, edge="f", callback=None, move=None):

        f = 0.5
        tw = x
        th = 2 * h + self.thickness

        if self.move(tw, th, move, True):
            return

        self.moveTo(0, self.thickness)
        for i in range(2):
            self.cc(callback, 0)
            self.edges[edge](x)
            self.polyline(0, 90)
            self.cc(callback, 1)
            self.polyline((h, 2), 90, (f*x, 1), 45, ((2**0.5)*(1-f)*x, 1), 45,
                          (h-(1-f)*x, 1), 90)
            self.moveTo(tw, th, 180)
            self.ctx.stroke()
        self.move(tw, th, move)

    def ankle1(self):
        # from vertical edge
        self.hole(15, 10, 3.45) # 3.45 for servo arm, 2.3 for knob

    def servoring(self, move=""):
        if self.move(20, 20, move, True):
            return
        self.moveTo(10, 10, 90)
        self.moveTo(3.45, 0, -90)
        self.polyline(0, (-264, 3.45), 0, 36, 6.55, 108, 0, (330, 9.0, 4), 0, 108, 6.55)
        self.move(20, 20, move)
        

    def ankle2(self):
        # from vertical edge
        self.hole(15, 10, self.anklebolt1/2)

    def servoHole(self):
        self.hole(6, 6, 11.6/2)
        self.hole(6, 12, 5.5/2)

    def render(self):
        # adjust to the variables you want in the local scope
        t = self.thickness

        ws = 25
        lx, ly, lh = 12.4, 23.5, max(self.length, ws+6+t)

        self.ctx.save()
        # Legs

        c1 = edges.CompoundEdge(self, "FE", (ly-7.0, 7.0))
        c2 = edges.CompoundEdge(self, "EF", (7.0, lh-7.0))
        e = [c1, c2, "F", "F"]

        for i in range(2):
            # front
            self.rectangularWall(lx, lh-7., [LegEdge(self, None), "f", "F", "f"], callback=[None, lambda:self.fingerHolesAt(ws-7., 0, lx)], move="right")
            # back
            self.rectangularWall(lx, lh, "FfFf", callback=[
                lambda:self.hole(lx/2, 7, self.anklebolt2/2)], move="right")
            # sides
            self.rectangularWall(ly, lh, e, callback=[None,
                lambda:self.fingerHolesAt(ws, 7.0, ly-7.0-3.0)], move="right")
            self.rectangularWall(ly, lh, e, callback=[
                lambda:self.rectangularHole(ly/2, ws+3+0.5*t, 12, 6, 3),
                lambda:self.fingerHolesAt(ws, 7.0, ly-7.0-3.0)], move="right")

        # top
        self.partsMatrix(2, 1, "right", self.rectangularWall, ly, lx, "ffff",
                         callback=[None, lambda: self.hole(lx/2, ly/2, 2.3)])
        self.partsMatrix(2, 1, "right", self.rectangularWall, lx, ly, "eeee", callback=[lambda: self.hole(lx/2, ly/2, 1.5)])
        # hold servo at the front
        self.partsMatrix(2, 1, "right", self.rectangularWall, 4.6, lx, "efee")
        # bottom
        self.partsMatrix(2, 1, "right", self.rectangularWall, lx, ly-7.0, "efff")
        # hold servo inside
        self.partsMatrix(2, 1, "right", self.rectangularWall, lx, ly-7.0-3.0, "efef")

        self.ctx.restore()
        self.rectangularWall(lx, lh, "ffff", move="up only")

        # feet
        self.foot(60, 40, ly, 30, move="right")
        self.foot(60, 40, ly, 30, move="right")
        self.ankles(30, 25, callback=[None, self.ankle1], move="right")
        self.ankles(30, 25, callback=[None, self.ankle2], move="right")
        self.partsMatrix(2, 2, "right", self.servoring)

