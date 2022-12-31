#!/usr/bin/env python3
# Copyright (C) 2020 Guillaume Collic
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

import math
from functools import partial

from boxes import Boxes, edges
from .dividertray import (
    SlotDescriptionsGenerator,
    DividerSlotsEdge,
)


class AgricolaInsert(Boxes):
    """
    Agricola Revised Edition game box insert, including some expansions.
    """

    ui_group = "Misc"

    description = """
This insert was designed with 3 mm plywood in mind, and should work fine with
materials around this thickness.

This is an insert for the [Agricola Revised Edition](https://boardgamegeek.com/boardgame/200680/agricola-revised-edition)
board game. It is specifically designed around the [Farmers Of The Moor expansion](https://boardgamegeek.com/boardgameexpansion/257344/agricola-farmers-moor),
and should also store the [5-6 players expansion](https://boardgamegeek.com/boardgameexpansion/210625/agricola-expansion-5-and-6-players)
(not tested, but I tried to take everything into account for it, please inform
us if you tested it).

It can be stored inside the original game box, including the 2 expansions,
with the lid slightly raised.

The parts of a given element are mostly generated next to each other vertically.
It should be straightforward to match them.

Here are the different elements, from left to right in the generated file.

#### Card tray

The cards are all kept in a tray, with paper dividers to sort them easily. When
the tray is not full of cards, wood dividers slides in slots in order to keep
the cards from falling into the empty space.

There should be enough space for the main game, Farmers Of The Moor, and the 5-6
player expansion, but not much more than that.

To keep a lower profile, the cards are at a slight angle, and the paper dividers
tabs are horizontal instead of vertical.
A small wall keeps the card against one side while the tabs protrude on the
other side, above the small wall.

The wall with the big hole is the sloped one. It goes between the two
"comb-like" walls first, with its two small holes at the bottom. Then there is a
low-height long wall with a sloped edge which should go from the sloped wall to
the other side. You can finish the tray with the last wall at the end.

#### Upper level trays

4 trays with movable walls are used to store resources. They were designed to
store them in this order:

* Stone / Vegetable / Pig / Cow
* Reed / Grain / Sheep
* Wood / Clay
* Food / Fire

The wall would probably be better if fixed instead of movable, but I would like
to test with the 5-6 player expansion to be sure their positions are correct
with it too.

The little feet of the movable wall should be glued. The triangles are put
horizontally, with their bases towards the sides.

#### Lower level tray

The lower level tray is used to store the horses.

#### Room/Field tiles

Two boxes are generated to store the room/field tiles. One for the wood/field,
the other for the clay/stone. They are stored with the main opening upside, but
I prefer to use them during play with this face on the side.

#### Moor/Forest and miscellaneous tiles

A box is generated to store the Moor/Forest tiles, and some other tiles such as
the "multiple resources" cardboard tokens.

The Moor/Forest tiles are at the same height as the Room/Field, and the upper
level trays are directly on them. The horse box and player box are slightly
lower. This Moor/Forest box have a lowered corner (the one for the miscellaneous
tiles). Two cardboard pieces can be stored between the smaller boxes and the
upper level trays (as seen on the picture).

Be sure to match the pieces so that the walls with smaller heights are next to
each other.

#### Players bit boxes

Each player has its own box where the bits of his color are stored.
The cardboard bed from Farmers Of The Moor is central to this box.

* The fences are stored inside the bed
* The bed is placed in the box, with holes to keep it there (and to take less
  height)
* The stables are stored in the two corners
* The five farmers are stored between the bed and the three walls, alternatively
  head up and head down.

During assembly, the small bars are put in the middle holes. The two bigger
holes at the ends are used for the bed feet. The bar keeps the bed from
protruding underneath.

"""

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=1.0)

    def render(self):
        player_box_height = 34.5
        player_box_inner_width = 50.5
        bigger_box_inner_height = 36.7
        row_width = 37.2
        tray_inner_height = 17
        box_width = 218
        card_tray_height = (
            self.thickness * 2 + tray_inner_height + bigger_box_inner_height
        )
        card_tray_width = (
            305.35 - player_box_inner_width * 2 - row_width * 2 - 9 * self.thickness
        )

        self.render_card_divider_tray(card_tray_height, box_width, card_tray_width)
        self.render_upper_token_trays(tray_inner_height, box_width)
        wood_room_box_width = 39.8
        self.render_room_box(wood_room_box_width, bigger_box_inner_height, row_width)
        stone_room_box_width = 26.7
        self.render_room_box(stone_room_box_width, bigger_box_inner_height, row_width)
        moor_box_length = 84.6
        self.render_moor_box(
            bigger_box_inner_height, player_box_height, row_width, moor_box_length
        )
        horse_box_margin = 0.5
        horse_box_length = (
            box_width
            - wood_room_box_width
            - stone_room_box_width
            - moor_box_length
            - 6 * self.thickness
            - horse_box_margin
        )
        self.render_horse_box(player_box_height, row_width, horse_box_length)
        for _ in range(6):
            self.render_player_box(player_box_height, player_box_inner_width)

    def render_card_divider_tray(
        self, card_tray_height, card_tray_length, card_tray_width
    ):
        """
        The whole tray which contains the cards, including its dividers.
        Cards are at an angle, to save height.
        """
        self.ctx.save()

        tray_inner_length = card_tray_length - self.thickness
        margin_for_score_sheet = 0  # 3 if you want more space for score sheet
        sleeved_cards_width = 62 + margin_for_score_sheet

        rad = math.acos(card_tray_height / sleeved_cards_width)
        angle = math.degrees(rad)
        cos = math.cos(rad)
        tan = math.tan(rad)
        sin = math.sin(rad)

        slots_number = 19
        slot_depth = 30
        slot_descriptions = SlotDescriptionsGenerator().generate_all_same_angles(
            [tray_inner_length / slots_number for _ in range(slots_number)],
            self.thickness,
            0.2,
            slot_depth,
            card_tray_height,
            angle,
        )
        slot_descriptions.adjust_to_target_length(tray_inner_length)

        sloped_wall_height = sleeved_cards_width - self.thickness * (tan + 1 / tan)
        sloped_wall_posx_at_y0 = (
            tray_inner_length - sloped_wall_height * tan - cos * self.thickness
        )
        sloped_wall_posx = sloped_wall_posx_at_y0 + cos * self.thickness / 2
        sloped_wall_posy = sin * self.thickness / 2

        dse = DividerSlotsEdge(self, slot_descriptions.descriptions)
        for _ in range(2):
            self.rectangularWall(
                tray_inner_length,
                card_tray_height,
                ["e", "e", dse, "f"],
                move="up",
                callback=[
                    partial(
                        lambda: self.fingerHolesAt(
                            sloped_wall_posx,
                            sloped_wall_posy,
                            sloped_wall_height,
                            angle=90 - angle,
                        )
                    )
                ],
            )

        # generate spacer
        spacer_height = card_tray_height / 2
        spacer_spacing = card_tray_width-99.8
        spacer_upper_width = sloped_wall_posx_at_y0 + spacer_height * tan
        self.trapezoidWall(
            spacer_height,
            spacer_upper_width,
            sloped_wall_posx_at_y0,
            "fefe",
            move="up rotated",
        )

        self.rectangularWall(
            card_tray_width,
            card_tray_height,
            "eFeF",
            move="up",
            callback=[
                partial(
                    lambda: self.fingerHolesAt(
                        spacer_spacing - self.thickness / 2, 0, spacer_height
                    )
                )
            ],
        )
        self.rectangularWall(
            card_tray_width,
            sloped_wall_height,
            "efef",
            move="up",
            callback=[
                partial(
                    self.generate_card_tray_sloped_wall_holes,
                    card_tray_width,
                    sloped_wall_height,
                    spacer_height,
                    spacer_spacing,
                    rad,
                )
            ],
        )

        self.ctx.restore()
        self.rectangularWall(card_tray_length, 0, "FFFF", move="right only")
        self.ctx.save()

        divider_height = sleeved_cards_width - self.thickness * tan
        self.generate_divider(
            card_tray_width, divider_height, slot_depth, spacer_spacing, "up"
        )
        self.explain(
            [
                "Wood divider",
                "Hard separation to keep the card",
                "from slipping in empty space left.",
                "Takes more space, but won't move.",
                "Duplicate as much as you want",
                "(I use 2).",
            ]
        )

        self.ctx.restore()
        self.rectangularWall(card_tray_width, 0, "ffff", move="right only")
        self.ctx.save()

        self.generate_paper_divider(
            card_tray_width, sleeved_cards_width, slot_depth, spacer_spacing, "up"
        )
        self.explain(
            [
                "Paper divider",
                "Soft separation to search easily",
                "the card group you need",
                "(by expansion, number of player,",
                "etc.).",
                "Duplicate as much as you want",
                "(I use 7).",
            ]
        )
        self.ctx.restore()
        self.rectangularWall(card_tray_width, 0, "ffff", move="right only")

    def explain(self, strings):
        self.text(
            str.join(
                "\n",
                strings,
            ),
            fontsize=7,
            align="bottom left",
        )

    def generate_sloped_wall_holes(self, side_wall_length, rad, sloped_wall_height):
        cos = math.cos(rad)
        tan = math.tan(rad)
        sin = math.sin(rad)
        posx_at_y0 = side_wall_length - sloped_wall_height * tan
        posx = posx_at_y0 - cos * self.thickness / 2
        posy = sin * self.thickness / 2
        self.fingerHolesAt(posx, posy, sloped_wall_height, angle=90 - math.degrees(rad))

    def generate_card_tray_sloped_wall_holes(
        self, side_wall_length, sloped_wall_height, spacer_height, spacer_spacing, rad
    ):
        # Spacer finger holes
        self.fingerHolesAt(
            side_wall_length - (spacer_spacing - self.thickness / 2),
            # the sloped wall doesn't exactly touch the bottom of the spacer
            -self.thickness * math.tan(rad),
            spacer_height / math.cos(rad),
        )

        # Big hole to access "lost" space behind sloped wall
        radius = 5
        padding = 8
        total_loss = 2 * radius + 2 * padding
        self.moveTo(radius + padding, padding)
        self.polyline(
            side_wall_length - total_loss,
            (90, radius),
            sloped_wall_height - total_loss,
            (90, radius),
            side_wall_length - total_loss,
            (90, radius),
            sloped_wall_height - total_loss,
            (90, radius),
        )

    def generate_paper_divider(self, width, height, slot_depth, spacer_spacing, move):
        """
        A card separation made of paper, which moves freely in the card tray.
        Takes less space and easy to manipulate, but won't block cards in place.
        """
        if self.move(width, height, move, True):
            return

        margin = 0.5
        actual_width = width - margin
        self.polyline(
            actual_width - spacer_spacing,
            90,
            height - slot_depth,
            -90,
            spacer_spacing,
            90,
            slot_depth,
            90,
            actual_width,
            90,
            height,
            90,
        )

        # Move for next piece
        self.move(width, height, move)

    def generate_divider(self, width, height, slot_depth, spacer_spacing, move):
        """
        A card separation made of wood which slides in the side slots.
        Can be useful to do hard separations, but takes more space and
        less movable than the paper ones.
        """
        total_width = width + 2 * self.thickness

        if self.move(total_width, height, move, True):
            return

        radius = 16
        padding = 20
        divider_notch_depth = 35

        self.polyline(
            self.thickness + spacer_spacing + padding - radius,
            (90, radius),
            divider_notch_depth - radius - radius,
            (-90, radius),
            width - 2 * radius - 2 * padding - spacer_spacing,
            (-90, radius),
            divider_notch_depth - radius - radius,
            (90, radius),
            self.thickness + padding - radius,
            90,
            slot_depth,
            90,
            self.thickness,
            -90,
            height - slot_depth,
            90,
            width - spacer_spacing,
            90,
            height - slot_depth,
            -90,
            self.thickness + spacer_spacing,
            90,
            slot_depth,
        )

        # Move for next piece
        self.move(total_width, height, move)

    def render_horse_box(self, player_box_height, row_width, width):
        """
        Box for the horses on lower level. Same height as player boxes.
        """
        length = 2 * row_width + 3 * self.thickness
        self.render_simple_tray(width, length, player_box_height)

    def render_moor_box(
        self, bigger_box_inner_height, player_box_height, row_width, length
    ):
        """
        Box for the moor/forest tiles, and the cardboard tokens with multiple
        units of resources.
        A corner is lowered (the one for the tokens) at the same height as player boxes
        to store 2 levels of small boards there.
        """
        self.ctx.save()
        height = bigger_box_inner_height
        lowered_height = player_box_height - self.thickness
        lowered_corner_height = height - lowered_height
        corner_length = 53.5

        self.rectangularWall(
            length,
            2 * row_width + self.thickness,
            "FfFf",
            move="up",
            callback=[
                partial(
                    lambda: self.fingerHolesAt(
                        0, row_width + 0.5 * self.thickness, length, 0
                    )
                )
            ],
        )

        for i in range(2):
            self.rectangularWall(
                length,
                lowered_height,
                [
                    "f",
                    "f",
                    MoorBoxSideEdge(
                        self, corner_length, lowered_corner_height, i % 2 == 0
                    ),
                    "f",
                ],
                move="up",
            )
        self.rectangularWall(length, height / 2, "ffef", move="up")

        for i in range(2):
            self.rectangularWall(
                2 * row_width + self.thickness,
                lowered_height,
                [
                    "F",
                    "F",
                    MoorBoxHoleEdge(self, height, lowered_corner_height, i % 2 == 0),
                    "F",
                ],
                move="up",
                callback=[
                    partial(self.generate_side_finger_holes, row_width, height / 2)
                ],
            )

        self.ctx.restore()
        self.rectangularWall(length, 0, "FFFF", move="right only")

    def generate_side_finger_holes(self, row_width, height):
        self.fingerHolesAt(row_width + 0.5 * self.thickness, 0, height)

    def render_room_box(self, width, height, row_width):
        """
        A box in which storing room/field tiles.
        """
        border_height = 12
        room_box_length = row_width * 2 + self.thickness

        self.ctx.save()

        self.rectangularWall(
            room_box_length,
            height,
            "eFfF",
            move="up",
            callback=[partial(self.generate_side_finger_holes, row_width, height)],
        )

        self.rectangularWall(
            room_box_length,
            width,
            "FFfF",
            move="up",
            callback=[partial(self.generate_side_finger_holes, row_width, width)],
        )

        self.rectangularWall(
            room_box_length,
            border_height,
            "FFeF",
            move="up",
            callback=[
                partial(self.generate_side_finger_holes, row_width, border_height)
            ],
        )

        for _ in range(3):
            self.trapezoidWall(width, height, border_height, "ffef", move="up")

        self.ctx.restore()

        self.rectangularWall(room_box_length, 0, "FFFF", move="right only")

    def render_player_box(self, player_box_height, player_box_inner_width):
        """
        A box in which storing all the bits of a single player,
        including (and designed for) the cardboard bed from Farmers Of The Moor.
        """
        self.ctx.save()
        bed_inner_height = player_box_height - self.thickness
        bed_inner_length = 66.75
        bed_inner_width = player_box_inner_width
        cardboard_bed_foot_height = 6.5
        cardboard_bed_hole_margin = 5
        cardboard_bed_hole_length = 12
        bed_head_length = 20
        bed_foot_height = 18
        support_length = 38

        bed_edge = Bed2SidesEdge(
            self, bed_inner_length, bed_head_length, bed_foot_height
        )
        noop_edge = NoopEdge(self)
        self.ctx.save()
        optim_180_x = (
            bed_inner_length + self.thickness + bed_head_length + 2 * self.spacing
        )
        optim_180_y = 2 * bed_foot_height - player_box_height + 2 * self.spacing
        for _ in range(2):
            self.rectangularWall(
                bed_inner_length,
                bed_inner_height,
                ["F", bed_edge, noop_edge, "F"],
                move="up",
            )
            self.moveTo(optim_180_x, optim_180_y, -180)
        self.ctx.restore()
        self.moveTo(0, bed_inner_height + self.thickness + self.spacing + optim_180_y)

        self.rectangularWall(
            bed_inner_length,
            bed_inner_width,
            "feff",
            move="up",
            callback=[
                partial(
                    self.generate_bed_holes,
                    bed_inner_width,
                    cardboard_bed_hole_margin,
                    cardboard_bed_hole_length,
                    support_length,
                )
            ],
        )

        self.ctx.save()
        self.rectangularWall(
            bed_inner_width,
            bed_inner_height,
            ["F", "f", BedHeadEdge(self, bed_inner_height - 15), "f"],
            move="right",
        )
        for _ in range(2):
            self.rectangularWall(
                cardboard_bed_foot_height - self.thickness,
                support_length,
                "efee",
                move="right",
            )
        self.ctx.restore()
        self.rectangularWall(
            bed_inner_width,
            bed_inner_height,
            "Ffef",
            move="up only",
        )

        self.ctx.restore()
        self.rectangularWall(
            bed_inner_length + bed_head_length + self.spacing - self.thickness,
            0,
            "FFFF",
            move="right only",
        )

    def generate_bed_holes(self, width, margin, hole_length, support_length):
        support_start = margin + hole_length

        bed_width = 29.5
        bed_space_to_wall = (width - bed_width) / 2
        bed_feet_width = 3

        posy_1 = bed_space_to_wall
        posy_2 = width - bed_space_to_wall

        for y, direction in [(posy_1, 1), (posy_2, -1)]:
            bed_feet_middle_y = y + direction * bed_feet_width / 2
            support_middle_y = y + direction * self.thickness / 2
            self.rectangularHole(
                margin,
                bed_feet_middle_y,
                hole_length,
                bed_feet_width,
                center_x=False,
            )
            self.fingerHolesAt(support_start, support_middle_y, support_length, angle=0)
            self.rectangularHole(
                support_start + support_length,
                bed_feet_middle_y,
                hole_length,
                bed_feet_width,
                center_x=False,
            )

    def render_upper_token_trays(self, tray_inner_height, box_width):
        """
        Upper level : multiple trays for each ressource
        (beside horses which are on the lower level)
        """
        tray_height = tray_inner_height + self.thickness
        upper_level_width = 196
        upper_level_length = box_width
        row_width = upper_level_width / 3

        # Stone / Vegetable / Pig / Cow
        self.render_simple_tray(row_width, upper_level_length, tray_height, 3)
        # Reed / Grain / Sheep
        self.render_simple_tray(row_width, upper_level_length * 2 / 3, tray_height, 2)
        # Wood / Clay
        self.render_simple_tray(row_width, upper_level_length * 2 / 3, tray_height, 1)
        # Food / Fire
        self.render_simple_tray(upper_level_length / 3, row_width * 2, tray_height, 1)

    def render_simple_tray(self, outer_width, outer_length, outer_height, dividers=0):
        """
        One of the upper level trays, with movable dividers.
        """
        width = outer_width - 2 * self.thickness
        length = outer_length - 2 * self.thickness
        height = outer_height - self.thickness
        self.ctx.save()
        self.rectangularWall(width, length, "FFFF", move="up")
        for _ in range(2):
            self.rectangularWall(width, height, "ffef", move="up")
        self.ctx.restore()
        self.rectangularWall(width, length, "FFFF", move="right only")
        for _ in range(2):
            self.rectangularWall(height, length, "FfFe", move="right")

        if dividers:
            self.ctx.save()
            for _ in range(dividers):
                self.render_simple_tray_divider(width, height, "up")
            self.ctx.restore()
            self.render_simple_tray_divider(width, height, "right only")

    def render_simple_tray_divider(self, width, height, move):
        """
        Simple movable divider. A wall with small feet for a little more stability.
        """

        if self.move(height, width, move, True):
            return

        t = self.thickness
        self.polyline(
            height - t,
            90,
            t,
            -90,
            t,
            90,
            width - 2 * t,
            90,
            t,
            -90,
            t,
            90,
            height - t,
            90,
            width,
            90,
        )

        self.move(height, width, move)

        self.render_simple_tray_divider_feet(width, height, move)

    def render_simple_tray_divider_feet(self, width, height, move):
        sqr2 = math.sqrt(2)
        t = self.thickness
        divider_foot_width = 2 * t
        full_width = t + 2 * divider_foot_width
        move_length = self.spacing + full_width / sqr2
        move_width = self.spacing + max(full_width, height)

        if self.move(move_width, move_length, move, True):
            return

        self.ctx.save()
        self.polyline(
            sqr2 * divider_foot_width,
            135,
            t,
            -90,
            t,
            -90,
            t,
            135,
            sqr2 * divider_foot_width,
            135,
            full_width,
            135,
        )
        self.ctx.restore()

        self.moveTo(-self.burn / sqr2, self.burn * (1 + 1 / sqr2), 45)
        self.moveTo(full_width)

        self.polyline(
            0,
            135,
            sqr2 * divider_foot_width,
            135,
            t,
            -90,
            t,
            -90,
            t,
            135,
            sqr2 * divider_foot_width,
            135,
        )

        self.move(move_width, move_length, move)


