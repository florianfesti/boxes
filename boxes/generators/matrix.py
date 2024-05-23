# Copyright (C) 2024 fidoriel
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


class Matrix(Boxes):
    """WS2812b matrix enclosure"""

    description = """## Simple WS2812b matrix enclosure
    WS2812b matrix enclosure for cheap chinease prebuild led matrixes.
    This design assumes that the distance between the leds is equal in both directions.

    There are several parts to this design:
    - The inner frame to hold the pcb in place
    - The front frame to hold a sandwich of plexiglass, spacer and the pcb
    - The plexiglass to protect and diffuse the leds.
        You may add car tint foil to the plexiglass to achieve a black look
    - The spacer to keep the plexiglass from touching the leds
    - The back box with an optional mounting hole. Please add a hole for the
        power supply to the side panels and the power and data cables
        through the led mount frame with your favorite svg editor.
    - The side panels with finger joints to hold everything together

    Assembly:
    1. Cut the parts
    2. Assemble the frame (side panels and inner frame)
    3. Insert the pcb, the spacers and the plexiglass
    4. Close the front frame
    5. Insert electronics in the back box
        (for example a USB C port on the side panel, a esp32 with wled firmware)
    6. Close the back box

    The inner frame and spacer should keep everything in place without the need for glue.
    If you are using multiple modules,
    you can add the layout parameters, so that the inner frame adjusts accordingly.

    Please Note: if you are creating a large matrix build of multiple individual modules,
    you need to enter absolute values across all modules for all parameters.
    Please cut the plane labeled "Plexiglass" out of plexiglass :)
    You can use a different thickness for the plexiglass, but make sure to adjust the settings accordingly.
    """
    ui_group = "misc"

    led_width: int
    led_height: int
    pysical_led_y: int
    pysical_led_x: int

    distance_between_leds: float
    plexiglass_thicknes: float

    h: int

    matrix_back_frame_border: int = 20
    matrix_front_frame_border_offset: int = 10

    height_pcb: float

    bottom_edge: str = "F"

    mounting_holes: bool
    mounting_hole_diameter: float

    matrix_count_x: int
    matrix_count_y: int

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)

        self.argparser.add_argument(
            "--led_width",
            action="store",
            type=int,
            default=16,
            help="Width of the LED matrix in pixels",
        )

        self.argparser.add_argument(
            "--led_height",
            action="store",
            type=int,
            default=16,
            help="Height of the LED matrix in pixels",
        )

        self.argparser.add_argument(
            "--pysical_led_y",
            action="store",
            type=int,
            default=160,
            help="Width of the LED matrix pcb in mm",
        )

        self.argparser.add_argument(
            "--pysical_led_x",
            action="store",
            type=int,
            default=160,
            help="Height of the LED matrix pcb in mm",
        )

        self.argparser.add_argument(
            "--matrix_back_frame_border",
            action="store",
            type=int,
            default=20,
            help="Border of the back frame bo keep the pcb in blace but allow for air flow and cable management",
        )

        self.argparser.add_argument(
            "--matrix_front_frame_border_offset",
            action="store",
            type=int,
            default=10,
            help="Offset of the front frame to allow for the plexiglass to be attached",
        )

        self.argparser.add_argument(
            "--distance_between_leds",
            action="store",
            type=float,
            default=1,
            help="Distance of the color dividers. Make sure your machine is able to cut thin structures.",
        )

        self.argparser.add_argument(
            "--h",
            action="store",
            type=int,
            default=30,
            help="Height of the matrix",
        )

        self.argparser.add_argument(
            "--height_pcb",
            action="store",
            type=float,
            default=0.2,
            help="Height of the pcb including the highest non led components in mm",
        )

        self.argparser.add_argument(
            "--plexiglass_thicknes",
            action="store",
            type=float,
            default=3,
            help="Thickness of the plexiglass in mm",
        )

        self.argparser.add_argument(
            "--mounting_holes",
            action="store",
            type=boolarg,
            default=False,
            help="Add mounting holes for the enclosure",
        )

        self.argparser.add_argument(
            "--mounting_hole_diameter",
            action="store",
            type=float,
            default=5,
            help="Diameter of the mounting holes in mm",
        )

        self.argparser.add_argument(
            "--matrix_count_x",
            action="store",
            type=int,
            default=1,
            help="Number of modules in x direction",
        )

        self.argparser.add_argument(
            "--matrix_count_y",
            action="store",
            type=int,
            default=1,
            help="Number of modules in y direction",
        )

        self.buildArgParser()

    def draw_frame(self, sizex: int, sizey: int, posx: int, posy: int):
        self.rectangularHole(
            x=posx,
            y=posy,
            dx=sizex,
            dy=sizey,
            r=0,
            center_x=False,
            center_y=False,
        )

    def matrix_back_sideholes(self, length: int):
        sandwich_height = (
            2 * self.thickness + self.plexiglass_thicknes + self.height_pcb
        )
        h = -0.5 * self.thickness + self.h - sandwich_height
        self.fingerHolesAt(0, h, length, angle=0)

    def draw_led_grid(self):
        space_per_led_x = self.pysical_led_x / self.led_width
        space_per_led_y = self.pysical_led_y / self.led_height
        for x in range(self.led_width):
            for y in range(self.led_height):
                self.rectangularHole(
                    x=self.matrix_front_frame_border_offset
                    + (x * space_per_led_x)
                    + self.distance_between_leds / 2,
                    y=self.matrix_front_frame_border_offset
                    + (y * space_per_led_y)
                    + self.distance_between_leds / 2,
                    dx=space_per_led_x - self.distance_between_leds,
                    dy=space_per_led_y - self.distance_between_leds,
                    r=0,
                    center_x=False,
                    center_y=False,
                )

    def create_mounting_holes(self):
        if self.mounting_holes:
            pos_x = (self.pysical_led_x + 2 * self.matrix_front_frame_border_offset) / 2
            pos_y = (
                (self.pysical_led_y + 2 * self.matrix_front_frame_border_offset) * 3 / 4
            )
            self.rectangularHole(
                x=pos_x,
                y=pos_y,
                dx=self.mounting_hole_diameter,
                dy=self.mounting_hole_diameter,
                r=self.mounting_hole_diameter,
            )
            self.rectangularHole(
                x=pos_x,
                y=pos_y + self.mounting_hole_diameter / 2,
                dx=self.mounting_hole_diameter / 2,
                dy=self.mounting_hole_diameter / 2,
                r=self.mounting_hole_diameter,
            )

    def render(self):
        x, y, h = (
            self.pysical_led_x + 2 * self.matrix_front_frame_border_offset,
            self.pysical_led_y + 2 * self.matrix_front_frame_border_offset,
            self.h,
        )

        d2 = edges.Bolts(2)
        d3 = edges.Bolts(3)

        d2 = d3 = None

        self.rectangularWall(
            x,
            h,
            "FFFF",
            bedBolts=[d2] * 4,
            move="up",
            label="Wall 1",
            callback=[
                lambda: self.matrix_back_sideholes(
                    self.pysical_led_x + 2 * self.matrix_front_frame_border_offset
                )
            ],
        )
        self.rectangularWall(
            y,
            h,
            "FfFf",
            bedBolts=[d3, d2, d3, d2],
            move="up",
            label="Wall 2",
            callback=[
                lambda: self.matrix_back_sideholes(
                    self.pysical_led_x + 2 * self.matrix_front_frame_border_offset
                )
            ],
        )
        self.rectangularWall(
            y,
            h,
            "FfFf",
            move="up",
            bedBolts=[d3, d2, d3, d2],
            label="Wall 4",
            callback=[
                lambda: self.matrix_back_sideholes(
                    self.pysical_led_y + 2 * self.matrix_front_frame_border_offset
                )
            ],
        )
        self.rectangularWall(
            x,
            h,
            "FFFF",
            bedBolts=[d2] * 4,
            move="up",
            label="Wall 3",
            callback=[
                lambda: self.matrix_back_sideholes(
                    self.pysical_led_y + 2 * self.matrix_front_frame_border_offset
                )
            ],
        )

        self.rectangularWall(
            x,
            y,
            "ffff",
            bedBolts=[d2, d3, d2, d3],
            move="right",
            label="Top",
            callback=[
                lambda: self.draw_frame(
                    sizex=self.pysical_led_x,
                    sizey=self.pysical_led_y,
                    posx=self.matrix_front_frame_border_offset,
                    posy=self.matrix_front_frame_border_offset,
                )
            ],
        )
        self.rectangularWall(
            x,
            y,
            "ffff",
            bedBolts=[d2, d3, d2, d3],
            move="right",
            label="Bottom",
            callback=[self.create_mounting_holes],
        )
        self.rectangularWall(
            x,
            y,
            "ffff",
            bedBolts=[d2, d3, d2, d3],
            move="right",
            label="matrix mount frame, please add cable holes as needed",
        )

        self.rectangularWall(
            x,
            y,
            label="led_grid",
            move="right",
            callback=[lambda: self.draw_led_grid()],
        )

        self.rectangularWall(
            x,
            y,
            label="led_grid",
            move="right",
            callback=[lambda: self.draw_led_grid()],
        )

        self.rectangularWall(x, y, label="Plexiglass")
