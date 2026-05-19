# Copyright (C) 2026 Florian Festi
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

from typing import cast

from boxes import *
from boxes.args import FloatStepper, IntStepper
from boxes.drawing import Context


class _FlushEdge(edges.BaseEdge):
    """Plain straight edge with the same bounding-box spacing as FingerHoleEdge ('h').
    Use it as a drop-in replacement for 'h' when you want the same layout footprint
    but no finger holes drawn (e.g. a flush/closed side of a panel)."""

    def __call__(self, length: float, **kw) -> None:
        self.boxes.edge(length)

    def startWidth(self) -> float:
        # mirrors FingerHoleEdge.startWidth()
        return self.settings.edge_width + self.settings.thickness

    def margin(self) -> float:
        return 0.0


class BoxWithDrawer(Boxes):
    """Two-piece outer box with a separate-height sliding drawer."""

    ui_group = "Box"
    tags: list[str] = ["unstable", "tcg"]

    description = """
A two-piece box where the inner volume can be filled with a dedicated drawer.
Use *drawer_h* to control drawer height independently from *h* / *hi*.
"""

    x: float = 40.0
    y: float = 20.0
    h: float = 30.0
    hi: float = 0.0
    outside: bool = False
    play: float = 0.15
    drawer_h: float = 20.0
    drawer_opening: bool = True
    magnet_nb: int = 1
    magnet_diameter: float = 6.0
    magnet_distance: float = 0.0
    magnet_h: float = 0.0
    side_magnet_diameter: float = 6.0

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.buildArgParser(x=self.x, y=self.y, h=self.h, hi=self.hi, outside=self.outside)
        self.addSettingsArgs(edges.FingerJointSettings, finger=2.0, space=2.0)
        self.argparser.add_argument(
            "--play",
            action="store",
            type=FloatStepper(0.05),
            default=self.play,
            help="play between fitting parts as multiple of the wall thickness",
        )
        self.argparser.add_argument(
            "--drawer_h",
            action="store",
            type=FloatStepper(1.0),
            default=self.drawer_h,
            help="height of the inner drawer [mm]",
        )
        self.argparser.add_argument(
            "--drawer_opening",
            action="store",
            type=boolarg,
            default=self.drawer_opening,
            help="reduce inner front wall to let drawer slide under it",
        )
        self.argparser.add_argument(
            "--magnet_nb",
            action="store",
            type=IntStepper(1),
            default=self.magnet_nb,
            help="number of magnets on the front walls (0 = none)",
        )
        self.argparser.add_argument(
            "--magnet_diameter",
            action="store",
            type=FloatStepper(0.1),
            default=self.magnet_diameter,
            help="diameter of each magnet hole [mm]",
        )
        self.argparser.add_argument(
            "--magnet_distance",
            action="store",
            type=FloatStepper(0.5),
            default=self.magnet_distance,
            help="centre-to-centre spacing between magnets (0 = auto, evenly distributed) [mm]",
        )
        self.argparser.add_argument(
            "--magnet_h",
            action="store",
            type=FloatStepper(0.5),
            default=self.magnet_h,
            help="vertical offset of magnet holes from the auto position (0 = auto) [mm]",
        )
        self.argparser.add_argument(
            "--side_magnet_diameter",
            action="store",
            type=FloatStepper(0.1),
            default=self.side_magnet_diameter,
            help="diameter of the side magnet hole on the right walls (0 = none) [mm]",
        )

    def _side_magnet_cb(self, wall_length: float, y_pos: float) -> None:
        """Single INNER_CUT hole centred on a side wall at the given y position."""
        d = self.side_magnet_diameter
        if d <= 0:
            return
        with self.saved_context():
            self.set_source_color(Color.INNER_CUT)
            self.hole(wall_length / 2, y_pos, d=d)

    def _magnet_holes_cb(self, wall_width: float, wall_height: float, near_top: bool = True) -> None:
        """Drill magnet holes near the opening edge of a front wall.

        near_top=True  → holes near the drawing top    (inner walls, opening at top)
        near_top=False → holes near the drawing bottom (outer walls, rotated 180°, opening at bottom)
        """
        n = self.magnet_nb
        d = self.magnet_diameter
        t = self.thickness
        if n <= 0 or d <= 0:
            return
        if self.magnet_distance == 0.0:
            spacing = wall_width / (n + 1)
            start_x = spacing
        else:
            spacing = self.magnet_distance
            start_x = wall_width / 2 - (n - 1) / 2 * spacing
        y_pos = (wall_height - t - d / 2) if near_top else (t + d / 2)
        if self.magnet_h != 0.0:
            y_pos = self.magnet_h
        with self.saved_context():
            self.set_source_color(Color.INNER_CUT)
            for i in range(n):
                self.hole(start_x + i * spacing, y_pos, d=d)

    def render(self) -> None:

        x = self.x
        y = self.y
        drawer_h = self.drawer_h
        t = self.thickness
        p = self.play * t
        # When drawer_opening is True a shelf panel (thickness t) sits between
        # the drawer compartment and the upper compartment, so the total wall
        # height must include that extra t.
        shelf_t = t * 2 if self.drawer_opening else t

        h = self.h + self.drawer_h + shelf_t
        if self.hi > 0:
            hi = self.hi + self.drawer_h + shelf_t
        else:
            hi = self.h + self.drawer_h + shelf_t

        if self.outside:
            x -= 4 * t + 2 * p
            y -= 4 * t + 2 * p
            h -= 2 * t
            hi -= 2 * t
            drawer_h -= 2 * t

        drawer_h = max(t, min(drawer_h, hi))
        drawer_x = max(t, x - (2 * t + 2 * p))
        drawer_y = y if self.drawer_opening else max(t, y - (2 * t + 2 * p))

        def wall_cb(length: float, line_color: list[float]) -> None:
            """Finger holes for shelf + split line at drawer_h in the given color."""
            with self.saved_context():
                self.set_source_color(Color.INNER_CUT)
                self.fingerHolesAt(0, drawer_h + t + t / 2, length, angle=0)
            with self.saved_context():
                self.set_source_color(line_color)
                self.moveTo(0, drawer_h + t)
                self.edge(length)
                ctx = cast(Context, self.ctx)
                ctx.stroke()

        # Make the second shell slightly bigger so it slips over the first one.
        self.edges["f"].settings.setValues(
            t,
            False,
            edge_width=self.edges["f"].settings.edge_width + p,
        )

        shell_names = ("inner", "outer")
        for i, shell_name in enumerate(shell_names):
            d = i * 2 * (t + p)
            height = hi if i == 0 else h
            wall_w = x + d
            # Outer walls are drawn rotated 180° so the opening edge (e) is at
            # the bottom of the piece – matching how they are actually assembled.
            # Inner: opening at top  → edges "fFeF" / "ffef"
            # Outer: opening at bottom → edges "eFfF" / "efff"
            front_edges = "fFeF" if i == 0 else "eFfF"
            side_edges  = "ffef" if i == 0 else "efff"
            near_top    = True

            def _front_cb(
                ww: float = wall_w,
                ht: float = height,
                idx: int = i,
                nt: bool = near_top,
            ) -> None:
                if idx == 0 and self.drawer_opening:
                    wall_cb(ww, Color.OUTER_CUT)
                self._magnet_holes_cb(ww, ht, near_top=nt)

            def _back_cb(
                ww: float = wall_w,
                idx: int = i,
            ) -> None:
                # back wall: shelf split line only, no magnets
                if idx == 0 and self.drawer_opening:
                    wall_cb(ww, Color.OUTER_CUT)

            # Side magnet y position in drawing coordinates.
            # Inner ("ffef"): closed end at drawing bottom → drawer_h/2 from bottom.
            # Outer ("efff"): open end at drawing bottom, but physically both shells
            #   rest with the same base level → also drawer_h/2 from drawing bottom.
            _side_y: float = drawer_h / 2

            def _inner_right_cb(
                yd: float = y + d,
                sy: float = _side_y,
            ) -> None:
                wall_cb(yd, Color.ETCHING)
                self._side_magnet_cb(yd, sy)

            def _outer_right_cb(
                yd: float = y + d,
                sy: float = _side_y,
            ) -> None:
                self._side_magnet_cb(yd, sy)

            with self.saved_context():
                self.rectangularWall(wall_w, height, front_edges,
                                     label=f"{shell_name} front",
                                     callback=[_front_cb],
                                     move="right")

                if i == 0 and self.drawer_opening:
                    self.rectangularWall(y + d, height, side_edges,
                                         label=f"{shell_name} right",
                                         callback=[_inner_right_cb],
                                         move="right")
                else:
                    self.rectangularWall(y + d, height, side_edges,
                                         label=f"{shell_name} right",
                                         callback=[_outer_right_cb],
                                         move="right")

                if i == 0 and self.drawer_opening:
                    self.rectangularWall(wall_w, height, front_edges,
                                         label=f"{shell_name} back",
                                         callback=[_back_cb],
                                         move="right")
                else:
                    self.rectangularWall(wall_w, height, front_edges, label=f"{shell_name} back", move="right")

                if i == 0 and self.drawer_opening:
                    self.rectangularWall(y + d, height, side_edges,
                                         label=f"{shell_name} left",
                                         callback=[lambda yd=y + d: wall_cb(yd, Color.ETCHING)],
                                         move="right")
                else:
                    self.rectangularWall(y + d, height, side_edges, label=f"{shell_name} left", move="right")
            self.rectangularWall(y, height, side_edges, move="up only")

        # Top and bottom
        with self.saved_context():
            outer_extra = 2 * (t + p)
            inner_extra = 2 * t

            if self.drawer_opening:
                self.rectangularWall(x, y, "ffff", label="shelf bottom", bedBolts=None, move="right")
            self.rectangularWall(x + outer_extra, y + outer_extra, "FFFF", label="outer top", bedBolts=None, move="right")

            if self.drawer_opening:
              fe = _FlushEdge(self, self.edges["h"].settings)
              self.rectangularWall(x - inner_extra, y - inner_extra, [fe, self.edges["h"], fe, self.edges["h"]],
                                   label="inner bottom flush", bedBolts=None, move="right")
            else:
              self.rectangularWall(x - inner_extra, y - inner_extra, "hhhh", label="inner bottom", bedBolts=None, move="right")

        # No drawing, just for movement
        self.rectangularWall(x + outer_extra, y + outer_extra, "hhhh", move="up only")

        # Drawer
        with self.saved_context():
            self.rectangularWall(drawer_x, drawer_h, "FFeF", label="drawer front", move="right")
            self.rectangularWall(drawer_y, drawer_h, "ffef", label="drawer right",
                                 callback=[lambda dy=drawer_y, dh=drawer_h, t=self.thickness: self._side_magnet_cb(dy, dh / 2 - t)],
                                 move="right")
            self.rectangularWall(drawer_x, drawer_h, "FFeF", label="drawer back", move="right")
            self.rectangularWall(drawer_y, drawer_h, "ffef", label="drawer left", move="right")
            self.rectangularWall(drawer_x, drawer_y, "fFfF", label="drawer bottom", move="right")
        self.rectangularWall(drawer_x, drawer_y, "FfFf", move="up only")
