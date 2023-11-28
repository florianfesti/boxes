# Copyright (C) 2013-2014 Florian Festi
# Copyright (C) 2018 jens persson <jens@persson.cx>
# Copyright (C) 2023 Manuel Lohoff
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

from boxes import edges, Boxes, BoolArg


class InsetEdgeSettings(edges.Settings):
    """Settings for InsetEdge"""
    absolute_params = {
        "thickness": 0,
    }


class InsetEdge(edges.BaseEdge):
    """An edge with space to slide in a lid"""
    def __call__(self, length, **kw):
        t = self.settings.thickness
        self.corner(90)
        self.edge(t, tabs=2)
        self.corner(-90)
        self.edge(length, tabs=2)
        self.corner(-90)
        self.edge(t, tabs=2)
        self.corner(90)


class FingerHoleEdgeSettings(edges.Settings):
    """Settings for FingerHoleEdge"""
    absolute_params = {
        "wallheight": 0,
        "fingerholedepth": 0,
    }


class FingerHoleEdge(edges.BaseEdge):
    """An edge with room to get your fingers around cards"""
    def __call__(self, length, **kw):
        depth = self.settings.fingerholedepth-10
        self.edge(length/2-10, tabs=2)
        self.corner(90)
        self.edge(depth, tabs=2)
        self.corner(-180, 10)
        self.edge(depth, tabs=2)
        self.corner(90)
        self.edge(length/2-10, tabs=2)


