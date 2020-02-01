#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

from boxes import Boxes, edges, boolarg
import math


class DividerTray(Boxes):
    """Divider tray - rows and dividers"""

    ui_group = "Tray"

    def __init__(self):
        Boxes.__init__(self)
        self.buildArgParser("sx", "sy", "h", "outside")
        self.argparser.add_argument(
            "--slot_depth", type=float, default=20, help="depth of the slot in mm"
        )
        self.argparser.add_argument(
            "--slot_angle",
            type=float,
            default=0,
            help="angle at which slots are generated, in degrees. 0° is vertical.",
        )
        self.argparser.add_argument(
            "--slot_radius",
            type=float,
            default=2,
            help="radius of the slot entrance in mm",
        )
        self.argparser.add_argument(
            "--slot_extra_slack",
            type=float,
            default=0.2,
            help="extra slack (in addition to thickness and kerf) for slot width to help insert dividers",
        )
        self.argparser.add_argument(
            "--divider_bottom_margin",
            type=float,
            default=0,
            help="margin between box's bottom and divider's",
        )
        self.argparser.add_argument(
            "--divider_upper_notch_radius",
            type=float,
            default=1,
            help="divider's notch's upper radius",
        )
        self.argparser.add_argument(
            "--divider_lower_notch_radius",
            type=float,
            default=8,
            help="divider's notch's lower radius",
        )
        self.argparser.add_argument(
            "--divider_notch_depth",
            type=float,
            default=15,
            help="divider's notch's depth",
        )
        self.argparser.add_argument(
            "--left_wall",
            type=boolarg,
            default=True,
            help="generate wall on the left side",
        )
        self.argparser.add_argument(
            "--right_wall",
            type=boolarg,
            default=True,
            help="generate wall on the right side",
        )

    def render(self):

        side_walls_number = len(self.sx) - 1 + sum([self.left_wall, self.right_wall])
        if side_walls_number == 0:
            raise ValueError("You need at least one side wall to generate this tray")

        slot_descriptions = self.generate_slot_descriptions(self.sy)

        if self.outside:
            self.sx = self.adjustSize(self.sx, self.left_wall, self.right_wall)
            side_wall_target_length = sum(self.sy) - 2 * self.thickness
            slot_descriptions.adjust_to_target_length(side_wall_target_length)
        else:
            # If the parameter 'h' is the inner height of the content itself,
            # then the actual tray height needs to be adjusted with the angle
            self.h = self.h * math.cos(math.radians(self.slot_angle))

        self.ctx.save()

        # Facing walls (outer) with finger holes to support side walls
        facing_wall_length = sum(self.sx) + self.thickness * (len(self.sx) - 1)
        side_edge = lambda with_wall: "F" if with_wall else "e"
        for _ in range(2):
            self.rectangularWall(
                facing_wall_length,
                self.h,
                ["e", side_edge(self.right_wall), "e", side_edge(self.left_wall)],
                callback=[self.generate_finger_holes],
                move="up",
            )

        # Side walls (outer & inner) with slots to support dividers
        side_wall_length = slot_descriptions.total_length()
        for _ in range(side_walls_number):
            se = DividerSlotsEdge(self, slot_descriptions.descriptions)
            self.rectangularWall(
                side_wall_length, self.h, ["e", "f", se, "f"], move="up"
            )

        # Switch to right side of the file
        self.ctx.restore()
        self.rectangularWall(
            max(facing_wall_length, side_wall_length), self.h, "ffff", move="right only"
        )

        # Dividers
        divider_height = (
            # h, with angle adjustement
            self.h / math.cos(math.radians(self.slot_angle))
            # removing what exceeds in the width of the divider
            - self.thickness * math.tan(math.radians(self.slot_angle))
            # with margin
            - self.divider_bottom_margin
        )
        for i, length in enumerate(self.sx):
            is_first_wall = i == 0
            is_last_wall = i == len(self.sx) - 1
            self.generate_divider(
                length,
                divider_height,
                "up",
                only_one_wall=(is_first_wall and not self.left_wall)
                or (is_last_wall and not self.right_wall),
            )

        if self.debug:
            debug_info = ["Debug"]
            debug_info.append(
                "Slot_edge_outer_length:{0:.2f}".format(
                    slot_descriptions.total_length() + 2 * self.thickness
                )
            )
            debug_info.append(
                "Slot_edge_inner_lengths:{0}".format(
                    str.join(
                        "|",
                        [
                            "{0:.2f}".format(e.usefull_length())
                            for e in slot_descriptions.get_straigth_edges()
                        ],
                    )
                )
            )
            debug_info.append(
                "Face_edge_outer_length:{0:.2f}".format(
                    facing_wall_length
                    + self.thickness * sum([self.left_wall, self.right_wall])
                )
            )
            debug_info.append(
                "Face_edge_inner_lengths:{0}".format(
                    str.join("|", ["{0:.2f}".format(e) for e in self.sx])
                )
            )
            debug_info.append("Tray_height:{0:.2f}".format(self.h))
            debug_info.append(
                "Content_height:{0:.2f}".format(
                    self.h / math.cos(math.radians(self.slot_angle))
                )
            )
            self.text(str.join("\n", debug_info), x=5, y=5, align="bottom left")

    def generate_slot_descriptions(self, sections):
        slot_width = self.thickness + self.slot_extra_slack

        descriptions = SlottedEdgeDescriptions()

        # Special case: if first slot start at 0, then radius is 0
        first_correction = 0
        current_section = 0
        if sections[0] == 0:
            slot = SlotDescription(
                slot_width,
                depth=self.slot_depth,
                angle=self.slot_angle,
                start_radius=0,
                end_radius=self.slot_radius,
            )
            descriptions.add(slot)
            first_correction = slot.round_edge_end_correction()
            current_section += 1

        first_length = sections[current_section]
        current_section += 1
        descriptions.add(
            StraightEdgeDescription(
                first_length, round_edge_compensation=first_correction
            )
        )

        for l in sections[current_section:]:
            slot = SlotDescription(
                slot_width,
                depth=self.slot_depth,
                angle=self.slot_angle,
                radius=self.slot_radius,
            )

            # Fix previous edge length
            previous_edge = descriptions.get_last_edge()
            previous_edge.round_edge_compensation += slot.round_edge_start_correction()

            # Add this slot
            descriptions.add(slot)

            # Add the straigth edge after this slot
            descriptions.add(
                StraightEdgeDescription(l, slot.round_edge_end_correction())
            )

        # We need to add extra space for the divider (or the actual content)
        # to slide all the way down to the bottom of the tray in spite of walls
        end_length = self.h * math.tan(math.radians(self.slot_angle))
        descriptions.get_last_edge().angle_compensation += end_length

        return descriptions

    def generate_finger_holes(self):
        posx = -0.5 * self.thickness
        for x in self.sx[:-1]:
            posx += x + self.thickness
            self.fingerHolesAt(posx, 0, self.h)

    def generate_divider(self, width, height, move, only_one_wall=False):
        second_tab_width = 0 if only_one_wall else self.thickness
        total_width = width + self.thickness + second_tab_width

        if self.move(total_width, height, move, True):
            return

        # Upper edge with a finger notch

        upper_radius = self.divider_upper_notch_radius
        lower_radius = self.divider_lower_notch_radius
        upper_third = (width - 2 * upper_radius - 2 * lower_radius) / 3

        # Upper: first tab width
        self.edge(self.thickness)

        # Upper: divider width (with notch if possible)
        if upper_third > 0:
            self.edge(upper_third)
            self.corner(90, upper_radius)
            self.edge(self.divider_notch_depth - upper_radius - lower_radius)
            self.corner(-90, lower_radius)
            self.edge(upper_third)
            self.corner(-90, lower_radius)
            self.edge(self.divider_notch_depth - upper_radius - lower_radius)
            self.corner(90, upper_radius)
            self.edge(upper_third)
        else:
            # if there isn't enough room for the radius, we don't use it
            self.edge(width)

        # Upper: second tab width if needed
        self.edge(second_tab_width)

        # First side, with tab depth only if there is 2 walls
        self.corner(90)
        self.edge(self.slot_depth)
        self.corner(90)
        self.edge(second_tab_width)
        self.corner(-90)
        self.edge(height - self.slot_depth)

        # Lower edge
        self.corner(90)
        self.edge(width)

        # Second side, always a tab
        self.corner(90)
        self.edge(height - self.slot_depth)
        self.corner(-90)
        self.edge(self.thickness)
        self.corner(90)
        self.edge(self.slot_depth)

        # Move for next piece
        self.move(total_width, height, move)


