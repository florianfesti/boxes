# Copyright (C) 2013-2024 Florian Festi / Melchior Rabe
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


class FatBallDispenser(Boxes):
    """Birdhouse for fat balls."""
    description = """
### Description
Fat balls are quite common to feed tits. Here you can build a dispenser that protects
the fat balls from rain and snow. The design was tested using 4mm plywood for the
main structural parts. For the spacer of the locking mechanism two layers of 3mm
plywood have been stacked. The poles were made from 8mm diameter beech rod and 19cm
in length. Some basic consistency checks have been made for different numbers, but
only the defaults have ever been built.

The final dispenser consists of two parts which slide into each other. You can mount
a hook to hang it into a tree. All edges that have angles different from 90 degrees (chamfers)
have engraved guiding lines which indicate the angle. You have to sand the edge such
that the pieces fit together.

The top part (roof) consists of the the following elements for a N sided dispenser:

  * The N sided roof bottom plate which supports the roof tiles. It has a central cut out
    which is needed for assembly and on the bottom side an engraved line which indicates the
    position of the mounting bracket.
  * N triangles forming the roof. They also have a small arc at the tip (roof_hole_diameter)
  which acts as a drilling guide if you want to mount a hook.
  * The N sided roof support piece which has a central hole for the hook. It is been mounted
  to the roof tiles through the hole in the roof bottom plate to support the roof
  tiles and acts as a mounting plate for the hook.
  * Spacer(s); in the reference builds 2 spacers using 3mm plywood have been used. The spacer
  needs to be a bit thicker than the ceiling (see below). That's the smaller
  "U" shaped part which is glued to the bottom side of the roof bottom plate.
  * The bracket is also "U" shaped and a bit wider than the spacer. This is glued to the
  bottom of the spacer and holds the cage (bottom part).

The bottom part (cage) consists of the follwoing elements:

  * The ceiling is N sided with the central refill hole and N smaller holes into which
  the poles are fitted.
  * The N sided floor part with finger joints for the balcony walls and holes for
  the poles. A central hole to drain rain water can be added as well.
  * N balcony walls surrounding the floor.
  * N poles that join floor and ceiling (not part of the drawing)

Other parts needed for assembly:

  * Wooden rod (N times the length of the poles).
  * A hook (e.g. M5x50mm)
  * A washer to distribute the load of the hook to the support piece
  * One or two nuts to secure the hook
  * Optional, a pice of wire mesh

Assembly:

  * Sand all chamfers
  * Glue balcony walls to the floor
  * Glue pairs of roof tiles and use the roof bottom plate as a jig, Hot glue may be used to
    tack the parts.
  * Glue all roof tiles to form the roof
  * Glue spacer(s) and the bracket into a stack
  * Glue roof tiles to the roof bottom plate and attach the support piece
  * Glue the stack to the roof bottom plate
  * Cut the poles to length
  * If you want to use multiple colors paint now, otherwise you also can paint later
  * After painting you may need to get the paint out of the pole holes again using a drillbit
  * Glue the poles into floor plate and ceiling
  * Attach the hanger
  * Attach the wire mesh
    """

    # naming conventions used in the code:
    # Radii (center to corner for polygons) are prefixed with `r_`
    # Angles in degrees use `a_` and angles in radians use `ar_` as prefix
    # Edges of polygons are prefixed with `l_`

    ui_group = "Unstable"  # see ./__init__.py for names

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.buildArgParser()
        # Add non default cli params if needed (see argparse std lib)
        self.argparser.add_argument(
            "--sides",  action="store", type=int, default=6,
            help="The number of sides of the floor plan.")
        self.argparser.add_argument(
            "--pole_diameter",  action="store", type=float, default=8.0,
            help="The diameter of the poles.")
        self.argparser.add_argument(
            "--ball_diameter",  action="store", type=float, default=75.0,
            help="The diameter of the fat balls. Give some extra mm to make it a loose fit")
        self.argparser.add_argument(
            "--balcony_width",  action="store", type=float, default=15.0,
            help="The width of the area outside of the poles.")
        self.argparser.add_argument(
            "--balcony_height",  action="store", type=float, default=20.0,
            help="The height of the balcony in mm. Set to 0 if no walls are needed.")
        self.argparser.add_argument(
            "--drain_hole_diameter",  action="store", type=float, default=5.0,
            help="""The diameter of the hole of the floor (to drain rainwater)
                    in mm. Set to 0 if you don't need it.""")
        self.argparser.add_argument(
            "--pole_clearance",  action="store", type=float, default=9.0,
            help="""The minimum distance between a pole and the central
                    refill hole in the ceiling in mm.""")
        self.argparser.add_argument(
            "--slide_clearance",  action="store", type=float, default=1.0,
            help="""The gap between the parts that slide into each other
                    in the locking mechanism in mm.""")
        self.argparser.add_argument(
            "--spacer_width",  action="store", type=float, default=15.0,
            help="The width of the spacer (part of the locking mechanism) in mm.")
        self.argparser.add_argument(
            "--pole_clearance_factor",  action="store", type=float, default=0.9,
            help="""The fraction of the pole clearance which is being used for
                    the locking mechanism.""")
        self.argparser.add_argument(
            "--roof_overhang",  action="store", type=float, default=20.0,
            help="Defines how much wider than the bottom floor the roof is.")
        self.argparser.add_argument(
            "--roof_height",  action="store", type=float, default=50.0,
            help="The height of the roof in mm.")
        self.argparser.add_argument(
            "--roof_hole_diameter",  action="store", type=float, default=5.0,
            help="""The diameter of the hole of the roof in mm.
                    Set to 0 if you don't want to attach a hanger.""")
        self.argparser.add_argument(
            "--roof_maintenance_clearance",  action="store", type=float, default=20.0,
            help="The distance from on bottom corner of the roof to the maintenance hole in mm.")
        self.argparser.add_argument(
            "--roof_support_fraction",  action="store", type=float, default=0.3,
            help="The radius of the roof support part as a fraction of the roof radius.")

    def calc_tile_angle(self, radius, height):
        """
            Calculate the angle (deg) between two roof tiles.
        """

        def cross(a, b):
            """
                The cross product of two vectors
            """
            c = [a[1]*b[2] - a[2]*b[1],
                 a[2]*b[0] - a[0]*b[2],
                 a[0]*b[1] - a[1]*b[0]]

            return c

        def scalar(a, b):
            """
                The scalar product of two vectors
            """
            return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

        def norm(a):
            """
                The norm of a vector
            """
            return math.sqrt(a[0]**2 + a[1]**2 + a[2]**2)

        def add(a, b):
            """
                The sum of two vectors
            """
            return [aa + bb for aa, bb in zip(a, b)]

        ar_center = math.radians(360/self.sides)
        base = radius * math.sin(ar_center / 2) * 2
        base_height = radius * math.cos(ar_center / 2)

        # Points are
        # P one corner at the bottom of the pyramid
        # C The center of the bottom of the pyramid
        # O The tip of the pyramid
        # Q, B the corners of the pyramid left and right of P

        pc = [-base/2, base_height, 0]
        pb = [-base, 0, 0]
        co = [0, 0, height]
        pq = [base * math.cos(ar_center), base * math.sin(ar_center), 0]

        po = add(pc, co)

        n1 = cross(pq, po)
        n2 = cross(po, pb)

        cos_e = scalar(n1, n2) / (norm(n1) * norm(n2))
        e = math.degrees(math.acos(cos_e))
        return e

    def get_pole_callback(self, pole_inset, pole_diameter, r_ceiling):
        """
            Returns a callback function that renders the pole (and other)
            holes into floor and ceiling.
        """
        def cb(number):
            if number == 0:
                if r_ceiling > 0:
                    self.hole(0, 0, self.ball_diameter / 2)
                elif self.drain_hole_diameter > 0:
                    self.hole(0, 0, self.drain_hole_diameter / 2)
            else:
                rads = math.radians((180 - (360/self.sides))/2)

                x = pole_inset * math.cos(rads)
                y = pole_inset * math.sin(rads)
                self.hole(x, y, pole_diameter / 2.0)

            if r_ceiling > 0 and 1 <= number <= (self.sides // 2 + 1):
                a_center = 360.0 / self.sides
                a_base = (180 - (360/self.sides))/2
                clearance = self.pole_clearance_factor * self.pole_clearance
                r_clearance = clearance / math.sin(math.radians(a_base))
                r = r_ceiling - r_clearance
                base_length = 2 * r * math.sin(math.radians(a_center / 2))

                dy = r_clearance * math.sin(math.radians(a_base))
                dx = r_clearance * math.cos(math.radians(a_base))
                dx_outside = dy / math.tan(math.radians(a_center))

                length = base_length
                if number == 1:
                    length += dx_outside + dx
                    dx = - dx_outside
                elif number == (self.sides // 2 + 1):
                    length += dx_outside + dx

                self.ctx.stroke()
                with self.saved_context():
                    self.set_source_color(Color.ETCHING)
                    self.moveTo(dx, dy)
                    self.ctx.line_to(length, 0)
                    self.ctx.stroke()

        return cb

    def get_roof_callback(self, r_polygon, r_hole):
        """
            Returns a callback function that renders the
            additional features of the roof bottom plate.
        """
        def cb(number):
            if number == 0:
                # maintenance hole
                self.hole(0, 0, r_hole)

                # engraving to indicate the bracket position
                self.ctx.stroke()
                with self.saved_context():
                    self.set_source_color(Color.ETCHING)
                    self.regularPolygonAt(0, 0, self.sides, r=r_polygon)
                    self.ctx.stroke()

        return cb

    def balcony_wall(self, x, y, finger_padding,
                     callback=None,
                     move=None,
                     label=""):
        """
            Function that renders a balcony wall.
            Due to the calculation of the length of the sides
            of the regularPolygonWall used for the floor plate,
            the finger joints need a bit of padding left and right
            such that they align with the floor plate. This is achieved
            using an "efe" edge at the bottom.
        """
        edges = "efeeee"

        edges = [self.edges.get(e, e) for e in edges]
        edges += edges  # append for wrapping around
        overallwidth = x + edges[-1].spacing() + edges[3].spacing()
        overallheight = y + edges[1].spacing() + edges[4].spacing()

        if self.move(overallwidth, overallheight, move, before=True):
            return

        self.moveTo(0, edges[1].margin())
        for i, l in enumerate((finger_padding, x, finger_padding, y, x+2*finger_padding, y)):
            self.cc(callback, i, y=edges[i].startwidth() + self.burn)
            e1, e2 = edges[i], edges[i + 1]

            edges[i](l)
            if i >= 2:
                self.edgeCorner(e1, e2, 90)

        a_inner = (90 - 360.0 / self.sides)
        inset = self.thickness * math.tan(math.radians(a_inner))
        self.ctx.stroke()
        with self.saved_context():
            self.set_source_color(Color.ETCHING)
            self.moveTo(inset, 0)
            self.ctx.line_to(0, self.balcony_height)
            self.moveTo(x+2*finger_padding-2*inset, 0)
            self.ctx.line_to(0, self.balcony_height)
            self.ctx.stroke()
        self.move(overallwidth, overallheight, move, label=label)

    def roof_tile(self, r_roof, move=None, label=""):
        """
        creates on rooftile

        :param move:  (Default value = None)
        :param label: rendered to identify parts, it is not meant to be cut or etched (Default value = "")
        """
        # calculate the roof dimensions

        a_base = (180 - (360 / self.sides)) / 2.0
        ar_base = math.radians(a_base)
        h_roof = self.roof_height
        l_roof = 2 * r_roof * math.cos(ar_base)
        r_roof_hole = self.roof_hole_diameter / 2
        h_roof_floor = r_roof * math.sin(ar_base)
        h_roof_tile = math.sqrt(h_roof_floor**2 + h_roof**2)

        a_roof = math.degrees(math.atan(h_roof/h_roof_floor))
        ar_roof = math.radians(a_roof)

        ar_tile_base = math.atan(h_roof_tile / (l_roof/2))
        a_tile_base = math.degrees(ar_tile_base)

        edges = [self.edges.get(e, e) for e in "eee"]

        overallwidth = l_roof + 2*edges[0].spacing()
        overallheight = h_roof_tile + 2*edges[0].spacing()

        l_side = math.sqrt((0.5*l_roof)**2 + h_roof_tile**2) - r_roof_hole

        if self.move(overallwidth, overallheight, move, before=True):
            return

        self.moveTo(0, edges[0].margin())

        e1, e2, e3 = edges[0], edges[1], edges[2]

        e1(l_roof)
        self.edgeCorner(e1, e2, 180-a_tile_base)
        e2(l_side)
        self.corner(90)
        self.corner(-(180-2*a_tile_base), radius=r_roof_hole)
        self.corner(90)
        e3(l_side)
        self.edgeCorner(e3, e1, 180-a_tile_base)

        # draw grinding line on base
        dy = self.thickness * math.tan(ar_roof)
        dx = dy / math.tan(ar_tile_base)
        self.ctx.stroke()
        with self.saved_context():
            self.set_source_color(Color.ETCHING)
            self.moveTo(dx, dy)
            self.ctx.line_to(l_roof-2*dx, 0)
            self.ctx.stroke()

        # draw grinding lines on sides
        a_face = self.calc_tile_angle(r_roof, self.roof_height)

        a_face /= 2.0
        l_grinding = self.thickness * math.tan(math.radians(a_face))

        # first we need to calculate the height of the line
        # dy is the distance from the roof tip down to the tip of the "grinding triangle"
        dy = h_roof_tile/l_roof * dx
        dy *= 2
        if r_roof_hole > 0:
            # this is only an approximation, but good enough
            dy = max(dy, r_roof_hole)

        dx_bottom = l_grinding/math.sin(ar_base)
        dx_top = l_roof/2 - (l_roof/2-dx_bottom)/(h_roof_tile/r_roof_hole)

        with self.saved_context():
            self.set_source_color(Color.ETCHING)
            self.moveTo(dx_bottom, 0)
            self.ctx.line_to(dx_top, h_roof_tile-dy)
            self.moveTo(l_roof-2*dx_bottom, 0)
            self.ctx.line_to(-dx_top, h_roof_tile-dy)
            self.ctx.stroke()

        self.move(overallwidth, overallheight, move, label=label)

    def lock_part(self, r_inner, r_outer, move=None, label=""):
        """
            Part of the locking mechanism (spacer and bracket).
        """
        number_of_edges = 2 * (2 + (self.sides // 2))
        edges = [self.edges.get(e, e) for e in "e"*number_of_edges]

        a_center = 360/self.sides
        a_base = (180 - (360/self.sides))/2

        r_inner, _, l_inner = self.regularPolygon(
            corners=self.sides, radius=r_inner)
        r_outer, _, l_outer = self.regularPolygon(
            corners=self.sides, radius=r_outer)

        overallwidth, overallheight = 1.5 * r_outer, 3**0.5 * r_outer

        if self.move(overallwidth, overallheight, move, before=True):
            return

        second_half = number_of_edges / 2

        for i in range(number_of_edges):
            e1, e2 = edges[i], edges[(i+1) % number_of_edges]
            if i in [second_half-1, number_of_edges-1]:
                length = r_outer - r_inner
            elif i < second_half:
                length = l_outer
            else:
                length = l_inner

            if i in [second_half-2]:
                angle = 180 - a_base
            elif i in [second_half-1]:
                angle = a_base
            elif i in [number_of_edges-2]:
                angle = a_base
            elif i in [number_of_edges-1]:
                angle = 180 - a_base
            elif i < second_half:
                angle = a_center
            else:
                angle = - a_center

            e1(length)
            self.edgeCorner(e1, e2, angle)

        self.move(overallwidth, overallheight, move, label=label)

    def render(self):
        # adjust to the variables you want in the local scope
        r_ball = self.ball_diameter / 2
        d_pole = self.pole_diameter
        r_pole = d_pole / 2
        w_balcony = self.balcony_width
        h_balcony = self.balcony_height

        ar_base = math.radians((180 - (360/self.sides))/2)
        r_clearance = self.pole_clearance / math.sin(ar_base)

        r_poles = r_ball + max(r_pole, r_clearance) + r_pole
        r_floor = r_poles + r_pole + max(w_balcony, r_clearance, r_pole)
        r_ceiling = r_poles + r_pole + max(r_clearance, r_pole)
        r_roof = r_floor + self.roof_overhang
        l_roof = 2 * r_roof * math.cos(ar_base)
        t = self.thickness

        floor_outset = t / math.tan(math.radians(90.0-180/self.sides))
        l_floor = 2 * r_floor * math.sin(math.radians(360.0 / self.sides / 2))

        h_roof = self.roof_height
        h_roof_floor = r_roof * math.sin(ar_base)
        a_roof = math.degrees(math.atan(h_roof/h_roof_floor))
        ar_roof = math.radians(a_roof)

        r_support = self.roof_support_fraction * r_roof

        # render the ceiling
        self.regularPolygonWall(corners=self.sides,
                                r=r_ceiling,
                                edges="e",
                                callback=self.get_pole_callback(r_ceiling - r_poles,
                                                                d_pole,
                                                                r_ceiling),
                                move="up")

        # render the roof base
        r_hole = r_ceiling - self.roof_maintenance_clearance
        self.regularPolygonWall(corners=self.sides,
                                r=r_roof, edges="e",
                                callback=self.get_roof_callback(r_polygon=r_ceiling,
                                                                r_hole=r_hole),
                                move="up")

        # only render a balcony if height is >0
        if h_balcony > 0:
            # render the floor plate
            self.regularPolygonWall(corners=self.sides,
                                    r=r_floor,
                                    edges="F",
                                    callback=self.get_pole_callback(r_floor-r_poles,
                                                                    d_pole,
                                                                    0),
                                    move="up")

            # render the balcony walls
            for _ in range(self.sides):
                self.balcony_wall(x=l_floor,
                                  y=h_balcony,
                                  finger_padding=floor_outset,
                                  move="up")
        else:
            # render the floor plate
            self.regularPolygonWall(corners=self.sides,
                                    r=r_floor,
                                    edges="e",
                                    callback=self.get_pole_callback(r_floor - r_poles,
                                                                    d_pole,
                                                                    False),
                                    move="up")

        if self.roof_hole_diameter > 0:
            (_, h_poly, _) = self.regularPolygon(corners=self.sides, radius=r_support)
            new_height = h_poly - self.thickness / math.atan(ar_roof)

            r_polygon = r_support * new_height / h_poly
            r_hole = self.roof_hole_diameter / 2
            self.regularPolygonWall(corners=self.sides,
                                    r=r_support,
                                    edges="e",
                                    callback=self.get_roof_callback(r_polygon=r_polygon,
                                                                    r_hole=r_hole),
                                    move="up")

        # render the spacer
        self.lock_part(r_ceiling + self.slide_clearance,
                       r_ceiling + self.slide_clearance + self.spacer_width,
                       move="up")

        # render the bracket
        r_inner = r_ceiling - r_clearance * self.pole_clearance_factor
        r_outer = r_ceiling + self.slide_clearance + self.spacer_width
        self.lock_part(r_inner, r_outer, move="right")

        # render the roof tiles
        for _ in range(self.sides):
            self.roof_tile(r_roof, move="up")
            self.moveTo((0.5 * l_roof) if _ % 2 else
                        (1.5 * l_roof + 2*self.spacing),
                        0, -180)
