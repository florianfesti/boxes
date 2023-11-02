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


class DinRailEdge(edges.FingerHoleEdge):

    def __init__(self, boxes, settings, width=35.0, offset=0.0) -> None:
        super().__init__(boxes, settings)
        self.width = width
        self.offset = offset

    def startwidth(self) -> float:
        return 8 + self.settings.thickness

    def __call__(self, length, bedBolts=None, bedBoltSettings=None, **kw):
        with self.saved_context():
            self.fingerHoles(
                0, self.burn + 8 + self.settings.thickness / 2, length, 0,
                bedBolts=bedBolts, bedBoltSettings=bedBoltSettings)

        w = self.width
        o = self.offset
        l = length
        self.polyline((l-w)/2-o, 45, 2.75*2**.5, 90, 2.75*2**.5, -45, .5, -90,
                      w+0.25,
                      -90, 1, 30, 5*2*3**-.5, 60, (l-w)/2+o-3.25)

        
class DinRailBox(Boxes):
    """Box for DIN rail used in electrical junction boxes"""

    ui_group = "WallMounted"

    def latch(self, l, move=None):

        t = self.thickness
        tw = l+3+6+t
        th = 8

        if self.move(tw, th, move, True):
            return

        self.moveTo(tw, th, 180)
        self.polyline(2, 90, 0, (-180, 1.5), 0, 90, l+1.2*t, 90,
                      3, -90, 1, 30, 2*2*3**-.5, 90, 4.5*2*3**-.5, 60,
                      4+1.25, 90, 4.5, -90, t+4, -90, 2, 90, l-.8*t-9, 90, 2, -90, 5+t, 90, 4, 90)

        self.move(tw, th, move)
        
    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=.8)

        self.buildArgParser(x=70, y=90, h=60)
        # Add non default cli params if needed (see argparse std lib)
        self.argparser.add_argument(
            "--rail_width",  action="store", type=float, default=35.,
            help="width of the rail (typically 35 or 15mm)")
        self.argparser.add_argument(
            "--rail_offset",  action="store", type=float, default=0.,
            help="offset of the rail from the middle of the box (in mm)")

    def spring(self):
        t = self.thickness
        l = min(self.x/2-1.5*t, 50)
        self.moveTo(self.x/2-l, -6-t, 0)
        self.polyline(l+0.525*t, 90 , 6, 90 , 1.1*t, 90, 3, -90, l-0.525*t,
                      180, l-0.525*t, -90, 1+0.1*t, 90, t-0.5, -90, 2)

    def lid_lip(self, l, move=None):
        t = self.thickness
        tw, th = l+2, t+8

        if self.move(tw, th, move, True):
            return
        self.moveTo(1, t)
        self.edges["f"](l)

        poly = [0, 90, 6, -60, 0, (120, 2*3**-.5), 0, 30, 2, 90, 5,
                      (-180, .5), 5, 90]
        self.polyline(*(poly+[l-2*3]+list(reversed(poly))))

        self.move(tw, th, move)

    def lid_holes(self):
        t = self.thickness
        self.rectangularHole(0.55*t, 7, 1.1*t, 1.6)
        self.rectangularHole(self.x-0.55*t, 7, 1.1*t, 1.6)

    def render(self):
        # adjust to the variables you want in the local scope
        x, y, h = self.x, self.y, self.h
        w = self.rail_width
        o = self.rail_offset
        t = self.thickness

        self.rectangularWall(x, y, "EEEE", callback=[
            lambda:self.fingerHolesAt(.55*t, .05*t, y-.1*t, 90), None,
            lambda:self.fingerHolesAt(.55*t, .05*t, y-.1*t, 90), None],
            move="right", label="Lid")
        
        self.lid_lip(y-.1*t, move="rotated right")
        self.lid_lip(y-.1*t, move="rotated right")

        self.rectangularWall(x, y, "ffff",
                             callback=[
                                 lambda:self.fingerHolesAt(0, (y-w)/2-0.5*t+o-9, x, 0)],
                             move="right", label="Back")

        # Change h edge to 8mm!
        self.edges["f"].settings.setValues(t, False, edge_width=8)
        dr = DinRailEdge(self, self.edges["f"].settings, w, o)

        self.rectangularWall(y, h, [dr, "F", "e", "F"],
                             ignore_widths=[1, 6], move="rotated right",
                             label="Left Side upsidedown")
        self.rectangularWall(y, h, [dr, "F", "e", "F"],
                             ignore_widths=[1, 6], move="rotated mirror right",
                             label="Right Side")
        self.rectangularWall(x, h, ["h", "f", "e", "f"],
                             ignore_widths=[1, 6], callback=[
                                 self.spring, None, self.lid_holes],
                             move="up",
                             label="Bottom")
        self.rectangularWall(x, h, ["h", "f", "e", "f"],
                             callback=[None, None, self.lid_holes],
                             ignore_widths=[1, 6], move="up",
                             label="Top")


        self.rectangularWall(x, 8, "feee", callback=[
            lambda:self.rectangularHole(x/2, 2.05-0.5*t, t, t+4.1)], move="up")
        self.latch((y-w)/2+o, move="up")
