#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
from functools import partial
from time import sleep
from boxes import Boxes, edges, boolarg
from .dividertray import (
    SlotDescriptionsGenerator,
    DividerSlotsEdge,
)


class CardGameTrayInsert(Boxes):
    """
    Tray insert for card games.
    """

    ui_group = "Tray"

    description = """
This insert was designed with 3 mm plywood in mind, and should work fine with
materials around this thickness.

This tray insert is heavily inspired (i.e., mostly stolen, with some additional
features) by the tray that is part of the Agricola
Insert box, as well as the divider tray.

The cards are all kept in a tray, with paper dividers to sort them easily. When
the tray is not full of cards, wood dividers slides in slots in order to keep
the cards from falling into the empty space.

To keep a lower profile, the cards are at a slight angle, and the paper dividers
tabs are horizontal instead of vertical.
A small wall keeps the card against one side while the tabs protrude on the
other side, above the small wall.

The wall with the big hole is the sloped one. It goes between the two
"comb-like" walls first, with its two small holes at the bottom. Then there is a
low-height long wall with a sloped edge which should go from the sloped wall to
the other side. You can finish the tray with the last wall at the end.

![3D example](static/samples/CardGameTrayInsert.png)

"""

    # TODO with side tab / without side tab
    # TODO at an angle, without an angle
    # TODO no hole if no angle
    # TODO add bottom
    # TODO add posibility of no bottom
    # TODO many columns, like DividerTray
    # TODO number of slots

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=1.0)
        self.argparser.add_argument(
            "--card_width",
            type=float,
            default=90,
            help="width of a card",
        )
        self.argparser.add_argument(
            "--tray_length",
            action="store",
            type=float,
            default=170,
            help="total outside length of the tray"
        )
        self.argparser.add_argument(
            "--card_height",
            action="store",
            type=float,
            default=63,
            help="height of a card"
        )
        self.argparser.add_argument(
            "--tray_height",
            type=float,
            default=0,
            help="height of the tray, 0 for matching the card height. If the height is smaller than the card height, the divider slots will be set at an angle."
        )
        self.argparser.add_argument(
            "--with_bottom",
            type=boolarg,
            default=True,
            help="if the tray is to have a bottom"
        )
        self.argparser.add_argument(
            "--horizontal_tabs",
            type=boolarg,
            default=True,
            help="the dividers have their tabs on the side, and a little wall is added to the tray itself"
        )
        self.argparser.add_argument(
            "--slot_density",
            type=int,
            default=20,
            help="how many mm between dividing slots"
        )

    def render(self):
        player_box_height = 34.5
        player_box_inner_width = 50.5
        bigger_box_inner_height = 36.7
        row_width = 37.2
        tray_inner_height = 17
        box_width = 218

        if self.tray_height == 0:
            self.tray_height = self.card_height

        # TODO when bottom, add thickness
        card_tray_height = self.tray_height
        if self.with_bottom:
            card_tray_height = card_tray_height - self.thickness

        card_tray_width = self.card_width
        if self.horizontal_tabs:
            card_tray_width = card_tray_width + self.thickness

        self.render_card_divider_tray(card_tray_height, self.tray_length, card_tray_width)

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

        has_sloped_wall = card_tray_height < self.card_height

        rad = math.acos(card_tray_height / self.card_height) if has_sloped_wall else 0

        angle = math.degrees(rad)
        cos = math.cos(rad)
        tan = math.tan(rad)
        sin = math.sin(rad)

        slots_number = math.floor(tray_inner_length / self.slot_density)

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

        if has_sloped_wall:
            sloped_wall_height = self.card_height - self.thickness * (tan + 1 / tan)
        else:
            sloped_wall_height = self.card_height

        sloped_wall_posx_at_y0 = (
            tray_inner_length - sloped_wall_height * tan - cos * self.thickness
        )
        sloped_wall_posx = sloped_wall_posx_at_y0 + cos * self.thickness / 2
        sloped_wall_posy = sin * self.thickness / 2

        sloped_holes = lambda: self.fingerHolesAt(
                        sloped_wall_posx,
                        sloped_wall_posy,
                        sloped_wall_height,
                        angle=90 - angle,
                    )

        dse = DividerSlotsEdge(self, slot_descriptions.descriptions)

        # side walls
        for _ in range(2):
            self.rectangularWall(
                tray_inner_length,
                card_tray_height,
                ["F", "e", dse, "f"],
                move="up",
                callback=[
                    partial( sloped_holes )
                ],
            )

        # generate spacer
        spacer_height = card_tray_height / 2

        # for the longer tab in the divider
        spacer_spacing = self.thickness

        spacer_upper_width = sloped_wall_posx_at_y0 + spacer_height * tan

        if self.horizontal_tabs:
            self.low_side_wall(spacer_height,spacer_upper_width,sloped_wall_posx_at_y0)

        if self.with_bottom:
            bottom_edges = "feff" if has_sloped_wall else "ffff"
            self.rectangularWall(
                card_tray_length,
                card_tray_width,
                bottom_edges,
                move="up"
            )

        self.front_wall(card_tray_width, card_tray_height, spacer_spacing,
                   spacer_height)

        self.back_wall(card_tray_width,sloped_wall_height,spacer_height,
                       spacer_spacing, rad)


        self.ctx.restore()
        self.rectangularWall(card_tray_length, 0, "FFFF", move="right only")
        self.ctx.save()

        divider_height = self.card_height - self.thickness * tan
        self.generate_divider(
            card_tray_width - 2 * self.thickness, divider_height, slot_depth, spacer_spacing, "up"
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
            card_tray_width, self.card_height, slot_depth, spacer_spacing, "up"
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

    def back_wall(self, card_tray_width, sloped_wall_height, spacer_height,
                  spacer_spacing, rad):

        edges = "efef" if rad > 0 else "Ffef"

        self.rectangularWall(
            card_tray_width,
            sloped_wall_height,
            edges,
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

    def low_side_wall(self,spacer_height,spacer_upper_width,sloped_wall_posx_at_y0):
            self.trapezoidWall(
                spacer_height,
                spacer_upper_width,
                sloped_wall_posx_at_y0,
                "fefe",
                move="up rotated",
            )


    def front_wall(self, card_tray_width, card_tray_height, spacer_spacing,
                   spacer_height):

        if self.horizontal_tabs:
            holes = lambda: self.fingerHolesAt(
                        spacer_spacing - self.thickness / 2, 0, spacer_height
                    )
        else:
            holes = lambda: "dummy"

        self.rectangularWall(
            card_tray_width,
            card_tray_height,
            "FFeF",
            move="up",
            callback=[
                partial( holes )
            ],
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
        if self.horizontal_tabs:
            self.fingerHolesAt(
                side_wall_length - (spacer_spacing - self.thickness / 2),
                # the sloped wall doesn't exactly touch the bottom of the spacer
                -self.thickness * math.tan(rad),
                spacer_height / math.cos(rad),
            )

        # Big hole to access "lost" space behind sloped wall
        if rad > 0:
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
        total_width = width


        if self.move(total_width, height, move, True):
            return

        radius = 16
        padding = 20
        divider_notch_depth = 35

        print( width, spacer_spacing, padding, radius )

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

    def generate_side_finger_holes(self, row_width, height):
        self.fingerHolesAt(row_width + 0.5 * self.thickness, 0, height)