class SlottedEdgeDescriptions:
    def __init__(self):
        self.descriptions = []

    def add(self, description):
        self.descriptions.append(description)

    def get_straigth_edges(self):
        return [x for x in self.descriptions if isinstance(x, StraightEdgeDescription)]

    def get_last_edge(self):
        return self.descriptions[-1]

    def adjust_to_target_length(self, target_length):
        actual_length = sum([d.tracing_length() for d in self.descriptions])
        compensation = actual_length - target_length

        compensation_ratio = compensation / sum(
            [d.asked_length for d in self.get_straigth_edges()]
        )

        for edge in self.get_straigth_edges():
            edge.outside_ratio = 1 - compensation_ratio

    def total_length(self):
        return sum([x.tracing_length() for x in self.descriptions])


class StraightEdgeDescription:
    def __init__(
        self,
        asked_length,
        round_edge_compensation=0,
        outside_ratio=1,
        angle_compensation=0,
    ):
        self.asked_length = asked_length
        self.round_edge_compensation = round_edge_compensation
        self.outside_ratio = outside_ratio
        self.angle_compensation = angle_compensation

    def __repr__(self):
        return (
            "StraightEdgeDescription({0}, round_edge_compensation={1}, angle_compensation={2}, outside_ratio={3})"
        ).format(
            self.asked_length,
            self.round_edge_compensation,
            self.angle_compensation,
            self.outside_ratio,
        )

    def tracing_length(self):
        """
        How much length should take tracing this straight edge
        """
        return (
            (self.asked_length * self.outside_ratio)
            - self.round_edge_compensation
            + self.angle_compensation
        )

    def usefull_length(self):
        """
        Part of the length which might be used by the content of the tray
        """
        return self.asked_length * self.outside_ratio


