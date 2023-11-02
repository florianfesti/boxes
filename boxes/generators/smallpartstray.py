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
from boxes import lids
from boxes.edges import CompoundEdge

class SmallPartsTray(Boxes):
    """Tray with slants to easier get out game tokens or screws"""

    ui_group = "Tray"

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)
        # self.addSettingsArgs(edges.StackableSettings)
        self.addSettingsArgs(lids.LidSettings)

        self.buildArgParser(sx="50*3", y=100, h=30, outside=True)
        self.argparser.add_argument(
            "--angle",  action="store", type=float, default=45.,
            help="angle of the ramps")
        self.argparser.add_argument(
            "--rampheight",  action="store", type=float, default=.5,
            help="height of the ramps relative to to total height")
        self.argparser.add_argument(
            "--two_sided",  action="store", type=boolarg, default=True,
            help="have ramps on both sides. Enables sliding dividers")
        self.argparser.add_argument(
            "--front_panel",  action="store", type=boolarg, default=True,
            help="have a vertical wall at the ramp")
        

    def innerWall(self, h, y, ramp_h, ramp_y, two_ramps, front=True,
                  move=None):
        a = math.degrees(math.atan(ramp_h/ramp_y))
        l = (ramp_h**2 + ramp_y**2)**.5
        if two_ramps:
            self.polygonWall(
                [y-2*ramp_y, a, l, 90-a, h-ramp_h, 90, y,
                 90, h-ramp_h, 90-a, l, a],
                "fffeff" if front else "ffeeef", move=move)
        else:
            self.polygonWall(
                [y-ramp_y, 90, h, 90, y, 90, h-ramp_h, 90-a, l, a],
                "ffeff" if front else "ffeef", move=move)

    def outerWall(self, h, y, ramp_h, ramp_y, two_ramps, front=True,
                  move=None):
        a = math.degrees(math.atan(ramp_h/ramp_y))
        l = (ramp_h**2 + ramp_y**2)**.5
        t = self.thickness

        def cb():
            with self.saved_context():
                self.moveTo(ramp_y, 0, 180-a)
                self.fingerHolesAt(0, 0.5*t, l, 0)
            if two_ramps:
                self.moveTo(y-ramp_y, 0, a)
                self.fingerHolesAt(0, -0.5*t, l, 0)
        
        if two_ramps:
            self.rectangularWall(
                y, h,
                [CompoundEdge(self, "EFE", (ramp_y, y-2*ramp_y, ramp_y)),
                 CompoundEdge(self, "EF", (ramp_h, h-ramp_h)) if front else "e",
                 "e",
                 CompoundEdge(self, "FE", (h-ramp_h, ramp_h)) if front else "e"],
                callback=[cb], move=move)
        else:
            self.rectangularWall(
                y, h, [
                    CompoundEdge(self, "EF", (ramp_y, y-ramp_y)) if front else "e",
                    "F",
                    "e",
                    CompoundEdge(self, "FE", (h-ramp_h, ramp_h))],
                    callback=[cb], move=move)
            

    def holeCB(self, sections, height):
        def CB():
            pos = -0.5 * self.thickness
            for l in sections[:-1]:
                pos += l + self.thickness
                self.fingerHolesAt(pos, 0, height)
        return CB
            
    def render_simple_tray_divider(self, width, height, move):
        """
        Simple movable divider. A wall with small feet for a little more stability.
        """

        if self.move(width, height, move, True):
            return

        t = self.thickness
        self.moveTo(t)
        self.polyline(
            width - 2 * t,
            90,
            t,
            -90,
            t,
            90,
            height - t,
            90,
            width,
            90,
            height - t,
            90,
            t,
            -90,
            t,
            90,
        )

        self.move(width, height, move)

    def render_simple_tray_divider_feet(self, move=None):
        sqr2 = math.sqrt(2)
        t = self.thickness
        divider_foot_width = 2 * t
        full_width = t + 2 * divider_foot_width
        move_length = full_width / sqr2 + 2 * self.burn
        move_width = full_width / sqr2 + 2 * self.burn

        if self.move(move_width, move_length, move, True):
            return

        self.moveTo(self.burn)
        self.ctx.save()
        self.polyline(
            sqr2 * divider_foot_width,
            135,
            t,
            -90,
            t,
            -90,
            t,
            135,
            sqr2 * divider_foot_width,
            135,
            full_width,
            135,
        )
        self.ctx.restore()

        self.moveTo(-self.burn / sqr2, self.burn * (1 + 1 / sqr2), 45)
        self.moveTo(full_width)

        self.polyline(
            0,
            135,
            sqr2 * divider_foot_width,
            135,
            t,
            -90,
            t,
            -90,
            t,
            135,
            sqr2 * divider_foot_width,
            135,
        )

        self.move(move_width, move_length, move)


    def render(self):
        # adjust to the variables you want in the local scope
        sx, y, h = self.sx, self.y, self.h
        t = self.thickness
        a = self.angle
        b = "e"

        if self.outside:
            self.sx = sx = self.adjustSize(sx)
            self.h = h = self.adjustSize(h, False)
            dy = t if self.front_panel else t / 2**0.5
            self.y = y = self.adjustSize(y, dy, dy)

        x = sum(sx) + (len(sx)-1) * t

        ramp_h = h * self.rampheight
        ramp_y = ramp_h / math.tan(math.radians(a))

        if self.two_sided and (2*ramp_y + 3*t > y):
            ramp_y = (y - 3*t) / 2
            ramp_h = ramp_y * math.tan(math.radians(a))
        elif ramp_y > y - t:
            ramp_y = y - t
            ramp_h = ramp_y * math.tan(math.radians(a))

        ramp_l = (ramp_h**2 + ramp_y**2)**.5

        with self.saved_context():
            self.outerWall(h, y, ramp_h, ramp_y,
                           self.two_sided, self.front_panel, move="up")
            self.outerWall(h, y, ramp_h, ramp_y,
                           self.two_sided, self.front_panel, move="mirror up")
            for i in range(len(sx)-1):
                self.innerWall(h, y, ramp_h, ramp_y,
                               self.two_sided, self.front_panel, move="up")
        self.innerWall(h, y, ramp_h, ramp_y,
                       self.two_sided, self.front_panel, move="right only")

        if self.front_panel:
            self.rectangularWall(
                x, h-ramp_h, "efef",
                callback=[self.holeCB(sx, h-ramp_h)], move="up")
        self.rectangularWall(x, ramp_l, "efef",
                             callback=[self.holeCB(sx, ramp_l)], move="up")
        if self.two_sided:
            self.rectangularWall(
                x, y-2*ramp_y, "efef",
                callback=[self.holeCB(sx, y-2*ramp_y)], move="up")
            self.rectangularWall(
                x, ramp_l, "efef",
                callback=[self.holeCB(sx, ramp_l)], move="up")
            if self.front_panel:
                self.rectangularWall(
                    x, h-ramp_h, "efef",
                    callback=[self.holeCB(sx, h-ramp_h)], move="up")
        else:
            self.rectangularWall(
                x, y-ramp_y, "efff",
                callback=[self.holeCB(sx, y-ramp_y)], move="up")
            self.rectangularWall(
                x, h, "Ffef",
                callback=[self.holeCB(sx, h)], move="up")
            

        if self.two_sided:
            with self.saved_context():
                for l in self.sx:
                    self.render_simple_tray_divider(l, h, move="right")

                self.partsMatrix(len(self.sx), 0, "right", self.render_simple_tray_divider_feet)
            self.render_simple_tray_divider(l, h, move="up only")

            self.lid(x, y)
