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

from boxes import Boxes, edges, boolarg


class PaintStorage(Boxes):
    """Stackable storage for hobby paint or other things"""

    webinterface = True
    ui_group = "Shelf"  # see ./__init__.py for names

    canheight: int
    candiameter: int
    minspace: int
    additional_bottom: int
    additional_top: int
    hexpattern: bool
    drawer: bool

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.StackableSettings)

        self.buildArgParser(x=100, y=300)

        self.argparser.add_argument(
            "--canheight", action="store", type=int, default=50,
            help="Height of the paintcans")
        self.argparser.add_argument(
            "--candiameter", action="store", type=int, default=30,
            help="Diameter of the paintcans")
        self.argparser.add_argument(
            "--minspace", action="store", type=int, default=10,
            help="Minimum space between the paintcans")
        self.argparser.add_argument(
            "--additional_bottom", action="store", type=boolarg, default=False,
            help="Additional bottom/floor with holes the paintcans go through")
        self.argparser.add_argument(
            "--additional_top", action="store", type=boolarg, default=False,
            help="Additional top/floor with holes the paintcans go through")
        self.argparser.add_argument(
            "--hexpattern", action="store", type=boolarg, default=False,
            help="Use hexagonal arrangement for the holes instead of orthogonal")
        self.argparser.add_argument(
            "--drawer", action="store", type=boolarg, default=False,
            help="Create a stackable drawer instead")

    def paintholes(self):
        """Place holes for the paintcans evenly"""

        if self.hexpattern:
            self.moveTo(self.minspace / 2, self.minspace / 2)
            settings = self.hexHolesSettings
            settings.diameter = self.candiameter
            settings.distance = self.minspace
            settings.style = 'circle'
            self.hexHolesRectangle(self.y - 1 * self.minspace,
                                   self.x - 1 * self.minspace,
                                   settings)
            return
        n_x = int(self.x / (self.candiameter + self.minspace))
        n_y = int(self.y / (self.candiameter + self.minspace))

        if n_x <= 0 or n_y <= 0:
            return

        spacing_x = (self.x - n_x * self.candiameter) / n_x
        spacing_y = (self.y - n_y * self.candiameter) / n_y
        for i in range(n_y):
            for j in range(n_x):
                self.hole(i * (self.candiameter + spacing_y) + (self.candiameter + spacing_y) / 2,
                          j * (self.candiameter + spacing_x) + (self.candiameter + spacing_x) / 2,
                          self.candiameter / 2)

    def sidesCb(self):
        x, y = self.x, self.y
        t = self.thickness

        stack = self.edges['s'].settings
        h = self.canheight - stack.height - stack.holedistance + t
        hx = 1 / 2. * x
        hh = h / 4.
        hr = min(hx, hh) / 2

        if not self.drawer:
            self.rectangularHole(h / 3, (x / 2.0) - t, hh, hx, r=hr)
            self.fingerHolesAt(((self.canheight/3)*2)-t*2, -t, x, 90)

            if self.additional_bottom:
                self.fingerHolesAt((self.canheight / 6) - (t / 2), -t, x, 90)
            if self.additional_top:
                self.fingerHolesAt(self.canheight - ((self.canheight / 6) + t), -t, x, 90)
        else:
            self.rectangularHole(h / 3, (x / 2.0) - t, hh, hx, r=hr)

    def render(self):
        # adjust to the variables you want in the local scope
        x, y = self.x, self.y
        t = self.thickness

        stack = self.edges['s'].settings
        h = self.canheight - stack.height - stack.holedistance + t

        wall_callbacks = [self.sidesCb]
        if not self.drawer:
            wall_keys = "EsES"
            bottom_keys = "EfEf"
        else:
            wall_keys = "FsFS"
            bottom_keys = "FfFf"

        # Walls
        self.rectangularWall(
            h, x - 2 * t, wall_keys,
            ignore_widths=[1, 2, 5, 6],
            callback=wall_callbacks, move="up",
        )
        self.rectangularWall(
            h, x - 2 * t, wall_keys,
            ignore_widths=[1, 2, 5, 6],
            callback=wall_callbacks, move="right"
        )

        # Plates
        self.rectangularWall(
            0.8 * stack.height + stack.holedistance, x, "eeee", move=""
        )
        self.rectangularWall(
            0.8 * stack.height + stack.holedistance, x, "eeee", move="down right"
        )

        # Bottom
        self.rectangularWall(
            y, x - 2 * t, bottom_keys, ignore_widths=[1, 2, 5, 6], move="up"
        )

        if not self.drawer:
            # Top
            self.rectangularWall(y, x, "efef", callback=[self.paintholes], move="up")
            if self.additional_bottom:
                self.rectangularWall(y, x, "efef", callback=[self.paintholes], move="up")
            if self.additional_top:
                self.rectangularWall(y, x, "efef", callback=[self.paintholes], move="up")
        else:
            # Sides
            self.rectangularWall(y, h, "efff", move="up")
            self.rectangularWall(y, h, "efff", move="up")
