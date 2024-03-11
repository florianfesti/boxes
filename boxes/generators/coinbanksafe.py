# Copyright (C) 2024 Oliver Jensen
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


class CoinBankSafe(Boxes):
    """A piggy-bank designed to look like a safe."""

    description ='''
Make sure not to discard the circle cutouts from the lid, base, and door. They are all needed.

![Closed](static/samples/CoinBankSafe-closed.jpg)

![Open](static/samples/CoinBankSafe-open.jpg)

Assemble the locking pins like this: wiggle-disc, number-disc, doorhole-disc, spacer-disc, D-disc.
Glue the first three in place, but do not glue the last two.
Leaving them unglued will allow you change the code, and to remove the pin from the door.

![Pins](static/samples/CoinBankSafe-pins.jpg)

'''

    ui_group = "Misc"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser("x", "y", "h")
        self.argparser.add_argument(
            "--slotlength", action="store", type=float, default=30,
            help="Length of the coin slot in mm")
        self.argparser.add_argument(
            "--slotwidth", action="store", type=float, default=4,
            help="Width of the coin slot in mm")
        self.argparser.add_argument(
            "--handlelength", action="store", type=float, default=8,
            help="Length of handle in multiples of thickness")
        self.argparser.add_argument(
            "--handleclearance", action="store", type=float, default=1.5,
            help="Clearance of handle in multiples of thickness")

    def drawNumbers(self, radius, cover):
        fontsize = 0.8 * (radius - cover)
        for num in range(8):
            angle = num*45
            x = (cover + fontsize *0.4) * math.sin(math.radians(angle))
            y = (cover + fontsize *0.4) * math.cos(math.radians(angle))
            self.text(str(num+1), align="center middle", fontsize=fontsize, angle=-angle, color=[1,0,0],
                          y=y, x=x)

    def lockPin(self, layers, move=None):
        t = self.thickness
        cutout_width = t/3
        barb_length = t
        base_length = layers * t
        base_width = t
        total_length = base_length + barb_length
        total_width = base_width + cutout_width * 0.5
        cutout_angle = math.degrees(math.atan(cutout_width / base_length))
        cutout_length = math.sqrt(cutout_width**2 + base_length**2)

        #self.rectangularWall(5*t, t)

        if self.move(total_length, total_width, move, True):
            return

        self.edge(total_length)
        self.corner(90)
        self.edge(base_width * 1/3)
        self.corner(90)
        self.edge(base_length)
        self.corner(180+cutout_angle, 0)
        self.edge(cutout_length)
        self.corner(90-cutout_angle)
        self.edge(cutout_width * 1.5)
        self.corner(90)
        self.edge(barb_length)
        self.corner(90)
        self.corner(-90, cutout_width * 0.5)
        self.edge(base_length - cutout_width * 0.5)
        self.corner(90)
        self.edge(t)
        self.corner(90)

        self.move(total_length, total_width, move)


    def render(self):
        x, y, h = self.x, self.y, self.h
        t = self.thickness

        slot_length = self.slotlength
        slot_width = self.slotwidth

        handle_length = self.handlelength * t
        handle_clearance = self.handleclearance * t

        # lock parameters
        big_radius = 2.25 * t
        small_radius = 1.4 * t
        doorhole_radius = 1.25 * t
        spacing = 1

        # side walls
        with self.saved_context():
            self.rectangularWall(x, h, "seFf", move="mirror right")
            self.rectangularWall(y, h, "sFFF", move="right")

            # wall with holes for the locking bar
            self.rectangularWall(
                x, h, "sfFe", ignore_widths=[3,4,7,8],
                callback=[lambda: self.fingerHolesAt(2.75*t, 0, h, 90)],
                move="mirror right")

            # locking bar
            self.moveTo(0, self.edges['s'].spacing() + t)
            self.rectangularWall(1.33*t, h, "eeef", move="right")
            # door
            door_clearance = .1 * t # amount to shave off of the door width so it can open
            before_hinge = 1.25 * t - door_clearance
            after_hinge = y - 2.25 * t - door_clearance
            self.moveTo(self.spacing/2, -t)
            self.polyline(
                after_hinge, -90, t, 90, t, 90, t, -90, before_hinge, 90,
                h, 90,
                before_hinge, -90, t, 90, t, 90, t, -90, after_hinge, 90,
                h, 90)
            num_dials = 3
            space_under_dials = 6*big_radius
            space_not_under_dials = h - space_under_dials
            dial_spacing = space_not_under_dials / (num_dials + 1)
            if dial_spacing < 1 :
                min_height = 6*big_radius + 4
                raise ValueError(f"With thickness {t}, h must be at least {min_height} to fit the dials.")

            for pos_y in (h/2,
                          h/2 - (2*big_radius + dial_spacing),
                          h/2 + (2*big_radius + dial_spacing)):
                self.hole(3*t - door_clearance, pos_y, doorhole_radius)
                self.rectangularHole(3*t - door_clearance, pos_y, t, t)
            self.rectangularHole(y/2 - door_clearance, h/2, t, handle_length / 2)

        self.rectangularWall(x, h, "seff", move="up only")

        # top
        self.rectangularWall(
            y, x, "efff", callback=[
                lambda: self.rectangularHole(y/2, x/2, slot_length, slot_width),
                lambda: (self.hole(1.75*t, 1.75*t, 1.15*t),
                         self.rectangularHole(1.75*t, 1.75*t, t, t))],
            label="top", move="right")

        # bottom
        self.rectangularWall(
            y, x, "efff", callback=[
                lambda: (self.hole(1.75*t, 1.75*t, 1.15*t),
                         self.rectangularHole(1.75*t, 1.75*t, t, t))],
            label="bottom", move="right")

        def holeCB():
            self.rectangularHole(0, 0, t, t)
            self.moveTo(0, 0, 45)
            self.rectangularHole(0, 0, t, t)

        # locks
        with self.saved_context():
            self.partsMatrix(3, 1, "right", self.parts.disc, 2*big_radius,
                             callback=lambda: (self.drawNumbers(big_radius, small_radius), self.rectangularHole(0, 0, t, t)))
            self.partsMatrix(3, 1, "right", self.parts.disc, 2*big_radius,
                             dwidth=0.8,callback=holeCB)
            self.partsMatrix(
                3, 1, "right", self.parts.disc, 2*small_radius,
                callback=lambda:self.rectangularHole(0, 0, t, t))
            self.partsMatrix(
                3, 1, "right", self.parts.waivyKnob, 2*small_radius,
                callback=lambda:self.rectangularHole(0, 0, t, t))

        self.partsMatrix(3, 1, "up only", self.parts.disc, 2*big_radius)

        # lock pins
        with self.saved_context():
            self.lockPin(5, move="up")
            self.lockPin(5, move="up")
            self.lockPin(5, move="up")
        self.lockPin(5, move="right only")

        # handle
        self.moveTo(0)
        handle_curve_radius = 0.2 * t
        self.moveTo(t * 2.5)
        self.polyline(
            0,
            (90, handle_curve_radius),
            handle_length - 2 * handle_curve_radius,
            (90, handle_curve_radius),
            handle_clearance - handle_curve_radius,
            90,
            handle_length / 4,
            -90,
            t,
            90,
            handle_length / 2,
            90,
            t,
            -90,
            handle_length / 4,
            90,
            handle_clearance - handle_curve_radius,
            )