class CardBox(Boxes):
    """Box for storage of playing cards, with versatile options"""
    ui_group = "Box"

    description = """
### Description
Versatile Box for Storage of playing cards. Multiple different styles of storage are supported, e.g. a flat storage or a trading card deck box style storage. See images for ideas.

#### Building instructions
Place inner walls on floor first (if any). Then add the outer walls. Glue the two walls without finger joins to the inside of the side walls. Make sure there is no squeeze out on top, as this is going to form the rail for the lid.

Add the top of the rails to the sides (front open) or to the back and front (right side open) and the grip rail to the lid.
Details of the lid and rails
![Details](static/samples/CardBox-detail.jpg)
Whole box (early version still missing grip rail on the lid):
"""

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser(y=68, h=92, outside=False, sx="65*4")
        self.argparser.add_argument(
            "--openingdirection", action="store", type=str, default="front",
            choices=['front', 'right'],
            help="Direction in which the lid slides open. Lid length > Lid width recommended.")
        self.argparser.add_argument(
            "--fingerhole", action="store", type=str, default="regular",
            choices=['regular', 'deep', 'custom'],
            help="Depth of cutout to grab the cards")
        self.argparser.add_argument(
            "--fingerhole_depth", action="store", type=float, default=20,
            help="Depth of cutout if fingerhole is set to 'custom'. Disabled otherwise.")
        self.argparser.add_argument(
            "--add_lidtopper", action="store", type=BoolArg(), default=False,
            help="Add an additional lid topper for optical reasons and customisation"
        )

    @property
    def fingerholedepth(self):
        if self.fingerhole == 'custom':
            return self.fingerhole_depth
        elif self.fingerhole == 'regular':
            a = self.h/4
            if a < 35:
                return a
            else:
                return 35
        elif self.fingerhole == 'deep':
            return self.h-self.thickness-10

    #inner dimensions of surrounding box (disregarding inlays)
    @property
    def boxhight(self):
        if self.outside:
            return self.h - 3 * self.thickness
        else:
            return self.h
    @property
    def boxwidth(self):
        return (len(self.sx) + 1) * self.thickness + sum(self.sx)
    @property
    def boxdepth(self):
        if not self.outside:
            if self.openingdirection == 'right':
                return self.y + 2 * self.thickness
            else:
                return self.y
        else:
            return self.y - 2 * self.thickness

    def divider_bottom(self):
        t = self.thickness
        sx = self.sx
        y = self.boxdepth

        pos = 0.5 * t
        for i in sx[:-1]:
            pos += i + t
            self.fingerHolesAt(pos, 0, y, 90)

    def divider_back_and_front(self):
        t = self.thickness
        sx = self.sx
        y = self.boxhight

        pos = 0.5 * t
        for i in sx[:-1]:
            pos += i + t
            self.fingerHolesAt(pos, 0, y, 90)

    def render(self):
        t = self.thickness

        h = self.boxhight
        x = self.boxwidth
        y = self.boxdepth
        sx = self.sx

        s = InsetEdgeSettings(thickness=t)
        p = InsetEdge(self, s)
        p.char = "a"
        self.addPart(p)

        s = FingerHoleEdgeSettings(thickness=t, wallheight=h, fingerholedepth=self.fingerholedepth)
        p = FingerHoleEdge(self, s)
        p.char = "A"
        self.addPart(p)

        if self.openingdirection == 'right':
            with self.saved_context():
                self.rectangularWall(x, y-t*.2, "eFee", move="right", label="Lid")
                self.rectangularWall(x, y, "ffff", callback=[self.divider_bottom],
                                     move="right", label="Bottom")
            self.rectangularWall(x, y, "eEEE", move="up only")
            self.rectangularWall(x, t, "feee", move="up", label="Lip Front")
            self.rectangularWall(x, t, "eefe", move="up", label="Lip Back")

            with self.saved_context():
                self.rectangularWall(x, h+t, "FfFf",
                                 callback=[self.divider_back_and_front],
                                 move="right",
                                 label="Back")
                self.rectangularWall(x, h+t, "FfFf",
                                 callback=[self.divider_back_and_front],
                                 move="right",
                                 label="Front")
            self.rectangularWall(x, h+t, "EEEE", move="up only")

            with self.saved_context():
                self.rectangularWall(y, h+t, "FFEF", move="right", label="Outer Side Left")
                self.rectangularWall(y, h+t, "FFaF", move="right", label="Outer Side Right")
            self.rectangularWall(y, h+t, "fFfF", move="up only")

            with self.saved_context():
                self.rectangularWall(y, h, "Aeee", move="right", label="Inner Side Left")
                self.rectangularWall(y, h, "Aeee", move="right", label="Inner Side Right")
            self.rectangularWall(y, h, "eAee", move="up only")

            with self.saved_context():
                self.rectangularWall(y-t*.2, t, "fEeE", move="right", label="Lid Lip")
            self.rectangularWall(y, t*2, "efee", move="up only")

            for i in range(len(sx) - 1):
                self.rectangularWall(h, y, "fAff", move="right", label="Divider")

            for c in sx:
                self.rectangularWall(c, h, "eeee", move="right", label="Front inlay")
                self.rectangularWall(c, h, "eeee", move="right", label="Back inlay")

            if self.add_lidtopper:
                self.rectangularWall(x, y - 2*t, "eeee", move="right", label="Lid topper")

        elif self.openingdirection == 'front':
            with self.saved_context():
                self.rectangularWall(x - t * .2, y, "eeFe", move="right", label="Lid")
                self.rectangularWall(x, y, "ffff", callback=[self.divider_bottom],
                                     move="right", label="Bottom")
            self.rectangularWall(x, y, "eEEE", move="up only")
            self.rectangularWall(x - t * .2, t, "fEeE", move="up", label="Lid Lip")

            with self.saved_context():
                self.rectangularWall(x, h + t, "FFEF",
                                     callback=[self.divider_back_and_front],
                                     move="right",
                                     label="Back")
                self.rectangularWall(x, h + t, "FFaF",
                                     callback=[self.divider_back_and_front],
                                     move="right",
                                     label="Front")
            self.rectangularWall(x, h + t, "EEEE", move="up only")

            with self.saved_context():
                self.rectangularWall(y, h + t, "FfFf", move="right", label="Outer Side Left")
                self.rectangularWall(y, h + t, "FfFf", move="right", label="Outer Side Right")
            self.rectangularWall(y, h + t, "fFfF", move="up only")

            with self.saved_context():
                self.rectangularWall(y, h, "Aeee", move="right", label="Inner Side Left")
                self.rectangularWall(y, h, "Aeee", move="right", label="Inner Side Right")
            self.rectangularWall(y, h, "eAee", move="up only")

            with self.saved_context():
                self.rectangularWall(y, t, "eefe", move="right", label="Lip Left")
                self.rectangularWall(y, t, "feee", move="right", label="Lip Right")
            self.rectangularWall(y, t * 2, "efee", move="up only")

            for i in range(len(sx) - 1):
                self.rectangularWall(h, y, "fAff", move="right", label="Divider")

            if self.add_lidtopper:
                self.rectangularWall(x, y - 2 * t, "eeee", move="right", label="Lid topper (optional)")
