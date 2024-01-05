# Copyright (C) 2021 Guillaume Collic
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

import argparse
import re

from boxes import boolarg


class Keyboard:
    """
    Code to manage Cherry MX compatible switches and Kailh hotswap socket.

    Reference :
    * https://www.cherrymx.de/en/dev.html
    * https://cdn.sparkfun.com/datasheets/Components/Switches/MX%20Series.pdf
    * https://www.kailhswitch.com/uploads/201815927/PG151101S11.pdf
    """

    STANDARD_KEY_SPACING = 19.05
    SWITCH_CASE_SIZE = 15.6
    FRAME_CUTOUT = 14

    def __init__(self) -> None:
        pass

    def add_common_keyboard_parameters(
        self,
        add_hotswap_parameter=True,
        add_pcb_mount_parameter=True,
        add_led_parameter=True,
        add_diode_parameter=True,
        add_cutout_type_parameter=True,
        default_columns_definition=None,
    ):
        if add_hotswap_parameter:
            self.argparser.add_argument(
                "--hotswap_enable",
                action="store",
                type=boolarg,
                default=True,
                help=("enlarge switches holes for hotswap pcb sockets"),
            )
        if add_pcb_mount_parameter:
            self.argparser.add_argument(
                "--pcb_mount_enable",
                action="store",
                type=boolarg,
                default=True,
                help=("adds holes for pcb mount switches"),
            )
        if add_led_parameter:
            self.argparser.add_argument(
                "--led_enable",
                action="store",
                type=boolarg,
                default=False,
                help=("adds pin holes under switches for leds"),
            )
        if add_diode_parameter:
            self.argparser.add_argument(
                "--diode_enable",
                action="store",
                type=boolarg,
                default=False,
                help=("adds pin holes under switches for diodes"),
            )
        if add_cutout_type_parameter:
            self.argparser.add_argument(
                "--cutout_type",
                action="store",
                type=str,
                default="castle",
                help=(
                    "Shape of the plate cutout: 'castle' allows for modding, and 'simple' is a tighter and simpler square"
                ),
            )
        if default_columns_definition:
            self.argparser.add_argument(
            "--columns_definition",
                type=self.argparseColumnsDefinition,
                default=default_columns_definition,
                help=(
                    "Each column is separated by '/', and is in the form 'nb_rows @ offset x repeat_count'. "
                    "Nb_rows is the number of rows for this column. "
                    "The offset is in mm and optional. "
                    "Repeat_count is optional and repeats this column multiple times. "
                    "Spaces are not important."
                    "For example '3x2 / 4@11' means we want 3 columns, the two first with "
                    "3 rows without offset, and the last with 4 rows starting at 11mm high."
                ),
            )

    def argparseColumnsDefinition(self, s):
        """
        Parse columns definition parameter

        :param s: string to parse

        Each column is separated by '/', and is in the form 'nb_rows @ offset x repeat_count'.
        Nb_rows is the number of rows for this column.
        The offset is in mm and optional.
        Repeat_count is optional and repeats this column multiple times.
        Spaces are not important.
        For example '3x2 / 4@11' means we want 3 columns, the two first with
        3 rows without offset, and the last with 4 rows starting at 11mm high
        """
        result = []
        try:
            for column_string in s.split("/"):
                m = re.match(r"^\s*(\d+)\s*@?\s*(\d*\.?\d*)(?:\s*x\s*(\d+))?\s*$", column_string)
                keys_count = int(m.group(1))
                offset = float(m.group(2)) if m.group(2) else 0
                n = int(m.group(3)) if m.group(3) else 1
                result.extend([(offset, keys_count)]*n)
        except:
            raise argparse.ArgumentTypeError("Don't understand columns definition string")

        return result

    def pcb_holes(
        self, with_hotswap=True, with_pcb_mount=True, with_led=False, with_diode=False
    ):
        grid_unit = 1.27
        main_hole_size = 4
        pcb_mount_size = 1.7
        led_hole_size = 1
        if with_hotswap:
            pin_hole_size = 2.9
        else:
            pin_hole_size = 1.5

        def grid_hole(x, y, d):
            self.hole(grid_unit * x, grid_unit * y, d=d)

        # main hole
        grid_hole(0, 0, main_hole_size)

        # switch pins
        grid_hole(-3, 2, pin_hole_size)
        grid_hole(2, 4, pin_hole_size)

        if with_pcb_mount:
            grid_hole(-4, 0, pcb_mount_size)
            grid_hole(4, 0, pcb_mount_size)

        if with_led:
            grid_hole(-1, -4, led_hole_size)
            grid_hole(1, -4, led_hole_size)

        if with_diode:
            grid_hole(-3, -4, led_hole_size)
            grid_hole(3, -4, led_hole_size)

    def apply_callback_on_columns(self, cb, columns_definition, spacing=None, reverse=False):
        if spacing is None:
            spacing = self.STANDARD_KEY_SPACING
        if reverse:
            columns_definition = list(reversed(columns_definition))

        for offset, nb_keys in columns_definition:
            self.moveTo(0, offset)
            for _ in range(nb_keys):
                cb()
                self.moveTo(0, spacing)
            self.moveTo(spacing, -nb_keys * spacing)
            self.moveTo(0, -offset)

        total_width = len(columns_definition) * spacing
        self.moveTo(-1 * total_width)

    def outer_hole(self, radius=2, centered=True):
        """
        Draws a rounded square big enough to go around a whole switch (15.6mm)
        """
        half_size = Keyboard.SWITCH_CASE_SIZE / 2
        if centered:
            self.moveTo(-half_size, -half_size)

        # draw clock wise to work with burn correction
        straight_edge = Keyboard.SWITCH_CASE_SIZE - 2 * radius
        polyline = [straight_edge, (-90, radius)] * 4
        self.moveTo(self.burn, radius, 90)
        self.polyline(*polyline)
        self.moveTo(0, 0, 270)
        self.moveTo(0, -radius)
        self.moveTo(-self.burn)

        if centered:
            self.moveTo(half_size, half_size)

    def castle_shaped_plate_cutout(self, centered=True):
        """
        This cutout shaped like a castle enables switch modding and rotation.
        More information (type 4) on https://geekhack.org/index.php?topic=59837.0
        """
        half_size = Keyboard.SWITCH_CASE_SIZE / 2
        if centered:
            self.moveTo(-half_size, -half_size)

        # draw clock wise to work with burn correction
        btn_half_side = [0.98, 90, 0.81, -90, 3.5, -90, 0.81, 90, 2.505]
        btn_full_side = [*btn_half_side, 0, *btn_half_side[::-1]]
        btn = [*btn_full_side, -90] * 4

        self.moveTo(self.burn+0.81, 0.81, 90)
        self.polyline(*btn)
        self.moveTo(0, 0, 270)
        self.moveTo(-self.burn-0.81, -0.81)

        if centered:
            self.moveTo(half_size, half_size)

    def configured_plate_cutout(self, support=False):
        """
        Choose which cutout to use based on configured type.

        support: if true, not the main cutout, but one to glue against the first
        1.5mm cutout to strengthen it, without the clipping part.
        """
        if self.cutout_type.lower() == "castle":
            if support:
                self.outer_hole()
            else:
                self.castle_shaped_plate_cutout()
        else:
            self.simple_plate_cutout(with_notch=support)

    def simple_plate_cutout(self, radius=0.2, with_notch=False):
        """
        A simple plate cutout, a 14mm rectangle, as specified in this reference sheet
        https://cdn.sparkfun.com/datasheets/Components/Switches/MX%20Series.pdf

        With_notch should be used for a secondary lower plate, strengthening the first one.
        A notch is added to let the hooks grasp the main upper plate.

        Current position should be switch center.

        Radius should be lower or equal to 0.3 mm
        """
        size = Keyboard.FRAME_CUTOUT
        half_size = size / 2

        if with_notch:
            notch_length = 5
            notch_depth = 1
            straight_part = 0.5 * (size - 2 * radius - 2 * notch_depth - notch_length)

            self.moveTo(-half_size + self.burn, 0, 90)
            polyline_quarter = [
                half_size - radius,
                (-90, radius),
                straight_part,
                (90, notch_depth / 2),
                0,
                (-90, notch_depth / 2),
                notch_length / 2,
            ]
            polyline = (
                polyline_quarter
                + [0]
                + list(reversed(polyline_quarter))
                + [0]
                + polyline_quarter
                + [0]
                + list(reversed(polyline_quarter))
            )
            self.polyline(*polyline)
            self.moveTo(0, 0, -90)
            self.moveTo(half_size - self.burn)
        else:
            self.rectangularHole(0, 0, size, size, r=radius)