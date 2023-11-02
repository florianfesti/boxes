# Copyright (C) 2022 Erik Snider (SniderThanYou@gmail.com)
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


class DiceBox(Boxes):
    """Box with lid and integraded hinge for storing dice"""

    ui_group = "Box"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(
            edges.FingerJointSettings,
            surroundingspaces=2.0)
        self.addSettingsArgs(
            edges.ChestHingeSettings,
            finger_joints_on_box=True,
            finger_joints_on_lid=True)
        self.buildArgParser(
            x=100,
            y=100,
            h=18,
            outside=True)
        self.argparser.add_argument(
            "--lidheight",  action="store", type=float, default=18,
            help="height of lid in mm")
        self.argparser.add_argument(
            "--hex_hole_corner_radius",  action="store", type=float, default=5,
            help="The corner radius of the hexagonal dice holes, in mm")
        self.argparser.add_argument(
            "--magnet_diameter",  action="store", type=float, default=6,
            help="The diameter of magnets for holding the box closed, in mm")

    def diceCB(self):
        t = self.thickness
        xi = self.x - 2 * t
        yi = self.y - 2 * t
        xc = xi / 2
        yc = yi / 2
        cr = self.hex_hole_corner_radius

        # -4*t because there are four gaps across:
        #   2 between the outer holes and the finger joints
        #   2 between the outer holes and the center hole
        # /6 because there are 6 apothems across, 2 for each hexagon
        apothem = (min(xi, yi) - 4 * t) / 6
        r = apothem * 2 / math.sqrt(3)

        # dice
        centers = [[xc, yc]]  # start with one in the center
        polar_r = 2 * apothem + t  # the full width of a hexagon, plus a gap of t width
        for i in range(6):
            theta = i * math.pi / 3  # 60 degrees each step
            centers.append(
                [
                    xc + polar_r * math.cos(theta),
                    yc + polar_r * math.sin(theta),
                ]
            )
        for center in centers:
            self.regularPolygonHole(x=center[0], y=center[1], n=6, r=r, corner_radius=cr, a=30)

        # magnets
        d = self.magnet_diameter
        mo = t + d/2
        self.hole(mo, mo, d=d)
        self.hole(xi-mo, mo, d=d)

    def render(self):
        x, y, h, hl = self.x, self.y, self.h, self.lidheight

        if self.outside:
            x = self.adjustSize(x)
            y = self.adjustSize(y)
            h = self.adjustSize(h)
            hl = self.adjustSize(hl)

        t = self.thickness

        hy = self.edges["O"].startwidth()
        hy2 = self.edges["P"].startwidth()

        e1 = edges.CompoundEdge(self, "eF", (hy-t, h-hy+t))
        e2 = edges.CompoundEdge(self, "Fe", (h-hy+t, hy-t))
        e_back = ("F", e1, "F", e2)

        p = self.edges["o"].settings.pin_height
        e_inner_1 = edges.CompoundEdge(self, "fe", (y-p, p))
        e_inner_2 = edges.CompoundEdge(self, "ef", (p, y-p))
        e_inner_topbot = ("f", e_inner_1, "f", e_inner_2)

        self.ctx.save()

        self.rectangularWall(x, y, e_inner_topbot, move="up", callback=[self.diceCB])
        self.rectangularWall(x, y, e_inner_topbot, move="up", callback=[self.diceCB])
        self.rectangularWall(x, h, "FFFF", ignore_widths=[1,2,5,6], move="up")
        self.rectangularWall(x, h, e_back, move="up")
        self.rectangularWall(x, hl, "FFFF", ignore_widths=[1,2,5,6], move="up")
        self.rectangularWall(x, hl-hy2+t, "FFqF", move="up")

        self.ctx.restore()
        self.rectangularWall(x, y, "ffff", move="right only")

        self.rectangularWall(y, x, "ffff", move="up")
        self.rectangularWall(y, x, "ffff", move="up")
        self.rectangularWall(y, hl-hy2+t, "Ffpf", ignore_widths=[5,6], move="up")
        self.rectangularWall(y, h-hy+t, "OfFf", ignore_widths=[5,6], move="up")
        self.rectangularWall(y, h-hy+t, "Ffof", ignore_widths=[5,6], move="up")
        self.rectangularWall(y, hl-hy2+t, "PfFf", ignore_widths=[5,6], move="up")
