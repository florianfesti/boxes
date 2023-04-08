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

class CompartmentBox(Boxes):
    """Type tray variation with sliding lid"""

    description = """Sliding lid rests on inner walls, 
    so will not work if no inner walls are present. 
    Suggested to place walls close to both sides for maximum stability."""

    ui_group = "Unstable"

    def __init__(self) -> None:
        Boxes.__init__(self)
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

        
        

    def xSlots(self):
        posx = -0.5 * self.thickness
        for x in self.sx[:-1]:
            posx += x + self.thickness
            posy = 0
            for y in self.sy:
                self.fingerHolesAt(posx, posy, y)
                posy += y + self.thickness

    def ySlots(self):
        posy = -0.5 * self.thickness
        for y in self.sy[:-1]:
            posy += y + self.thickness
            posx = 0
            for x in reversed(self.sx):
                self.fingerHolesAt(posy, posx, x)
                posx += x + self.thickness

    def xHoles(self):
        posx = -0.5 * self.thickness
        for x in self.sx[:-1]:
            posx += x + self.thickness
            self.fingerHolesAt(posx, 0, self.h)

    def yHoles(self):
        posy = -0.5 * self.thickness
        for y in self.sy[:-1]:
            posy += y + self.thickness
            self.fingerHolesAt(posy, 0, self.h)

    def render(self):
        t = self.thickness
        if self.outside:
            self.sx = self.adjustSize(self.sx)
            self.sy = self.adjustSize(self.sy)
            self.h = self.adjustSize(self.h) - 2 * t


        x = sum(self.sx) + self.thickness * (len(self.sx) - 1)
        y = sum(self.sy) + self.thickness * (len(self.sy) - 1)
        h = self.h


        # Create new Edges here if needed E.g.:
        s = edges.FingerJointSettings(self.thickness, relative=False,
                                      style = "rectangular")
        p = edges.FingerJointEdge(self, s)
        p.char = "a" # 'a', 'A', 'b' and 'B' is reserved for beeing used within generators
        self.addPart(p)

        # outer walls
        b = self.bottom_edge
        tl, tb, tr, tf = "FEFe"
        tl, tb, tr, tf = "ŠSŠe" if b == "s" else "FEFe"


        # x sides

        self.ctx.save()

        # outer walls - front/back
        hb = h+t * (3 if tb == "S" else 1)
        self.rectangularWall(x, hb, [b, "F", tb, "F"],
                                callback=[self.xHoles],
                                ignore_widths=[1,2,5,6],
                                move="up", label="back")

        self.rectangularWall(x, h, [b, "F", tf, "F"],
                                callback=[self.mirrorX(self.xHoles, x)],
                                ignore_widths=[1,6],
                                move="up", label="front")

        # floor
        if b != "e":
            self.rectangularWall(x, y, "ffff", callback=[self.xSlots, self.ySlots], move="up", label="bottom")

        # Inner walls

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
        self.sideWall(
            y, h+t, "left", [b, "f", tl, "f"], callback=[self.yHoles, ],
            move="up", label="left side")
            
        self.sideWall(
            y, h+t, "right", [b, "f", tr, "f"],
            callback=[self.mirrorX(self.yHoles, y), ],
            move="up", label="right side")

        # inner walls
        for i in range(len(self.sx) - 1):
            e = [edges.SlottedEdge(self, self.sy, be, slots=0.5 * h),
                 "f", "e", "f"]
            self.rectangularWall(y, h, e, move="up", label=f"inner y {i+1}")

        lipy = y-t if self.handle == "lip" else y
        self.rectangularWall(lipy, t, "eefe", move="up", label="Lip Left")
        self.rectangularWall(lipy, t, "feee", move="up", label="Lip Right")

    def sideWall(self, x, y, side, edges="eeee",
                        holesMargin=None, holesSettings=None,
                        bedBolts=None, bedBoltSettings=None,
                        callback=None,
                        move=None,
                        label=""):

        if len(edges) != 4:
            raise ValueError("four edges required")
        if side not in {"left", "right"}:
            raise ValueError("side must be left or right")
        b = edges[0]
        edges = [self.edges.get(e, e) for e in edges]
        edges += edges  # append for wrapping around
        overallwidth = x + edges[-1].spacing() + edges[1].spacing()
        overallheight = y + edges[0].spacing() + edges[2].spacing()
        t = self.thickness

        if self.move(overallwidth, overallheight, move, before=True):
            return

        self.moveTo(edges[-1].spacing(), edges[0].margin())

        for i, l in enumerate((x, y, x, y)):
            self.cc(callback, i, y=edges[i].startwidth() + self.burn)
            e1, e2 = edges[i], edges[i + 1]

            if i == 3 and side == "right":
                l -= t
                self.edges.get('e')(t)
                l += edges[i+1].startwidth()
                e2 = self.edges["e"]
                edges[i](l,
                     bedBolts=self.getEntry(bedBolts, i),
                     bedBoltSettings=self.getEntry(bedBoltSettings, i))
            elif i == 1 and side == "left":
                l -= t
                l += edges[i-1].startwidth()
                edges[i](l,
                     bedBolts=self.getEntry(bedBolts, i),
                     bedBoltSettings=self.getEntry(bedBoltSettings, i))
                self.edges.get('e')(t)
            else:
                if i == 3 and side == "left":
                    l += edges[i+1].startwidth() + edges[i-1].startwidth()
                    e2 = self.edges["e"]
                if i == 1 and side == "right":
                    l += edges[i+1].startwidth() + edges[i-1].startwidth()
                    e2 = self.edges["e"]

                if i == 2 and self.handle == "lip":
                    if b != "s":
                        l -= t
                        print(b)
                        if side == "left":
                            self.edges.get('e')(t)
                            edges[i](l,
                                bedBolts=self.getEntry(bedBolts, i),
                                bedBoltSettings=self.getEntry(bedBoltSettings, i))
                        elif side == "right":
                            edges[i](l,
                                bedBolts=self.getEntry(bedBolts, i),
                                bedBoltSettings=self.getEntry(bedBoltSettings, i))
                            self.edges.get('e')(t)
                    else:
                        self.edges.get('S')(l)
                        self.fingerHolesAt(0 if side == "left" else -t, 1.5*t, l-t, angle=180)
                else:
                    edges[i](l,
                        bedBolts=self.getEntry(bedBolts, i),
                        bedBoltSettings=self.getEntry(bedBoltSettings, i))

                if i == 2 and side == "left":
                    e1 = self.edges["e"]
                if i == 0 and side == "right":
                    e1 = self.edges["e"]
                if i == 0 and side == "left":
                    e1 = self.edges["e"]

            
            self.edgeCorner(e1, e2, 90)

        if holesMargin is not None:
            self.moveTo(holesMargin,
                        holesMargin + edges[0].startwidth())
            self.hexHolesRectangle(x - 2 * holesMargin, y - 2 * holesMargin, settings=holesSettings)

        self.move(overallwidth, overallheight, move, label=label)

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


#todo stackable top/bottom