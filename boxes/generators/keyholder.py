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


class HangerEdge(edges.BaseEdge):
    char = "H"

    def margin(self) -> float:
        return self.hook_height * 0.7

    def __call__(self, l, **kw):
        # Radius of the bottom part of the hook
        radius_outside = self.hook_height * 0.5
        radius_inside = radius_outside - self.hook_thickness

        # Make corners less sharp
        radius_burr = 1.5

        hookInnerHeight = self.hook_height * 0.7
        hookLength = self.hook_height * 0.7

        # Correct orientation
        self.polyline(0, -90)

        # Line bottom
        self.edge(hookLength - radius_outside)

        # Outer corner
        self.corner(90, radius_outside)

        # Line right
        self.edge(hookInnerHeight - radius_outside - self.hook_thickness / 2)

        # Semicircle at top
        self.corner(180, self.hook_thickness / 2)

        # Line left-ish
        self.edge(
            hookInnerHeight
            - self.hook_thickness
            - self.hook_thickness / 2
            - radius_inside
        )

        # Inner corner
        self.corner(-90, radius_inside)

        # Line bottom
        self.edge(hookLength - self.hook_thickness - 2 * radius_burr - radius_inside)
        self.corner(-90, radius_burr)

        # Line top
        self.edge(self.hook_height - self.hook_thickness - 2 * radius_burr)
        self.corner(90, radius_burr)

        # Correct orientation
        self.polyline(0, -90)


class KeyHolder(Boxes):
    """Wall organizer with hooks for keys or similar small items"""

    description = """Example for a KeyHolder with a slightly larger backplate and 8 hooks. This uses 6mm plywood for extra stability.

Closeup:

![KeyHolder-2](static/samples/KeyHolder-2.jpg)

Full picture:
"""

    ui_group = "WallMounted"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.argparser.add_argument(
            "--num_hooks", action="store", type=int, default=7, help="Number of hooks"
        )
        self.argparser.add_argument(
            "--hook_distance",
            action="store",
            type=float,
            default=20,
            help="Distance between hooks",
        )
        self.argparser.add_argument(
            "--hook_thickness",
            action="store",
            type=float,
            default=5,
            help="Thickness of hook",
        )
        self.argparser.add_argument(
            "--hook_height",
            action="store",
            type=float,
            default=20,
            help="Height of back part of hook",
        )

        # Padding around the hooks to define the size of the back plate
        self.argparser.add_argument(
            "--padding_top",
            action="store",
            type=float,
            default=10,
            help="Padding above hooks",
        )
        self.argparser.add_argument(
            "--padding_left_right",
            action="store",
            type=float,
            default=5,
            help="Padding left/right from hooks",
        )
        self.argparser.add_argument(
            "--padding_bot",
            action="store",
            type=float,
            default=30,
            help="Padding below hooks",
        )

        self.argparser.add_argument(
            "--mounting",
            action="store",
            type=boolarg,
            default=False,
            help="Add mounting holes",
        )

        self.addSettingsArgs(
            edges.FingerJointSettings, surroundingspaces=0.0, finger=1.0, space=1.0
        )
        self.addSettingsArgs(edges.MountingSettings)

    def yHoles(self):
        """
        Holes for hooks to attach to
        """
        posx = 0.5 * self.thickness
        posx += self.padding_left_right
        for _ in range(self.num_hooks):
            self.fingerHolesAt(posx, self.padding_bot, self.hook_height)
            posx += self.hook_distance + self.thickness

    def render(self):
        self.addPart(HangerEdge(self, 1))

        # Total height and width of the backplate
        h = self.hook_height + self.padding_bot + self.padding_top
        w = (
            (self.padding_left_right * 2)
            + self.num_hooks * self.thickness
            + (self.num_hooks - 1) * self.hook_distance
        )

        # Back plate
        self.rectangularWall(
            w,
            h,
            "eeGe" if self.mounting else "eeee",
            callback=[self.yHoles, None, None, None],
            move="up",
        )

        # Hooks
        for _ in range(self.num_hooks):
            self.rectangularWall(
                self.hook_thickness, self.hook_height, "eHef", move="right"
            )