class Memoizer(dict):
    def __init__(self, computation):
        self.computation = computation

    def __missing__(self, key):
        res = self[key] = self.computation(key)
        return res


class SlotDescription:
    _div_by_cos_cache = Memoizer(lambda a: 1 / math.cos(math.radians(a)))
    _tan_cache = Memoizer(lambda a: math.tan(math.radians(a)))

    def __init__(
        self, width, depth=20, angle=0, radius=0, start_radius=None, end_radius=None
    ):
        self.depth = depth
        self.width = width
        self.start_radius = radius if start_radius == None else start_radius
        self.end_radius = radius if end_radius == None else end_radius
        self.angle = angle

    def __repr__(self):
        return "SlotDescription({0}, depth={1}, angle={2}, start_radius={3}, end_radius={4})".format(
            self.width, self.depth, self.angle, self.start_radius, self.end_radius
        )

    def _div_by_cos(self):
        return SlotDescription._div_by_cos_cache[self.angle]

    def _tan(self):
        return SlotDescription._tan_cache[self.angle]

    def angle_corrected_width(self):
        """
        returns how much width is the slot when measured horizontally, since the angle makes it bigger.
        It's the same as the slot entrance width when radius is 0°.
        """
        return self.width * self._div_by_cos()

    def round_edge_start_correction(self):
        """
        returns by how much we need to stop tracing our straight lines at the start of the slot
        in order to do a curve line instead
        """
        return self.start_radius * (self._div_by_cos() - self._tan())

    def round_edge_end_correction(self):
        """
        returns by how much we need to stop tracing our straight lines at the end of the slot
        in order to do a curve line instead
        """
        return self.end_radius * (self._div_by_cos() + self._tan())

    def _depth_angle_correction(self):
        """
        The angle makes one side of the slot deeper than the other.
        """
        extra_depth = self.width * self._tan()
        return extra_depth

    def corrected_start_depth(self):
        """
        Returns the depth of the straigth part of the slot starting side
        """
        extra_depth = self._depth_angle_correction()
        return self.depth + max(0, extra_depth) - self.round_edge_start_correction()

    def corrected_end_depth(self):
        """
        Returns the depth of the straigth part of the slot ending side
        """
        extra_depth = self._depth_angle_correction()
        return self.depth + max(0, -extra_depth) - self.round_edge_end_correction()

    def tracing_length(self):
        """
        How much length this slot takes on an edge
        """
        return (
            self.round_edge_start_correction()
            + self.angle_corrected_width()
            + self.round_edge_end_correction()
        )


class DividerSlotsEdge(edges.BaseEdge):
    """Edge with multiple angled rounded slots for dividers"""

    description = "Edge with multiple angled rounded slots for dividers"

    def __init__(self, boxes, descriptions):

        super(DividerSlotsEdge, self).__init__(boxes, None)

        self.descriptions = descriptions

    def __call__(self, length, **kw):

        self.ctx.save()

        for description in self.descriptions:
            if isinstance(description, SlotDescription):
                self.do_slot(description)
            elif isinstance(description, StraightEdgeDescription):
                self.do_straight_edge(description)

        # rounding errors might accumulates :
        # restore context and redo the move straight
        self.ctx.restore()
        self.moveTo(length)

    def do_straight_edge(self, straight_edge):
        self.edge(straight_edge.tracing_length())

    def do_slot(self, slot):
        self.ctx.save()

        self.corner(90 - slot.angle, slot.start_radius)
        self.edge(slot.corrected_start_depth())
        self.corner(-90)
        self.edge(slot.width)
        self.corner(-90)
        self.edge(slot.corrected_end_depth())
        self.corner(90 + slot.angle, slot.end_radius)

        # rounding errors might accumulates :
        # restore context and redo the move straight
        self.ctx.restore()
        self.moveTo(slot.tracing_length())
