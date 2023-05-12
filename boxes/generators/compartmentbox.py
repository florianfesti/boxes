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
    Suggested to place walls close to both sides for maximum stability. 
    Margin helps to prevent the lid from getting stuck. 
    Vertical margin increases the overall height. 
    The lip holding the lid in place can be generated as two separate 
    pieces or as a single piece that continues at the back."""

    ui_group = "Tray"

    def __init__(self) -> None:
        Boxes.__init__(self) # avoid TypeTray.__init__
        self.addSettingsArgs(edges.StackableSettings)
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
        self.argparser.add_argument(
            "--margin_t", action="store", type=float, default=0.1,
            dest="margin_vertical", help="vertical margin for sliding lid (multiples of thickness)")
        self.argparser.add_argument(
            "--margin_s", action="store", type=float, default=0.05,
            dest="margin_side", help="margin to add at both sides of sliding lid (multiples of thickness)")
        self.argparser.add_argument(
            "--split_lip",  action="store", type=boolarg, default=True,
            help="create two strips to reduce waste material")

    def render(self):
        t = self.thickness
        k = self.burn
        if self.outside:
            self.sx = self.adjustSize(self.sx)
            self.sy = self.adjustSize(self.sy)
            self.hi = self.h = self.adjustSize(self.h) - 2 * t

        x = sum(self.sx) + self.thickness * (len(self.sx) - 1)
        y = sum(self.sy) + self.thickness * (len(self.sy) - 1)
        h = self.h
        b = self.bottom_edge
        split_lip = self.split_lip

        margin_vertical = self.margin_vertical * t
        margin_side = self.margin_side

        stackable = b == "s"
        tside, tback = ["Š","S"] if stackable else ["F","E"] # top edges
        if not split_lip:
            tback = tside

        if (margin_vertical < 0):
            raise ValueError("vertical margin can not be negative")
        if (margin_side < 0):
            raise ValueError("side margin can not be negative")

        # x walls
        self.ctx.save()

        # outer walls - front/back
        hb = h + t + margin_vertical
        if stackable:
            hb += -t + self.edges["S"].settings.holedistance
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
        x_compensated = x - 2*margin_side*t # margin at both sides (left, right)
        if handle == "lip":
            #compensate for the lid being a bit lower due to the margin, goal is to keep top at same height
            lip_height = (0 if stackable else t) + margin_vertical/2
            if (stackable):
                #compensate for the stackable edge extra height
                lip_height += self.edges["S"].settings.holedistance #get this value from the settings
                # correct the stackable edge for the length lost at the ends
                s = copy.deepcopy(self.edges["S"].settings)
                # get value from settings and make change
                s.setValues(self.thickness, width = self.edges["S"].settings.width/self.thickness - margin_side)
                s.edgeObjects(self, chars="aA") # this seems to be correct
            self.rectangularWall(x_compensated, y, "feee", move="up", label="lid")
            self.rectangularWall(x_compensated, lip_height, "fe" + ("A" if stackable else "e") + "e", move="up", label="lid lip")
        if handle == "hole":
            self.rectangularWall(x_compensated, y + t, move="up", label="lid", callback=[self.gripHole])
        if handle == "none":
            self.rectangularWall(x_compensated, y + t, move="up", label="lid")


        self.ctx.restore()
        self.rectangularWall(x, h, "ffff", move="right only")
        # y walls

        # outer walls - left/right
        f = edges.CompoundEdge(self, "fE", [h+self.edges[b].startwidth(), t+margin_vertical])
        self.rectangularWall(y, h+t+margin_vertical, [b, f, tside, "f"], callback=[self.yHoles, ],
                             ignore_widths=[1,5,6],
                             move="up", label="left side")
        self.rectangularWall(y, h+t+margin_vertical, [b, f, tside, "f"], callback=[self.yHoles, ],
                             ignore_widths=[1,5,6],
                             move="mirror up", label="right side")

        # inner y walls
        for i in range(len(self.sx) - 1):
            e = [edges.SlottedEdge(self, self.sy, be, slots=0.5 * h),
                 "f", "e", "f"]
            self.rectangularWall(y, h, e, move="up", label=f"inner y {i+1}")


        # lip that holds the lid in place
        lip_front_edge = "e" if self.handle == "lip" else "E"  
        if split_lip:
            self.rectangularWall(y, t, "eef" + lip_front_edge, move="up", label="Lip Left")
            self.rectangularWall(y, t, "eef" + lip_front_edge, move="mirror up", label="Lip Right")
        else:
            tx = y + self.edges.get('f').spacing() + self.edges.get(lip_front_edge).spacing()
            ty = x + 2 * self.edges.get('f').spacing()
            r=k # as sharp as possible without removing additional material from the part
            self.move(tx, ty, "up", before=True)

            self.moveTo(self.edges.get("f").margin(), self.edges.get("f").margin())
            self.edges.get("f")(y)
            self.edgeCorner("f", lip_front_edge)
            self.edges.get(lip_front_edge)(t)
            self.edgeCorner(lip_front_edge, "e")
            self.edge(y-t-r)
            self.corner(-90, radius=r)
            self.edge(x-(t+r)*2)
            self.corner(-90, radius=r)
            self.edge(y-t-r)
            self.edgeCorner("e", lip_front_edge)
            self.edges.get(lip_front_edge)(t)
            self.edgeCorner(lip_front_edge, "f")
            self.edges.get('f')(x)
            self.corner(90)
            self.edges.get('f')(y)
            self.corner(90)

            self.move(tx, ty, "up", label="Lip")

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

            slot_height = 2* radius
            slot_x = self.thickness + slot_offset

            for w in widths:
                if sum(widths) > 100:
                    slotwidth = w / sum(widths) * (x - (len(widths) + 1) * self.thickness)
                else:
                    slotwidth = w / 100 * (x - (len(widths) + 1) * self.thickness)
                slot_x += slotwidth / 2

                with self.saved_context():
                    self.rectangularHole(slot_x,radius+t,slotwidth,slot_height,radius,True,True)
                slot_x += slotwidth / 2 + slot_offset + self.thickness + slot_offset