class MoorBoxSideEdge(edges.BaseEdge):
    """
    Edge for the sides of the moor tiles box
    """

    def __init__(self, boxes, corner_length, corner_height, lower_corner):
        super().__init__(boxes, None)
        self.corner_height = corner_height
        self.lower_corner = lower_corner
        self.corner_length = corner_length

    def __call__(self, length, **kw):
        radius = self.corner_height / 2
        if self.lower_corner:
            self.polyline(
                length - self.corner_height - self.corner_length,
                (90, radius),
                0,
                (-90, radius),
                self.corner_length,
            )
        else:
            self.polyline(length)

    def startwidth(self):
        return self.corner_height

    def endwidth(self):
        return 0 if self.lower_corner else self.corner_height


class MoorBoxHoleEdge(edges.BaseEdge):
    """
    Edge which does the notches for the moor tiles box
    """

    def __init__(self, boxes, height, corner_height, lower_corner):
        super().__init__(boxes, None)
        self.height = height
        self.corner_height = corner_height
        self.lower_corner = lower_corner

    def __call__(self, length, **kw):
        one_side_width = (length - self.thickness) / 2
        notch_width = 20
        radius = 6
        upper_edge = (one_side_width - notch_width - 2 * radius) / 2
        hole_start = 10
        lowered_hole_start = 2
        hole_depth = self.height - 2 * radius
        lower_edge = notch_width - 2 * radius

        one_side_polyline = lambda margin1, margin2: [
            upper_edge,
            (90, radius),
            hole_depth - margin1,
            (-90, radius),
            lower_edge,
            (-90, radius),
            hole_depth - margin2,
            (90, radius),
            upper_edge,
        ]

        normal_side_polyline = one_side_polyline(hole_start, hole_start)
        corner_side_polyline = one_side_polyline(
            lowered_hole_start, lowered_hole_start + self.corner_height
        )

        full_polyline = (
            normal_side_polyline
            + [0, self.thickness, 0]
            + (corner_side_polyline if self.lower_corner else normal_side_polyline)
        )
        self.polyline(*full_polyline)

    def startwidth(self):
        return self.corner_height

    def endwidth(self):
        return 0 if self.lower_corner else self.corner_height


