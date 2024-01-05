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

import boxes
from boxes import *
from boxes import lids

class TrayLayoutFile(Boxes):
    """Generate a layout file for a typetray."""
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
            "--output", action="store", type=str, default="traylayout.txt",
            help="Name of the layout text file.")

    def open(self) -> None:
        # Use empty open and close methods to avoid initializing the whole drawing infrastructure.
        pass

    def close(self) -> None:
        # Use empty open and close methods to avoid initializing the whole drawing infrastructure.
        pass

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
        with open(self.output, 'w') as f:
            f.write(str(self))


class TrayLayout(Boxes):
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
        self.buildArgParser("h", "hi", "outside", "sx", "sy")
        if self.UI == "web":
            self.argparser.add_argument(
                "--layout", action="store", type=str, default="")
        else:
            self.argparser.add_argument(
                "--input", action="store", type=argparse.FileType('r'),
                default="traylayout.txt",
                help="layout file")
            self.layout = None

    def vWalls(self, x: int, y: int) -> int:
        """Number of vertical walls at a crossing."""
        result = 0
        if y > 0 and self.vwalls[y - 1][x]:
            result += 1
        if y < len(self.y) and self.vwalls[y][x]:
            result += 1
        return result

    def hWalls(self, x: int, y: int) -> int:
        """Number of horizontal walls at a crossing."""
        result = 0
        if x > 0 and self.hwalls[y][x - 1]:
            result += 1
        if x < len(self.x) and self.hwalls[y][x]:
            result += 1
        return result

    def vFloor(self, x: int, y: int) -> bool:
        """Is there floor under vertical wall."""
        if y >= len(self.y):
            return False

        return (x > 0 and self.floors[y][x - 1]) or (x < len(self.x) and self.floors[y][x])

    def hFloor(self, x: int, y: int) -> bool:
        """Is there floor under horizontal wall."""
        if x >= len(self.x):
            return False
        return (y > 0 and self.floors[y - 1][x]) or (y < len(self.y) and self.floors[y][x])

    @restore
    def edgeAt(self, edge, x, y, length, angle=0):
        self.moveTo(x, y, angle)
        edge = self.edges.get(edge, edge)
        edge(length)

    def prepare(self):
        if self.layout:
            self.parse(self.layout.split('\n'))
        else:
            self.parse(self.input)

        if self.outside:
            self.x = self.adjustSize(self.x)
            self.y = self.adjustSize(self.y)
            self.h = self.adjustSize(self.h, e2=False)

            if self.hi:
                self.hi = self.adjustSize(self.hi, e2=False)

        self.hi = self.hi or self.h
        self.edges["s"] = boxes.edges.Slot(self, self.hi / 2.0)
        self.edges["C"] = boxes.edges.CrossingFingerHoleEdge(self, self.hi)
        self.edges["D"] = boxes.edges.CrossingFingerHoleEdge(self, self.hi, outset=self.thickness)

    def walls(self, move=None):
        lx = len(self.x)
        ly = len(self.y)
        # t = self.thickness
        # b = self.burn
        # t2 = self.thickness / 2.0

        self.ctx.save()

        # Horizontal Walls
        for y in range(ly + 1):
            if y == 0 or y == ly:
                h = self.h
            else:
                h = self.hi

            start = 0
            end = 0

            while end < lx:
                lengths = []
                edges = []

                while start < lx and not self.hwalls[y][start]:
                    start += 1

                if start == lx:
                    break

                end = start

                while end < lx and self.hwalls[y][end]:
                    if self.hFloor(end, y):
                        edges.append("f")
                    else:
                        edges.append("E")

                    lengths.append(self.x[end])
                    if self.hFloor(end, y) == 0 and self.hFloor(end + 1, y) == 0:
                        edges.append("EDs"[self.vWalls(end + 1, y)])
                    else:
                        edges.append("eCs"[self.vWalls(end + 1, y)])
                    lengths.append(self.thickness)
                    end += 1

                # remove last "slot"
                lengths.pop()
                edges.pop()
                self.rectangularWall(sum(lengths), h, [
                    boxes.edges.CompoundEdge(self, edges, lengths),
                    "f" if self.vWalls(end, y) else "e",
                    "e",
                    "f" if self.vWalls(start, y) else "e"],
                                     move="right")
                start = end

        self.ctx.restore()
        self.rectangularWall(10, h, "ffef", move="up only")
        self.ctx.save()

        # Vertical Walls
        for x in range(lx + 1):
            if x == 0 or x == lx:
                h = self.h
            else:
                h = self.hi
            start = 0
            end = 0

            while end < ly:
                lengths = []
                edges = []
                while start < ly and not self.vwalls[start][x]:
                    start += 1

                if start == ly:
                    break

                end = start

                while end < ly and self.vwalls[end][x]:
                    if self.vFloor(x, end):
                        edges.append("f")
                    else:
                        edges.append("E")

                    lengths.append(self.y[end])
                    if self.vFloor(x, end) == 0 and self.vFloor(x, end + 1) == 0:
                        edges.append("EDs"[self.hWalls(x, end + 1)])
                    else:
                        edges.append("eCs"[self.hWalls(x, end + 1)])
                    lengths.append(self.thickness)
                    end += 1
                # remove last "slot"
                lengths.pop()
                edges.pop()

                upper = [{"f": "e",
                          "s": "s",
                          "e": "e",
                          "E": "e",
                          "C": "e",
                          "D": "e"}[e] for e in reversed(edges)]
                edges = ["e" if e == "s" else e for e in edges]
                self.rectangularWall(sum(lengths), h, [
                    boxes.edges.CompoundEdge(self, edges, lengths),
                    "eFf"[self.hWalls(x, end)],
                    boxes.edges.CompoundEdge(self, upper, list(reversed(lengths))),
                    "eFf"[self.hWalls(x, start)]],
                                     move="right")
                start = end

        self.ctx.restore()
        self.rectangularWall(10, h, "ffef", move="up only")

    def base_plate(self, callback=None, move=None):
        lx = len(self.x)
        ly = len(self.y)
        t = self.thickness
        w = self.edges["F"].startwidth()
        b = self.burn
        t2 = self.thickness / 2.0

        tw = sum(self.x) + (lx - 1) * t + 2 * w
        th = sum(self.y) + (ly - 1) * t + 2 * w

        if self.move(tw, th, move, True):
            return

        for i, (x, y, a) in enumerate((
                (w, w + b, 0),
                (tw - w, w + b, 90),
                (tw - w, th - w + b, 180),
                (w, th - w + b, 270))):
            self.cc(callback, i, x, y, a)

        # Horizontal lines
        posy = w - t
        for y in range(ly, -1, -1):
            posx = w
            for x in range(lx):
                if self.hwalls[y][x]:
                    e = "F"
                else:
                    e = "e"

                if y < ly and self.floors[y][x]:
                    if y > 0 and self.floors[y - 1][x]:
                        # Inside Wall
                        if self.hwalls[y][x]:
                            self.fingerHolesAt(posx, posy + t2, self.x[x], angle=0)
                    else:
                        # Top edge
                        self.edgeAt(e, posx + self.x[x],
                                    posy + w + b, self.x[x],
                                    -180)
                        if x == 0 or not self.floors[y][x - 1]:
                            self.edgeAt("e", posx - w, posy + w + b, w, 0)
                        elif y == 0 or not self.floors[y - 1][x - 1]:
                            self.edgeAt("e", posx - t, posy + w + b, t, 0)
                        if x == lx - 1 or not self.floors[y][x + 1]:
                            self.edgeAt("e", posx + self.x[x], posy + w + b, w, 0)
                elif y > 0 and self.floors[y - 1][x]:
                    # Bottom Edge
                    self.edgeAt(e, posx, posy - b + t - w, self.x[x])
                    if x == 0 or not self.floors[y-1][x - 1]:
                        self.edgeAt("e", posx - w, posy + t - w - b, w)
                    elif x == 0 or y == ly or not self.floors[y][x - 1]:
                        self.edgeAt("e", posx - t, posy + t - w - b, t)
                    if x == lx - 1 or y == 0 or not self.floors[y-1][x + 1]:
                        self.edgeAt("e", posx + self.x[x], posy + t -w - b, w)
                posx += self.x[x] + self.thickness
            posy += self.y[y - 1] + self.thickness

        posx = w - t
        for x in range(lx + 1):
            posy = w
            for y in range(ly - 1, -1, -1):
                if self.vwalls[y][x]:
                    e = "F"
                else:
                    e = "e"
                if x > 0 and self.floors[y][x - 1]:
                    if x < lx and self.floors[y][x]:
                        # Inside wall
                        if self.vwalls[y][x]:
                            self.fingerHolesAt(posx + t2, posy, self.y[y])
                    else:
                        # Right edge
                        self.edgeAt(e, posx + w + b, posy, self.y[y], 90)
                        if y == 0 or not self.floors[y-1][x-1]:
                            self.edgeAt("e", posx + w + b, posy + self.y[y], w, 90)
                        elif x == lx or y == 0 or not self.floors[y - 1][x]:
                            self.edgeAt("e", posx + w + b, posy + self.y[y], t, 90)
                        if y == ly - 1 or not self.floors[y+1][x-1]:
                            self.edgeAt("e", posx + w + b, posy - w, w, 90)
                elif x < lx and self.floors[y][x]:
                    # Left edge
                    self.edgeAt(e, posx + t - w - b, posy + self.y[y], self.y[y], -90)
                    if y == 0 or not self.floors[y - 1][x]:
                        self.edgeAt("e", posx + t - w - b,
                                    posy + self.y[y] + w, w, -90)
                    elif x == 0 or y == 0 or not self.floors[y - 1][x - 1]:
                        self.edgeAt("e", posx + t - w - b,
                                    posy + self.y[y] + t, t, -90)
                    if y == ly - 1 or not self.floors[y + 1][x]:
                        self.edgeAt("e", posx + t - w - b, posy, w, -90)
                posy += self.y[y] + self.thickness
            if x < lx:
                posx += self.x[x] + self.thickness

        self.move(tw, th, move)

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
                        elif c == '-':
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
                            raise ValueError("""Can't parse line %i in layout: expected " ", "x" or "X" for char #%i""" % (nr + 1, n + 1))
                    else:
                        if c == ' ':
                            w.append(False)
                        elif c == '|':
                            w.append(True)
                        else:
                            raise ValueError("""Can't parse line %i in layout: expected " ", or "|" for char #%i""" % (nr + 1, n + 1))

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
                raise ValueError("Wrong number of vertical walls in line %i: %i (%i expected)" % (nr, len(walls), lx + 1))

        self.x = x
        self.y = y
        self.hwalls = hwalls
        self.vwalls = vwalls
        self.floors = floors

    def render(self) -> None:
        self.prepare()
        self.walls()
        self.base_plate(move="up")
        self.lid(sum(self.x) + (len(self.x)-1) * self.thickness,
                 sum(self.y) + (len(self.y)-1) * self.thickness)
