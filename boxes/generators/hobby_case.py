# Copyright (C) 2016 Florian Festi
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
from __future__ import annotations

import io

import boxes
from boxes import *
from boxes import lids


class HobbyCaseFile(Boxes):
    """Generate a layout file for a hobbycase."""
    # This class generates the skeleton text file that can then be edited
    # to describe the actual box

    description = """This is a two step process. This is step 1.
The layout is based on a grid of sizes in x and y direction.
Choose how many distances you need in both directions.
The actual sizes and all other settings can be entered in the second step."""

    webinterface = False

    ui_group = "Tray"

    sx: list[float] = []  # arg input
    sy: list[float] = []  # arg input
    hwalls: list[list[bool]] = []
    vwalls: list[list[bool]] = []
    floors: list[list[bool]] = []

    def __init__(self, input=None, webargs=False) -> None:
        Boxes.__init__(self)
        self.argparser = argparse.ArgumentParser()
        self.buildArgParser("sx", "sy")
        self.argparser.add_argument(
            "--output", action="store", type=str, default="hobbycaselayout.txt",
            help="Name of the layout text file.")

    def open(self) -> None:
        # Use empty open and close methods to avoid initializing the whole drawing infrastructure.
        pass

    def close(self):
        # Use empty open and close methods to avoid initializing the whole drawing infrastructure.
        return io.BytesIO(bytes(str(self), 'utf-8'))

    def fillDefault(self, sx: list[float], sy: list[float]) -> None:
        self.sx = sx
        self.sy = sy
        x = len(sx)
        y = len(sy)
        self.hwalls = [[True for _ in range(x)] for _ in range(y + 1)]
        self.vwalls = [[True for _ in range(x + 1)] for _ in range(y)]
        self.floors = [[True for _ in range(x)] for _ in range(y)]

    def __str__(self) -> str:
        r = []

        for i, x in enumerate(self.sx):
            r.append(" |" * i + " ,> %.1fmm\n" % x)

        for hwalls, vwalls, floors, y in zip(self.hwalls, self.vwalls, self.floors, self.sy):
            r.append("".join("+" + " -"[h] for h in hwalls) + "+\n")
            r.append("".join((" |"[v] + "X "[f] for v, f in zip(vwalls, floors))) + " |"[vwalls[-1]] + " %.1fmm\n" % y)
        r.append("".join("+" + " -"[h] for h in self.hwalls[-1]) + "+\n")

        return "".join(r)

    def render(self) -> None:
        self.fillDefault(self.sx, self.sy)


def create_custom_array(values, inbetween_value, ends_value=None):
    array = [elem for pair in zip(values, [inbetween_value] * (len(values) - 1)) for elem in pair] + [values[-1]]
    if not ends_value:
        return array
    return [ends_value] + array + [ends_value]


