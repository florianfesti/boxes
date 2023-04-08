#!/usr/bin/env python3
# Copyright (C) 2013-2014 Florian Festi
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
from boxes.generators.typetray import TypeTray

class CompartmentBox(TypeTray):
    """Type tray variation with sliding lid"""

    description = """Sliding lid rests on inner walls, 
    so will not work if no inner walls are present. 
    Suggested to place walls close to both sides for maximum stability."""

    ui_group = "Tray"

    def __init__(self) -> None:
        Boxes.__init__(self) # avoid TypeTray.__init__
        self.buildArgParser("sx", "sy", "h", "outside", "bottom_edge")
        self.argparser.add_argument(
            "--handle", action="store", type=str, default="lip",
            choices={"none","lip","hole"},
            help="how to grab the lid to remove")
        self.argparser.add_argument(
            "--radius", action="store", type=float, default=10,
            dest="radius", help="radius of the grip hole in mm")
        self.argparser.add_argument(
            "--holes", action="store", type=str,
            default="70",
            help="width of hole(s) in percentage of maximum hole width")

    def render(self):
        t = self.thickness
        if self.outside:
            self.sx = self.adjustSize(self.sx)
            self.sy = self.adjustSize(self.sy)
            self.hi = self.h = self.adjustSize(self.h) - 2 * t

        x = sum(self.sx) + self.thickness * (len(self.sx) - 1)
        y = sum(self.sy) + self.thickness * (len(self.sy) - 1)
        h = self.h
        b = self.bottom_edge

        stackable = b == "s"

        tside, tback = ["Š","S"] if stackable else ["F","E"] # top edges

        # x walls
        self.ctx.save()

        # outer walls - front/back
        hb = h+t * (3 if stackable else 1)
        self.rectangularWall(x, hb, [b, "F", tback, "F"],
                                callback=[self.xHoles],
                                ignore_widths=[1,2,5,6],
                                move="up", label="back")

        self.rectangularWall(x, h, [b, "F", "e", "F"],
                                callback=[self.mirrorX(self.xHoles, x)],
                                ignore_widths=[1,6],
                                move="up", label="front")

        # floor
        if b != "e":
            self.rectangularWall(x, y, "ffff", callback=[self.xSlots, self.ySlots], move="up", label="bottom")

        # Inner x walls
        be = "f" if b != "e" else "e"
        for i in range(len(self.sy) - 1):
            e = [edges.SlottedEdge(self, self.sx, be), "f",
                 edges.SlottedEdge(self, self.sx[::-1], "e", slots=0.5 * h), "f"]
            self.rectangularWall(x, h, e, move="up", label=f"inner x {i+1}")

        # top / lid
        handle = self.handle
        if handle == "lip":
            self.rectangularWall(x, y, "feee", move="up", label="lid")
            self.rectangularWall(x, t * (2 if b == "s" else 1), "fe" + ("S" if b == "s" else "e") + "e", move="up", label="lid lip")
        if handle == "hole":
            self.rectangularWall(x, y + t, move="up", label="lid", callback=[self.gripHole])
        if handle == "none":
            self.rectangularWall(x, y + t, move="up", label="lid")


        self.ctx.restore()
        self.rectangularWall(x, h, "ffff", move="right only")
        # y walls

        # outer walls - left/right
        f = edges.CompoundEdge(self, "fE", [h+self.edges[b].startwidth(), t])
        self.rectangularWall(y, h+t, [b, f, tside, "f"], callback=[self.yHoles, ],
                             ignore_widths=[1,5,6],
                             move="up", label="left side")
        self.rectangularWall(y, h+t, [b, f, tside, "f"], callback=[self.yHoles, ],
                             ignore_widths=[1,5,6],
                             move="mirror up", label="right side")

        # inner y walls
        for i in range(len(self.sx) - 1):
            e = [edges.SlottedEdge(self, self.sy, be, slots=0.5 * h),
                 "f", "e", "f"]
            self.rectangularWall(y, h, e, move="up", label=f"inner y {i+1}")

        if self.handle == "lip":
            lip_edges = "eefe"
        else:
            lip_edges = "eefE"
        
        # lip that holds the lid in place
        self.rectangularWall(y, t, lip_edges, move="up", label="Lip Left")
        self.rectangularWall(y, t, lip_edges, move="mirror up", label="Lip Right")

    def gripHole(self):
        if not self.radius:
            return
        radius = self.radius
        t = self.thickness
        widths = argparseSections(self.holes)

        x = sum(self.sx) + self.thickness * (len(self.sx) - 1)

        if sum(widths) > 0:
            if sum(widths) < 100:
                slot_offset = ((1 - sum(widths) / 100) * (x - (len(widths) + 1) * self.thickness)) / (len(widths) * 2)
            else:
                slot_offset = 0

            slot_height = 2* radius # (self.settings.height - 2 * self.thickness) * self.settings.hole_height / 100
            slot_x = self.thickness + slot_offset

            for w in widths:
                if sum(widths) > 100:
                    slotwidth = w / sum(widths) * (x - (len(widths) + 1) * self.thickness)
                else:
                    slotwidth = w / 100 * (x - (len(widths) + 1) * self.thickness)
                slot_x += slotwidth / 2

                with self.saved_context():
                    #self.moveTo(20, slot_x, 0)
                    self.rectangularHole(slot_x,radius+t,slotwidth,slot_height,radius,True,True)
                slot_x += slotwidth / 2 + slot_offset + self.thickness + slot_offset