class BedHeadEdge(edges.BaseEdge):
    """
    Edge which does the head side of the Agricola player box
    """

    def __init__(self, boxes, hole_depth):
        super().__init__(boxes, None)
        self.hole_depth = hole_depth

    def __call__(self, length, **kw):
        hole_length = 16
        upper_corner = 10
        lower_corner = 6
        depth = self.hole_depth - upper_corner - lower_corner
        upper_edge = (length - hole_length - 2 * upper_corner) / 2
        lower_edge = hole_length - 2 * lower_corner

        self.polyline(
            upper_edge,
            (90, upper_corner),
            depth,
            (-90, lower_corner),
            lower_edge,
            (-90, lower_corner),
            depth,
            (90, upper_corner),
            upper_edge,
        )


class Bed2SidesEdge(edges.BaseEdge):
    """
    Edge which does a bed like shape, skipping the next corner.
    The next edge should be a NoopEdge
    """

    def __init__(self, boxes, bed_length, full_head_length, full_foot_height):
        super().__init__(boxes, None)
        self.bed_length = bed_length
        self.full_head_length = full_head_length
        self.full_foot_height = full_foot_height

    def __call__(self, bed_height, **kw):
        foot_corner = 6
        middle_corner = 3
        head_corner = 10
        foot_height = self.full_foot_height - self.thickness - foot_corner
        head_length = self.full_head_length - head_corner - self.thickness
        corners = foot_corner + middle_corner + head_corner
        head_height = bed_height - foot_height - corners
        middle_length = self.bed_length - head_length - corners

        self.polyline(
            foot_height,
            (90, foot_corner),
            middle_length,
            (-90, middle_corner),
            head_height,
            (90, head_corner),
            head_length,
        )


class NoopEdge(edges.BaseEdge):
    """
    Edge which does nothing, not even turn or move.
    """

    def __init__(self, boxes):
        super().__init__(boxes, None)

    def __call__(self, length, **kw):
        # cancel turn
        self.corner(-90)
