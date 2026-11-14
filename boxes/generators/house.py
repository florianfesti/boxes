#!/usr/bin/env python3
# Copyright (C) 2013-2024 Florian Festi
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


class ExtendedEdge(edges.BaseEdge):
    """Wrap an edge and continue it straight on the same baseline

    Unlike CompoundEdge no step is inserted between the two sections, so the
    plain extension continues exactly where the wrapped edge (e.g. finger
    joint notches) ends.

    :param edge: wrapped edge, drawn over length - extra
    :param extra: length of the plain extension
    :param before: draw the extension before the wrapped edge
    """

    def __init__(self, boxes, edge, extra, before=False) -> None:
        super().__init__(boxes, None)
        self.edge_ = edge
        self.extra = extra
        self.before = before

    def startWidth(self) -> float:
        return self.edge_.startWidth()

    def endWidth(self) -> float:
        return self.edge_.endWidth()

    def margin(self) -> float:
        return self.edge_.margin()

    def __call__(self, length, **kw):
        if self.before:
            self.edge(self.extra)
        self.edge_(length - self.extra, **kw)
        if not self.before:
            self.edge(self.extra)


class House(Boxes):
    """House shaped box with a 90° gable roof, open at the front"""

    ui_group = "Box"

    description = """Looking at the open front the box looks like this:

```
  /\\
 /  \\
|    |
+----+
```

Parts: house shaped back plate, two side walls, a floor and two roof panels
(45° slope each, 90° at the ridge). The sizes are inner sizes of the
rectangular base (x = width, y = depth) and the height h of the walls up to
the eaves.

The 45° corner between side wall and roof can't be done with a finger joint.
There are two options for the side walls:

* **full**: The walls reach up to the roof and overlap with it. An etched
  line is added on the outside of each wall: one material thickness below the
  top edge and shorter than the depth by *cutline_inset*. Remove the material
  between this line and the top edge of the inside (bevel at 45°) so the
  roof sits flush on the wall.
* **flush**: The walls end flush with the underside of the roof at the outer
  edge. The back plate sticks out above the wall to cover the small
  triangular gap between wall and roof.

The two roof panels are joined at the ridge with a finger joint.

Without overhang (*overhang* = 0) the walls are always full height and the
back plate is a plain house outline. The roof ends at the inner top corner
of the wall.

* **full**: a mitre joint. The wall and the roof meet at an outer angle of
  135°, so both parts get a 22.5° bevel. Both are cut a bit longer
  (by thickness * tan(22.5°)) and get an etched line on the inside
  (walls) / underside (roof) marking the bevel. Remove the material between
  the line and the outer edge by filing or sanding at 22.5°. The etched
  side of all parts is meant to face the inside of the house.
* **flush**: the roof ends square at the inner top corner of the wall. No
  bevel, so a small gap remains on the outside.

The roof depth can be set independently with *roof_depth* (0 = same as y),
e.g. to let the roof overlap to the front.

The second wall is mirrored so the etched line is on the outside of both walls
when the parts are laid out with the etched side up.
"""

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser("x", "y", "h")
        self.argparser.add_argument(
            "--wall_style", action="store", type=str, default="full",
            choices=("full", "flush"),
            help="full: walls overlap with the roof and get an etched 45° cut line; "
                 "flush: walls end flush with the roof leaving a gap")
        self.argparser.add_argument(
            "--overhang", action="store", type=float, default=10.0,
            help="roof overhang along the slope (0 adds etched cut lines to the roof panels)")
        self.argparser.add_argument(
            "--roof_depth", action="store", type=float, default=0.0,
            help="depth of the roof panels (inner depth y + back plate thickness are covered); "
                 "0 = same as y, larger values let the roof overlap to the front")
        self.argparser.add_argument(
            "--cutline_inset", action="store", type=float, default=2.0,
            help="how much shorter than the depth the etched cut line is (in mm)")

    def etchLine(self, y, height, tabs_right=True):
        """Etched line at the given height, centered on the whole wall

        The wall is y long plus the tabs of the finger joint to the back plate
        (one material thickness). The line is centered over this whole length,
        which is the depth of the roof joint.

        :param y: length of the wall body
        :param height: height above the bottom edge of the wall body
        :param tabs_right: True if the back plate tabs are at the x=y end of the wall,
            False if they are at the x=0 end
        """
        inset = self.cutline_inset
        length = y + self.thickness
        if length - inset <= 0:
            return
        start = 0.0 if tabs_right else -self.thickness
        with self.saved_context():
            self.set_source_color(Color.ETCHING)
            self.ctx.move_to(start + inset / 2.0, height)
            self.ctx.line_to(start + length - inset / 2.0, height)
            self.ctx.stroke()

    def backPlate(self, x, h, move=None, label=""):
        """House shaped plate: floor edge, right wall, two slopes, left wall"""
        t = self.thickness
        f = self.edges["f"]
        # stepped back plate only if the wall is lowered by the roof thickness
        flush = self.wall_style == "flush" and self.overhang > 0
        slope = x / 2 ** 0.5

        tw = x + 2 * t
        th = h + x / 2 + 2 * t

        if self.move(tw, th, move, True, label=label):
            return

        self.moveTo(t, t)
        f(x)
        self.corner(90)
        # right wall
        if flush:
            # wall ends at h - t; the plate covers the triangular gap
            # between wall and roof by sticking out to the wall's outer face
            f(h - t)
            self.corner(-90)
            self.edge(t)
            self.corner(135)
            self.edge(t * 2 ** 0.5)
        else:
            f(h)
            self.corner(45)
        f(slope)
        self.corner(90)
        f(slope)
        # left wall
        if flush:
            self.edge(t * 2 ** 0.5)
            self.corner(135)
            self.edge(t)
            self.corner(-90)
            f(h - t)
        else:
            self.corner(45)
            f(h)
        self.corner(90)

        self.move(tw, th, move, label=label)

    def roofPanel(self, y, slope, extra, ridge="f", mirror=False, move=None, label=""):
        """Roof panel

        :param y: inner depth
        :param slope: length of the matching slope of the back plate
        :param extra: additional length at the ridge
        :param ridge: edge type at the ridge ("f" fingers, "F" matching notches)
        :param mirror: back plate side on the right instead of the left. The
            two roof panels are mirror images of each other, so one of them has
            to be drawn mirrored to have the etched side on the outside.
        """
        t = self.thickness
        F = self.edges["F"]
        ridge_edge = self.edges[ridge]
        if self.overhang > 0:
            eave = t * 2 ** 0.5 + self.overhang
        else:
            # ends at the inner top corner of the wall, mitre adds a bit
            eave = self.mitre
        w = eave + slope + extra

        front = self.roof_front
        tw = y + t + front
        th = w + (t if ridge == "f" else 0)

        if self.move(tw, th, move, True, label=label):
            return

        if self.mitre > 0:
            # no overhang: etched line on the underside (part is drawn
            # flipped, see render()) marking the 22.5° bevel. The line is at
            # the underside length, the outer surface is longer by the
            # mitre offset.
            inset = self.cutline_inset
            if tw - inset > 0:
                with self.saved_context():
                    self.set_source_color(Color.ETCHING)
                    self.ctx.move_to(inset / 2.0, self.mitre)
                    self.ctx.line_to(tw - inset / 2.0, self.mitre)
                    self.ctx.stroke()

        if mirror:
            self.edge(y + front)
            self.edge(t)
            self.corner(90)
            self.edge(eave)
            F(slope)
            self.edge(extra)
            self.corner(90)
            self.edge(t)
            ridge_edge(y + front)
            self.corner(90)
            self.edge(w)
            self.corner(90)
        else:
            self.moveTo(t, 0)
            self.edge(y + front)
            self.corner(90)
            self.edge(w)
            self.corner(90)
            ridge_edge(y + front)
            self.edge(t)
            self.corner(90)
            self.edge(extra)
            F(slope)
            self.edge(eave)
            self.corner(90)
            self.edge(t)

        self.move(tw, th, move, label=label)

    def render(self):
        x, y, h = self.x, self.y, self.h
        t = self.thickness

        if h <= t:
            raise ValueError("House: h must be larger than the material thickness")

        slope = x / 2 ** 0.5

        # extra roof depth at the front (relative to the side walls)
        self.roof_front = (self.roof_depth - y) if self.roof_depth > 0 else 0.0
        if y + self.roof_front <= 0:
            raise ValueError("House: roof_depth must be positive")

        # offset between inner and outer face of a 22.5° mitre
        self.mitre = ((2 ** 0.5 - 1) * t
                      if self.overhang <= 0 and self.wall_style == "full" else 0.0)

        wallEdges = ("FFee", "FeeF")
        if self.overhang <= 0 and self.wall_style == "full":
            # mitre: outer face is higher by self.mitre, the finger joint
            # to the back plate keeps the length h
            m = self.mitre
            wallh = h + m
            cb = ([lambda: self.etchLine(y, h, True)],
                  [lambda: self.etchLine(y, h, False)])
            F = self.edges["F"]
            up = ExtendedEdge(self, F, m)
            down = ExtendedEdge(self, F, m, before=True)
            wallEdges = (["F", up, "e", "e"], ["F", "e", "e", down])
        elif self.overhang <= 0:
            # square full height walls
            wallh = h
            cb = (None, None)
        elif self.wall_style == "full":
            wallh = h
            cb = ([lambda: self.etchLine(y, wallh - t, True)],
                  [lambda: self.etchLine(y, wallh - t, False)])
        else:
            wallh = h - t
            cb = (None, None)

        self.backPlate(x, h, move="right", label="Back plate")
        self.rectangularWall(y, wallh, wallEdges[0], callback=cb[0], move="right", label="Left wall")
        self.rectangularWall(y, wallh, wallEdges[1], callback=cb[1], move="right", label="Right wall")
        self.rectangularWall(x, y, "efFf", move="right", label="Floor")
        # without overhang and full walls the whole roof is flipped so the
        # etched line ends up on the underside
        flip = self.overhang <= 0 and self.wall_style == "full"
        self.roofPanel(y, slope, 0, "f", mirror=flip, move="right", label="Roof left")
        # Ridge joint: the "f" panel ends at the inner face of the other panel
        # and its fingers reach through to the outer face. The "F" panel runs
        # up to the outer face of the "f" panel, so its body is one material
        # thickness longer. Both panels end up with the same total length.
        # The right panel is drawn mirrored so that the etched (outer) side
        # is up for both panels.
        self.roofPanel(y, slope, t, "F", mirror=not flip, move="right", label="Roof right")
