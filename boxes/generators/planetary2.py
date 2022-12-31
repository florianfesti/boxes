#!/usr/bin/env python3
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

from boxes import *


class Planetary2(Boxes):

    """Balanced force Difference Planetary Gear (not yet working properly)"""

    ui_group = "Unstable"

    description = """Still has issues. The middle planetary gears set must not have a mashing sun gear as it can't be a proper gear set."""

    def __init__(self):
        Boxes.__init__(self)
        self.buildArgParser("nema_mount")
        self.argparser.add_argument(
	    "--profile", action="store", type=str, default="GT2_2mm",
            choices=pulley.Pulley.getProfiles(),
            help="profile of the teeth/belt")        
        self.argparser.add_argument(
            "--sunteeth", action="store", type=int, default=20,
            help="number of teeth on sun gear")
        self.argparser.add_argument(
            "--planetteeth", action="store", type=int, default=20,
            help="number of teeth on planets")
        self.argparser.add_argument(
            "--maxplanets", action="store", type=int, default=0,
            help="limit the number of planets (0 for as much as fit)")
        self.argparser.add_argument(
            "--deltateeth", action="store", type=int, default=1,
            help="enable secondary ring with given delta to the ring gear")
        self.argparser.add_argument(
            "--modulus", action="store", type=float, default=1.0,
            help="modulus of the theeth in mm")
        self.argparser.add_argument(
            "--shaft", action="store", type=float, default=6.,
            help="diameter of the shaft")
        self.argparser.add_argument(
            "--screw1", action="store", type=float, default=2.4,
            help="diameter of lower part of the screw hole")
        self.argparser.add_argument(
            "--screw2", action="store", type=float, default=4.,
            help="diameter of upper part of the screw hole")
        self.argparser.add_argument(
            "--pinsize", action="store", type=float, default=3.1,
            help="diameter of alignment pins")
        # self.argparser.add_argument(
        #    "--stages",  action="store", type=int, default=4,
        #    help="number of stages in the gear reduction")

    def pins(self, r, rh, nr=0, angle=0.0):
        self.moveTo(0, 0, angle)

        if nr < 8:
            ang = 20 + 10 * nr
        else:
            ang = 15 + 10 * (nr-8)

        ang = 180 - ang
        for a in (0, ang, -ang):
            self.moveTo(0, 0, a)
            self.hole(r, 0,  rh)
            self.moveTo(0, 0, -a)


    def render(self):

        ringteeth = self.sunteeth + 2 * self.planetteeth
        t = self.thickness
        spoke_width = 4 * t
        pinsize = self.pinsize / 2.

        pitch1, size1, xxx = self.gears.sizes(teeth=self.sunteeth,
                                              dimension=self.modulus)
        pitch2, size2, xxx = self.gears.sizes(teeth=self.planetteeth,
                                              dimension=self.modulus)
        pitch3, size3, xxx = self.gears.sizes(
            teeth=ringteeth, internal_ring=True, spoke_width=spoke_width,
            dimension=self.modulus)

        planets = int(math.pi / (math.asin(float(self.planetteeth + 2) / (self.planetteeth + self.sunteeth))))

        if self.maxplanets:
            planets = min(self.maxplanets, planets)

        # Make sure the teeth mash
        ta = self.sunteeth + ringteeth
        # There are sunteeth+ringteeth mashing positions for the planets
        planetpositions = [round(i * ta / planets) * 360 / ta for i in range(planets)]
        secondary_offsets = [((pos % (360. / (ringteeth - self.deltateeth))) -
                              (pos % (360. / ringteeth)) * ringteeth / self.planetteeth)
                              for pos in planetpositions]

        ratio = (1 + (ringteeth / self.sunteeth)) * (-ringteeth/self.deltateeth)
        # XXX make configurable?
        profile_shift = 20
        pressure_angle = 20

        screw = self.screw1 / 2

        # output
        # XXX simple guess
        belt = self.profile
        pulleyteeth = int((size3-2*t) * math.pi / pulley.Pulley.spacing[belt][1])
        numplanets = planets

        deltamodulus = self.modulus * ringteeth / (ringteeth - self.deltateeth)

        def holes(r):
            def h():
                self.hole(2*t, 2*t, r)
                self.hole(size3-2*t, 2*t, r)
                self.hole(2*t, size3-2*t, r)
                self.hole(size3-2*t, size3-2*t, r)
            return h

        def planets():
            self.moveTo(size3/2, size3/2)
            for angle in planetpositions:
                angle += 180 # compensate for 3 postion in callback
                self.moveTo(0, 0, angle)
                self.hole((pitch1+pitch2), 0, size2/2)
                self.moveTo(0, 0, -angle)

        # Base
        self.rectangularWall(size3, size3, callback=[
            lambda: self.NEMA(self.nema_mount, size3 / 2, size3 / 2),
            holes(screw), planets],
                             move="up")

        def gear():
            self.moveTo(size3 / 2, size3 / 2)
            self.gears(teeth=ringteeth, dimension=self.modulus,
                       angle=pressure_angle, internal_ring=True,
                       spoke_width=spoke_width, teeth_only=True,
                       profile_shift=profile_shift, move="up")

        # Lower primary ring gear
        self.rectangularWall(size3, size3, callback=[gear, holes(screw)], move="up")
        tl = 0.5*size3*(2**0.5-1)*2**0.5
        screw = self.screw2 / 2
        self.rectangularTriangle(tl, tl, num=8, callback=[
            None, lambda:self.hole(2*t, 2*t, screw)], move='up')

        # Secondary ring gears
        def ring():
            self.gears(teeth=ringteeth - self.deltateeth,
                       dimension=deltamodulus,
                       angle=pressure_angle, internal_ring=True,
                       spoke_width=spoke_width, teeth_only=True,
                       profile_shift=profile_shift)
            for i in range(3):
                self.hole((size3-6*t)/2+0.5*pinsize, 0, pinsize)
                self.moveTo(0, 0, 120)

        self.pulley(pulleyteeth, belt, callback=ring, move="up")
        self.pulley(pulleyteeth, belt, callback=ring, move="up")

        # Upper primary ring gear
        self.rectangularWall(size3, size3, callback=[gear, holes(screw)], move="up")
        # top cover plate
        self.rectangularWall(size3, size3, callback=[holes(screw)], move="up")

        # Sun gear
        def sunpins():
            self.hole(0.5*self.shaft+1.5*pinsize ,0, pinsize)
            self.hole(-0.5*self.shaft-1.5*pinsize ,0, pinsize)
        self.partsMatrix(4, 4, 'up', self.gears, teeth=self.sunteeth,
                         dimension=self.modulus, callback=sunpins,
                         angle=pressure_angle, mount_hole=self.shaft,
                         profile_shift=profile_shift)

        # Planets
        for i in range(numplanets):
            with self.saved_context():
                self.gears(teeth=self.planetteeth, dimension=self.modulus,
                           angle=pressure_angle,
                           callback=lambda:self.pins(0.25*size2, pinsize, i),
                           profile_shift=profile_shift, move="right")
                for j in range(2):
                    self.gears(teeth=self.planetteeth, dimension=self.modulus,
                               angle=pressure_angle,
                               callback=lambda:self.pins(0.25*size2, pinsize, i,
                                                         secondary_offsets[i]),
                               profile_shift=profile_shift, move="right")
                    self.gears(teeth=self.planetteeth, dimension=self.modulus,
                               angle=pressure_angle,
                               callback=lambda:self.pins(0.25*size2, pinsize, i),
                               profile_shift=profile_shift, move="right")

            self.gears(teeth=self.planetteeth, dimension=self.modulus,
                       angle=pressure_angle,
                       profile_shift=profile_shift, move="up only")

        self.text("1:%.1f" % abs(ratio))
