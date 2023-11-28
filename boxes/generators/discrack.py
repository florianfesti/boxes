# Copyright (C) 2019 chrysn <chrysn@fsfe.org>
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

from math import sqrt, pi, sin, cos

from boxes import *


def offset_radius_in_square(squareside, angle, outset):
    """From the centre of a square, rotate by an angle relative to the
    vertical, move away from the center (down if angle = 0), and then in a
    right angle until the border of the square. Return the length of that last
    segment.

    Note that for consistency with other boxes.py methods, angle is given in
    degree.

    >>> # Without rotation, it's always half the square length
    >>> offset_radius_in_square(20, 0, 0)
    10.0
    >>> offset_radius_in_square(20, 0, 5)
    10.0
    >>> # Without offset, it's half square length divided by cos(angle) -- at
    >>> # least before it hits the next wall
    >>> offset_radius_in_square(20, 15, 0) # doctest:+ELLIPSIS
    10.35276...
    >>> offset_radius_in_square(20, 45, 0) # doctest:+ELLIPSIS
    14.1421...
    >>> # Positive angles make the segment initially shorter...
    >>> offset_radius_in_square(20, 5, 10) < 10
    True
    >>> # ... while negative angles make it longer.
    >>> offset_radius_in_square(20, -5, 10) > 10
    True
    """

    if angle <= -90:
        return offset_radius_in_square(squareside, angle + 180, outset)
    if angle > 90:
        return offset_radius_in_square(squareside, angle - 180, outset)

    angle = angle / 180 * pi

    step_right = outset * sin(angle)
    step_down = outset * cos(angle)

    try:
        len_right = (squareside / 2 - step_right) / cos(angle)
    except ZeroDivisionError:
        return squareside / 2

    if angle == 0:
        return len_right
    if angle > 0:
        len_up = (squareside / 2 + step_down) / sin(angle)

        return min(len_up, len_right)
    else: # angle < 0
        len_down = - (squareside / 2 - step_down) / sin(angle)

        return min(len_down, len_right)