class HobbyCaseLayout(Boxes):
    """Generate a typetray from a layout file."""

    # This class reads in the layout either from a file (with --input) or
    # as string (with --layout) and turns it into a drawing for a box.

    ui_group = "Tray"

    description = """This is a two step process. This is step 2.
Edit the layout text graphics to adjust your tray.
Put in the sizes for each column and row. You can replace the hyphens and
vertical bars representing the walls with a space character to remove the walls.
You can replace the space characters representing the floor by a "X" to remove the floor for this compartment.
"""

    def __init__(self) -> None:
        super().__init__()
        self.addSettingsArgs(boxes.edges.FingerJointSettings)
        self.addSettingsArgs(lids.LidSettings)
        self.argparser.add_argument("--unitD", action="store", type=float, default=128)
        self.argparser.add_argument("--unitH", action="store", type=float, default=50)
        self.argparser.add_argument("--unitW", action="store", type=str, default="215 215 215")
        self.argparser.add_argument("--cols", action="store", type=int, default=3)
        self.argparser.add_argument("--rows", action="store", type=int, default=6)
        self.argparser.add_argument("--shelvesNs", action="store", type=str, default="2 3 2")

    @restore
    def edgeAt(self, edge, x, y, length, angle=0):
        self.moveTo(x, y, angle)
        edge = self.edges.get(edge, edge)
        edge(length)

    def prepare(self):
        self.unitW = [float(w) for w in self.unitW.split()]

        self.sumW = sum(self.unitW)

        self.shelvesNs = [int(w) for w in self.shelvesNs.split()]
        self.externalDepth = self.unitD + 2 * self.thickness
        self.internalDepth = self.unitD

    def topAndBottom(self):
        x = self.sumW + 2 * (self.cols - 1) * self.thickness
        y = self.externalDepth
        self.rectangularWall(x, y, "FFeF", move="up", label="top (%ix%i)" % (x, y))
        self.rectangularWall(x, y, "FFeF", move="up", label="bottom (%ix%i)" % (x, y))
        # self.rectangularWall(x, y, "eeee", move="up", label="reference top/bottom (%ix%i)" % (x, y))

    def verticalWalls(self):
        self.ctx.save()
        x_inner = self.internalDepth
        x_outer = self.externalDepth
        y = self.rows * self.unitH + (self.rows + 1) * self.thickness

        self.rectangularWall(x_outer, y, "fffe", move="right", label="left\n(%ix%i)" % (x_outer, y))

        self.partsMatrix(2 * (self.cols - 1), 0, "right",
                         self.rectangularWall,
                         x_inner, y, "fffe", label="vertical wall\n(%ix%i)" % (x_inner, y))

        self.rectangularWall(x_outer, y, "fffe", move="up", label="right\n(%ix%i)" % (x_outer, y))

        self.move(x_outer, y + 2 * self.thickness, "up")

    def cover(self, move=None):
        x = self.sumW + 2 * self.cols * self.thickness
        y = self.rows * self.unitH + (self.rows + 1) * self.thickness
        self.rectangularWall(x, y, "eeze", move="up", label="cover plate\n(%ix%i)" % (x, y))

    def shelves(self, move=None):
        for columnIndex, unitWidth in enumerate(self.unitW):
            x = unitWidth
            y = self.internalDepth
            self.partsMatrix(self.shelvesNs[columnIndex], 0, "up",
                             self.rectangularWall,
                             x, y, "efff", label="shelf (column %i)\n(%ix%i)" % (columnIndex, x, y))

    def base_plate(self):
        tw = self.sumW + 2 * self.cols * self.thickness
        th = self.rows * self.unitH + (self.rows + 1) * self.thickness
        self.ctx.save()

        # TODO: use CompoundEdge on all outer edges/joints
        self.rectangularWall(tw, th, "fFfF", label="base plate\n(%ix%i)" % (tw, th))

        self.fingerHolesAt(1.5 * self.thickness, 1.5 * self.thickness, self.unitW[0], angle=0)
        self.fingerHolesAt(1.5 * self.thickness, 1.5 * self.thickness, self.unitW[0], angle=90)

        if self.cols > 1:
            for col in range(1, self.cols):
                # TODO: Fix horizonal and vertical shifts by weird margins
                posx = sum(self.unitW[:col]) + (col) * self.thickness
                posy = 1.5 * self.thickness

                self.fingerHolesAt(posx, posy, th, angle=90)
                self.fingerHolesAt(posx + self.thickness, posy, th, angle=90)
        self.ctx.restore()
        self.ctx.save()
        if self.rows > 1:
            for row in range(1, self.rows):
                for col in range(self.cols):
                    posx = sum(self.unitW[:col]) + col * 2 * self.thickness + (col + 1) * 1.25 * self.thickness
                    posy = row * self.unitH + row * self.thickness + 1.5 * self.thickness
                    w = self.unitW[col]

                    self.fingerHolesAt(posx, posy, w, angle=0)
        self.ctx.restore()
        # self.move(tw, th, "up")

    def new_base_plate(self, move=None):
        F = self.edges["F"].startwidth()
        tx = sum(self.unitW) + 2 * (self.cols - 1) * self.thickness + 2 * F
        ty = self.rows * self.unitH + (self.rows - 1) * self.thickness + 2 * F

        horizontalEdges = "F" + "eF" * self.cols
        horizontalLengths = [F] + [item for w in self.unitW for item in (w, 2 * self.thickness)] + [F]

        verticalLengths = [self.unitH + self.thickness] * self.rows
        verticalLengths[-1] += self.thickness

        horizontalLengths = self.unitW
        horizontalInbetween = 2 * self.thickness
        verticalLengths = [self.unitH] * self.rows
        verticalInbetween = self.thickness

        for col in range(self.cols):
            for row in range(1, self.rows):
                posx = 2.25 * self.thickness + sum(self.unitW[:col]) + col * 2 * self.thickness
                posy = F + row * self.unitH + row * self.thickness + 0.75 * self.thickness
                self.fingerHolesAt(posx, posy, self.unitW[col], angle=0)

        for col in range(1, self.cols):
            posx = 1.75 * self.thickness + sum(self.unitW[:col]) + col * 2 * self.thickness
            posy = F + 0.75 * self.thickness
            self.fingerHolesAt(posx, posy, ty - 2 * F, angle=90)
            self.fingerHolesAt(posx-self.thickness, posy, ty - 2 * F, angle=90)


        self.rectangularWall(tx, ty,
                             [
                                 self.segmented_edge(horizontalLengths, "F", horizontalInbetween, "E", F, "E"),
                                 self.segmented_edge(verticalLengths, "F", verticalInbetween, "E", F, "E"),
                                 self.segmented_edge(list(reversed(horizontalLengths)), "F", horizontalInbetween, "E",
                                                     F, "E"),
                                 self.segmented_edge(list(reversed(verticalLengths)), "F", verticalInbetween, "E", F,
                                                     "E"),
                             ], label="base plate\n(%ix%i)" % (tx, ty), move="up")

        # self.move(tx, ty, "up")

    def test_ref(self):
        tx = sum(self.unitW) + 2 * (self.cols) * self.thickness
        ty = self.rows * self.unitH + (self.rows + 1) * self.thickness
        self.rectangularWall(tx, ty, "eeee", move="up", label="top (%ix%i)" % (tx, ty))

    def segmented_edge(self, segments_lengths, segment_edge, inbetween_length, inbetween_edge, ends_length=None,
                       ends_edge=None):
        lengths = create_custom_array(segments_lengths, inbetween_length, ends_length)
        _edges = create_custom_array([segment_edge] * len(segments_lengths), inbetween_edge, ends_edge)
        return boxes.edges.CompoundEdge(self, _edges, lengths)

    def parse(self, input):
        x = []
        y = []
        hwalls = []
        vwalls = []
        floors = []
        for nr, line in enumerate(input):
            if not line or line[0] == "#":
                continue
            m = re.match(r"( \|)* ,>\s*(\d*\.?\d+)\s*mm\s*", line)
            if m:
                x.append(float(m.group(2)))
                continue
            if line[0] == '+':
                w = []
                for n, c in enumerate(line[:len(x) * 2 + 1]):
                    if n % 2:
                        if c == ' ':
                            w.append(False)
                        elif c == '-' or c == '=':
                            w.append(True)
                        else:
                            pass
                            # raise ValueError(line)
                    else:
                        if c != '+':
                            pass
                            # raise ValueError(line)

                hwalls.append(w)
            if line[0] in " |":
                w = []
                f = []
                for n, c in enumerate(line[:len(x) * 2 + 1]):
                    if n % 2:
                        if c in 'xX':
                            f.append(False)
                        elif c == ' ':
                            f.append(True)
                        else:
                            raise ValueError(
                                """Can't parse line %i in layout: expected " ", "x" or "X" for char #%i""" % (
                                    nr + 1, n + 1))
                    else:
                        if c == ' ':
                            w.append(False)
                        elif c == '|':
                            w.append(True)
                        else:
                            raise ValueError("""Can't parse line %i in layout: expected " ", or "|" for char #%i""" % (
                                nr + 1, n + 1))

                floors.append(f)
                vwalls.append(w)
                m = re.match(r"([ |][ xX])+[ |]\s*(\d*\.?\d+)\s*mm\s*", line)
                if not m:
                    raise ValueError("""Can't parse line %i in layout: Can read height of the row""" % (nr + 1))
                else:
                    y.append(float(m.group(2)))

        # check sizes
        lx = len(x)
        ly = len(y)

        if lx == 0:
            raise ValueError("Need more than one wall in x direction")
        if ly == 0:
            raise ValueError("Need more than one wall in y direction")
        if len(hwalls) != ly + 1:
            raise ValueError("Wrong number of horizontal wall lines: %i (%i expected)" % (len(hwalls), ly + 1))
        for nr, walls in enumerate(hwalls):
            if len(walls) != lx:
                raise ValueError("Wrong number of horizontal walls in line %i: %i (%i expected)" % (nr, len(walls), lx))
        if len(vwalls) != ly:
            raise ValueError("Wrong number of vertical wall lines: %i (%i expected)" % (len(vwalls), ly))
        for nr, walls in enumerate(vwalls):
            if len(walls) != lx + 1:
                raise ValueError(
                    "Wrong number of vertical walls in line %i: %i (%i expected)" % (nr, len(walls), lx + 1))

        self.x = x
        self.y = y
        self.hwalls = hwalls
        self.vwalls = vwalls
        self.floors = floors

    def render(self) -> None:
        self.prepare()
        # self.test_ref()
        self.new_base_plate()
        self.cover()
        self.topAndBottom()
        self.verticalWalls()
        self.shelves()
        # self.base_plate()
