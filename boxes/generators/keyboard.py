#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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


class Keyboard:
    """
    Code to manage Cherry MX compatible switches and Kailh hotswap socket.
    """

    STANDARD_KEY_SPACING = 19
    SWITCH_CASE_SIZE = 15.6

    def __init__(self):
        pass

    def pcb_holes(self):
        grid_unit = 1.27
        main_hole_size = 4
        pcb_mount_size = 1.7
        led_hole_size = 1
        pin_hole_size = 2.9

        def grid_hole(x, y, d):
            self.hole(grid_unit * x, grid_unit * y, d=d)

        # main hole
        grid_hole(0, 0, main_hole_size)

        # switch pins
        grid_hole(-3, 2, pin_hole_size)
        grid_hole(2, 4, pin_hole_size)

        grid_hole(-4, 0, pcb_mount_size)
        grid_hole(4, 0, pcb_mount_size)

    def apply_callback_on_columns(self, cb, columns_definition, spacing, reverse=False):
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