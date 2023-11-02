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

from math import *

from boxes import *


class LaptopStand(Boxes):  # Change class name!
    """A simple X shaped frame to support a laptop on a given angle"""

    ui_group = "Misc"  # see ./__init__.py for names

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.argparser.add_argument(
            "--l_depth",
            action="store",
            type=float,
            default=250,
            help="laptop depth - front to back (mm)",
        )
        self.argparser.add_argument(
            "--l_thickness",
            action="store",
            type=float,
            default=10,
            help="laptop thickness (mm)",
        )
        self.argparser.add_argument(
            "--angle",
            action="store",
            type=float,
            default=15,
            help="desired tilt of keyboard (deg)",
        )
        self.argparser.add_argument(
            "--ground_offset",
            action="store",
            type=float,
            default=10,
            help="desired height between bottom of laptop and ground at lowest point (front of laptop stand)",
        )
        self.argparser.add_argument(
            "--nub_size",
            action="store",
            type=float,
            default=10,
            help="desired thickness of the supporting edge",
        )

    def render(self):
        calcs = self.perform_calculations()

        self.laptopstand_triangles(calcs, move="up")

    def perform_calculations(self):
        # a
        angle_rads_a = math.radians(self.angle)

        # h
        height = self.l_depth * math.sin(angle_rads_a)

        # y
        base = sqrt(2) * self.l_depth * math.cos(angle_rads_a)

        # z
        hyp = self.l_depth * sqrt(math.pow(math.cos(angle_rads_a), 2) + 1)

        # b
        angle_rads_b = math.atan(math.tan(angle_rads_a) / math.sqrt(2))

        # g
        base_extra = (
            1
            / math.cos(angle_rads_b)
            * (self.nub_size - self.ground_offset * math.sin(angle_rads_b))
        )

        # x
        lip_outer = (
            self.ground_offset / math.cos(angle_rads_b)
            + self.l_thickness
            - self.nub_size * math.tan(angle_rads_b)
        )

        bottom_slot_depth = (height / 4) + (self.ground_offset / 2)

        top_slot_depth_big = (
            height / 4 + self.ground_offset / 2 + (self.thickness * height) / (2 * base)
        )

        top_slot_depth_small = (
            height / 4 + self.ground_offset / 2 - (self.thickness * height) / (2 * base)
        )

        half_hyp = (hyp * (base - self.thickness)) / (2 * base)

        return dict(
            height=height,
            base=base,
            hyp=hyp,
            angle=math.degrees(angle_rads_b),
            base_extra=base_extra,
            lip_outer=lip_outer,
            bottom_slot_depth=bottom_slot_depth,
            top_slot_depth_small=top_slot_depth_small,
            top_slot_depth_big=top_slot_depth_big,
            half_hyp=half_hyp,
        )

    def laptopstand_triangles(self, calcs, move=None):
        tw = calcs["base"] + self.spacing + 2 * (calcs["base_extra"] + math.sin(math.radians(calcs["angle"]))*(calcs["lip_outer"]+1))
        th = calcs["height"] + 2 * self.ground_offset + self.spacing

        if self.move(tw, th, move, True):
            return
        self.moveTo(calcs["base_extra"]+self.spacing + math.sin(math.radians(calcs["angle"]))*(calcs["lip_outer"]+1))
        self.draw_triangle(calcs, top=False)
        self.moveTo(calcs["base"] - self.spacing,
                    th, 180)
        self.draw_triangle(calcs, top=True)

        self.move(tw, th, move)

    @restore
    def draw_triangle(self, calcs, top):
        # Rear end
        self.moveTo(0, calcs["height"] + self.ground_offset, -90)

        self.edge(calcs["height"] + self.ground_offset)
        self.corner(90)

        foot_length = 10 + self.nub_size

        base_length_without_feet = (
            calcs["base"] - foot_length * 2 - 7 # -7 to account for extra width gained by 45deg angles
        )

        if top:
            # Bottom without slot
            self.polyline(
                foot_length, 45,
                5, -45,
                base_length_without_feet, -45,
                5, 45,
                foot_length + calcs["base_extra"], 0,
            )
        else:
            # Bottom with slot
            self.polyline(
                foot_length, 45,
                5, -45,
                (base_length_without_feet - self.thickness) / 2, 90,
                calcs["bottom_slot_depth"] - 3.5, -90,
                self.thickness, -90,
                calcs["bottom_slot_depth"] - 3.5, 90,
                (base_length_without_feet - self.thickness) / 2, -45,
                5, 45,
                foot_length  + calcs["base_extra"], 0,
            )

        # End nub
        self.corner(90 - calcs["angle"])
        self.edge(calcs["lip_outer"])
        self.corner(90, 1)
        self.edge(self.nub_size - 2)
        self.corner(90, 1)
        self.edge(self.l_thickness)
        self.corner(-90)

        if top:
            # Top with slot
            self.edge(calcs["half_hyp"])
            self.corner(90 + calcs["angle"])
            self.edge(calcs["top_slot_depth_small"])
            self.corner(-90)
            self.edge(self.thickness)
            self.corner(-90)
            self.edge(calcs["top_slot_depth_big"])
            self.corner(90 - calcs["angle"])
            self.edge(calcs["half_hyp"])
        else:
            # Top without slot
            self.edge(calcs["hyp"])

        self.corner(90 + calcs["angle"])