class DiscRack(Boxes):
    """A rack for storing disk-shaped objects vertically next to each other"""

    ui_group = "Shelf"

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.buildArgParser(sx="20*10")
        self.argparser.add_argument(
            "--disc_diameter", action="store", type=float, default=150.0,
            help="Disc diameter in mm")
        self.argparser.add_argument(
            "--disc_thickness", action="store", type=float, default=5.0,
            help="Thickness of the discs in mm")

        self.argparser.add_argument(
            "--lower_factor", action="store", type=float, default=0.75,
            help="Position of the lower rack grids along the radius")
        self.argparser.add_argument(
            "--rear_factor", action="store", type=float, default=0.75,
            help="Position of the rear rack grids along the radius")

        self.argparser.add_argument(
            "--disc_outset", action="store", type=float, default=3.0,
            help="Additional space kept between the disks and the outbox of the rack")

        # These can be parameterized, but the default value of pulling them up
        # to the box front is good enough for so many cases it'd only clutter
        # the user interface.
        #
        # The parameters can be resurfaced when there is something like rare or
        # advanced settings.
        '''
        self.argparser.add_argument(
            "--lower_outset", action="store", type=float, default=0.0,
            help="Space in front of the disk slits (0: automatic)")
        self.argparser.add_argument(
            "--rear_outset", action="store", type=float, default=0.0,
            help="Space above the disk slits (0: automatic)")
        '''

        self.argparser.add_argument(
            "--angle", action="store", type=float, default=18,
            help="Backwards slant of the rack")
        self.addSettingsArgs(edges.FingerJointSettings)

    def parseArgs(self, *args, **kwargs):
        Boxes.parseArgs(self, *args, **kwargs)
        self.lower_outset = self.rear_outset = 0

        self.calculate()

    def calculate(self):
        self.outer = self.disc_diameter + 2 * self.disc_outset

        r = self.disc_diameter / 2

        # distance between radius line and front (or rear) end of the slit
        self.lower_halfslit = r * sqrt(1 - self.lower_factor**2)
        self.rear_halfslit = r * sqrt(1 - self.rear_factor**2)

        if True: # self.lower_outset == 0: # when lower_outset parameter is re-enabled
            toplim = offset_radius_in_square(self.outer, self.angle, r * self.lower_factor)
            # With typical positive angles, the lower surface of board will be limiting
            bottomlim = offset_radius_in_square(self.outer, self.angle, r * self.lower_factor + self.thickness)
            self.lower_outset = min(toplim, bottomlim) - self.lower_halfslit

        if True: # self.rear_outset == 0: # when rear_outset parameter is re-enabled
            # With typical positive angles, the upper surface of board will be limiting
            toplim = offset_radius_in_square(self.outer, -self.angle, r * self.rear_factor)
            bottomlim = offset_radius_in_square(self.outer, -self.angle, r * self.rear_factor + self.thickness)
            self.rear_outset = min(toplim, bottomlim) - self.rear_halfslit

        # front outset, space to radius, space to rear part, plus nothing as fingers extend out
        self.lower_size = self.lower_outset + \
                self.lower_halfslit + \
                r * self.rear_factor

        self.rear_size = r * self.lower_factor + \
                self.rear_halfslit + \
                self.rear_outset

        self.warn_on_demand()

    def warn_on_demand(self):
        warnings = []

        # Are the discs supported on the outer ends?

        def word_thickness(length):
            if length > 0:
                return f"very thin ({length:.2g} mm at a thickness of {self.thickness:.2g} mm)"
            if length < 0:
                return "absent"

        if self.rear_outset < self.thickness:
            warnings.append("Rear upper constraint is %s. Consider increasing the disc outset parameter, or move the angle away from 45°." % word_thickness(self.rear_outset))

        if self.lower_outset < self.thickness:
            warnings.append("Lower front constraint is %s. Consider increasing the disc outset parameter, or move the angle away from 45°." % word_thickness(self.lower_outset))

        # Are the discs supported where the grids meet?

        r = self.disc_diameter / 2
        inner_lowerdistance = r * self.rear_factor - self.lower_halfslit
        inner_reardistance = r * self.lower_factor - self.rear_halfslit

        if inner_lowerdistance < 0 or inner_reardistance < 0:
            warnings.append("Corner is inside the disc radios, discs would not be supported. Consider increasing the factor parameters.")

        # Won't the type-H edge on the rear side make the whole contraption
        # wiggle?

        max_slitlengthplush = offset_radius_in_square(
                self.outer, self.angle, r * self.rear_factor + self.thickness)
        slitlengthplush = self.rear_halfslit + self.thickness * ( 1 +
                self.edgesettings['FingerJoint']['edge_width'])

        if slitlengthplush > max_slitlengthplush:
            warnings.append("Joint would protrude from lower box edge. Consider increasing the the disc outset parameter, or move the angle away from 45°.")

        # Can the discs be removed at all?
        # Does not need explicit checking, for Thales' theorem tells us that at
        # the point where there is barely support in the corner, three contact
        # points on the circle form just a semicircle and the discs can be
        # inserted/removed. When we keep the other contact points and move the
        # slits away from the corner, the disc gets smaller and thus will fit
        # through the opening that is as wide as the diameter of the largest
        # possible circle.

        # Act on warnings

        if warnings:
            self.argparser.error("\n".join(warnings))

    def sidewall_holes(self):
        r = self.disc_diameter / 2

        self.moveTo(self.outer/2, self.outer/2, -self.angle)
        # can now move down to paint horizontal lower part, or right to paint
        # vertical rear part
        with self.saved_context():
            self.moveTo(
                    r * self.rear_factor,
                    -r * self.lower_factor - self.thickness/2,
                    90)
            self.fingerHolesAt(0, 0, self.lower_size)
        with self.saved_context():
            self.moveTo(
                    r * self.rear_factor + self.thickness/2,
                    -r * self.lower_factor,
                    0)
            self.fingerHolesAt(0, 0, self.rear_size)

        if self.debug:
            self.circle(0, 0, self.disc_diameter / 2)

    def _draw_slits(self, inset, halfslit):
        total_x = 0

        for x in self.sx:
            center_x = total_x + x / 2

            total_x += x
            self.rectangularHole(inset, center_x, 2 * halfslit, self.disc_thickness)
            if self.debug:
                self.ctx.rectangle(inset - halfslit, center_x - x/2, 2 * halfslit, x)

    def lower_holes(self):
        r = self.disc_diameter / 2
        inset = self.lower_outset + self.lower_halfslit

        self._draw_slits(inset, self.lower_halfslit)

    def rear_holes(self):
        r = self.disc_diameter / 2
        inset = r * self.lower_factor

        self._draw_slits(inset, self.rear_halfslit)

    def render(self):
        o = self.outer

        self.lower_factor = min(self.lower_factor, 0.99)
        self.rear_factor = min(self.rear_factor, 0.99)

        self.rectangularWall(o, o, "eeee", move="right", callback=[self.sidewall_holes])
        self.rectangularWall(o, o, "eeee", move="right mirror", callback=[self.sidewall_holes])

        self.rectangularWall(self.lower_size, sum(self.sx), "fffe", move="right", callback=[self.lower_holes])
        self.rectangularWall(self.rear_size, sum(self.sx), "fefh", move="right", callback=[self.rear_holes])
