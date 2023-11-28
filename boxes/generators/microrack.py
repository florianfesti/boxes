# Copyright (C) 2019 Gabriel Morell
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


class SBCMicroRack(Boxes):
    """Stackable rackable racks for SBC Pi-Style Computers"""

    webinterface = True
    ui_group = "Shelf"  # see ./__init__.py for names

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.StackableSettings)

        self.buildArgParser(x=56, y=85)

        # count
        self.argparser.add_argument(
            "--sbcs", action="store", type=int, default=5,
            help="how many slots for sbcs",
        )

        # spaces
        self.argparser.add_argument(
            "--clearance_x", action="store", type=int, default=3,
            help="clearance for the board in the box (x) in mm"
        )
        self.argparser.add_argument(
            "--clearance_y", action="store", type=int, default=3,
            help="clearance for the board in the box (y) in mm"
        )
        self.argparser.add_argument(
            "--clearance_z", action="store", type=int, default=28,
            help="SBC Clearance in mm",
        )

        # mounting holes
        self.argparser.add_argument(
            "--hole_dist_edge", action="store", type=float, default=3.5,
            help="hole distance from edge in mm"
        )
        self.argparser.add_argument(
            "--hole_grid_dimension_x", action="store", type=int, default=58,
            help="width of x hole area"
        )
        self.argparser.add_argument(
            "--hole_grid_dimension_y", action="store", type=int, default=49,
            help="width of y hole area"
        )
        self.argparser.add_argument(
            "--hole_diameter", action="store", type=float, default=2.75,
            help="hole diameters"
        )

        # i/o holes
        self.argparser.add_argument(
            "--netusb_z", action="store", type=int, default=18,
            help="height of the net/usb hole mm"
        )
        self.argparser.add_argument(
            "--netusb_x", action="store", type=int, default=53,
            help="width of the net/usb hole in mm"
        )

        # features
        self.argparser.add_argument(
            "--stable", action='store', type=boolarg, default=False,
            help="draw some holes to put a 1/4\" dowel through at the base and top"
        )
        self.argparser.add_argument(
            "--switch", action='store', type=boolarg, default=False,
            help="adds an additional vertical segment to hold the switch in place, works best w/ --stable"
        )
        # TODO flesh this idea out better
        #self.argparser.add_argument(
        #    "--fan", action='store', type=int, default=0, required=False,
        #    help="ensure that the x width is at least this much and as well, draw a snug holder for a fan someplace"
        # )


    def paint_mounting_holes(self):
        cy = self.clearance_y
        cx = self.clearance_x

        h2r = self.hole_diameter
        hde = self.hole_dist_edge
        hgdx = self.hole_grid_dimension_x
        hgdy = self.hole_grid_dimension_y

        self.hole(
            h2r + cx + hde / 2,
            h2r + cy + hde / 2,
            h2r / 2
        )

        self.hole(
            h2r + cx + hgdx + hde / 2,
            h2r + cy + hde / 2,
            h2r / 2
        )

        self.hole(
            h2r + cx + hde / 2,
            h2r + cy + hgdy + hde / 2,
            h2r / 2
        )

        self.hole(
            h2r + cx + hgdx + hde / 2,
            h2r + cy + hgdy + hde / 2,
            h2r / 2
        )

    def paint_stable_features(self):
        if self.stable:
            self.hole(
                10, 10, d=6.5
            )

    def paint_netusb_holes(self):
        t = self.thickness
        x = self.x
        w = x + self.hole_dist_edge * 2
        height_per = self.clearance_z + t 
        usb_height = self.netusb_z
        usb_width = self.netusb_x
        for i in range(self.sbcs):
            self.rectangularHole(w/2, (height_per)*i+15 , usb_width, usb_height, r=1)

    def paint_finger_holes(self):
        t = self.thickness
        height_per = self.clearance_z + t
        for i in range(self.sbcs):
            self.fingerHolesAt((height_per) * i + +height_per/2 + 1.5, self.hole_dist_edge, self.x, 90)

    def render(self):
        # adjust to the variables you want in the local scope
        x, y = self.x, self.y
        t = self.thickness

        height_per = self.clearance_z + t
        height_total = self.sbcs * height_per

        # render your parts here

        with self.saved_context():
            self.rectangularWall(height_total + height_per/2,
                                 x + self.hole_dist_edge * 2,
                                 "eseS",
                                 callback=[self.paint_finger_holes,
                                           self.paint_netusb_holes],
                                 move="up")

            self.rectangularWall(height_total + height_per/2,
                                 x + self.hole_dist_edge * 2,
                                 "eseS",
                                 callback=[self.paint_finger_holes,
                                           self.paint_stable_features],
                                 move="up")

            if self.switch:
                self.rectangularWall(height_total + height_per / 2,
                                     x + self.hole_dist_edge * 2,
                                     "eseS",
                                     callback=[self.paint_stable_features],
                                     move="up")

        self.rectangularWall(height_total + height_per/2,
                             x + self.hole_dist_edge * 2,
                             "eseS",
                             move="right only")

        self.rectangularWall(y + self.hole_dist_edge * 2,
                             x + self.hole_dist_edge * 2,
                             "efef",
                             move="up")

        for i in range(self.sbcs):
            self.rectangularWall(y + self.hole_dist_edge * 2,
                                 x + self.hole_dist_edge * 2,
                                 "efef",
                                 callback=[self.paint_mounting_holes],
                                 move="up")

