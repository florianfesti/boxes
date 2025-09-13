# Copyright (C) 2024 Alex Roberts
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
from boxes.walledges import _WallMountedBox

class WallHopper(_WallMountedBox):
    """Storage hopper with dispensing tray"""

    description = '''
####Assembly Notes:
1. The generator produces three pieces with angled finger joints.
Bottom panel, sloped front panel and label panel (if enabled).
2. Joint lengths vary to accommodate the slope angles.
3. Orient pieces as shown in the generated layout to assemble correctly.
'''
    def __init__(self) -> None:
        super().__init__()

        self.buildArgParser(sx="80", h=150)

        self.argparser.add_argument(
            "--hopper_depth",  action="store", type=float, default=50,
            help="Depth of the hopper")
        self.argparser.add_argument(
            "--dispenser_depth",  action="store", type=float, default=45,
            help="Depth of the dispenser")
        self.argparser.add_argument(
            "--dispenser_height",  action="store", type=float, default=50,
            help="Height of the dispenser")
        self.argparser.add_argument(
            "--slope_ratio",  action="store", type=float, default=0.4,
            help="Fraction of the bottom slope of the dispenser")
        self.argparser.add_argument(
            "--slope_angle",  action="store", type=float, default=30,
            help="Angle of the bottom slope of the dispenser")
        self.argparser.add_argument(
            "--label", action="store", type=boolarg, default=True,
            help="include a label area on the front")
        self.argparser.add_argument(
            "--label_ratio",  action="store", type=float, default=0.2,
            help="Fraction of the label of the dispenser")

    def wallCB(self, sx, l, wall=False):
        def CB():
            t = self.thickness
            posx = -0.5*t
            for x in sx[:-1]:
                posx += x + t
                if wall:
                    self.wallHolesAt(posx, 0, l, 90)
                else:
                    self.fingerHolesAt(posx, 0, l, 90)
        return CB

    def render(self):
        self.generateWallEdges() # creates the aAbBcCdD| edges

        hd = self.hopper_depth
        dd = self.dispenser_depth
        dh = self.dispenser_height
        sr = self.slope_ratio if self.slope_ratio < 1 else 0.999
        a = self.slope_angle
        lr = self.label_ratio if self.label_ratio < 1 else 0.999
        t = self.thickness

        x = sum(self.sx) + self.thickness * (len(self.sx) - 1)
        h = self.h

        # Check that sa generates a valid dispenser
        minsa = 0 # 0 degrees is a flat front
        maxsa = math.degrees(math.atan(dd/(dh*sr))) # equivalent to no flat section on the dispenser
        if a < minsa:
            a = minsa
        elif a > maxsa:
            a = maxsa

        # Get the width of the 'h' edge
        wh = self.edges["h"].startwidth()

        # Check that ratios are valid
        if not self.label:
            lr = 0
        if sr + lr >= 1: # Check you haven't put in invalid values
            # Scale proportionally to sum to 0.95
            total = sr + lr
            sr = (sr / total) * 0.95  # Scale to 95%
            lr = (lr / total) * 0.95  # Scale to 95%

        # Calculate angle between label and return to dispenser
        b = math.degrees(math.atan(dd/((1-(lr+sr))*dh)))

        # Dispenser flat is dispenser depth minus the slope
        df = dd - dh*sr*math.tan(math.radians(a))

        # Calculate the length of the slope
        sl = dh*sr/math.cos(math.radians(a))

        # calculate the length of the top slope
        tl = (dd**2 + ((1-(lr+sr))*dh)**2)**0.5

        # Configure angled finger joints for the sloped sections
        # First set: For bottom-to-slope connection
        angledsettings = copy.deepcopy(self.edges["f"].settings)
        angledsettings.setValues(self.thickness, True, angle=90-a)
        angledsettings.edgeObjects(self, chars="gG")

        # Second set: For slope-to-label connection
        angledsettings = copy.deepcopy(self.edges["f"].settings)
        angledsettings.setValues(self.thickness, True, angle=a)
        angledsettings.edgeObjects(self, chars="kK")


        with self.saved_context():
            # Bottom panel with finger joints
            self.rectangularWall(x, hd+df, "ffGf",
                                 callback=[self.wallCB(self.sx, hd+df)],
                                 label="bottom", move="up")

            if self.label:
                # Sloped front with label area
                self.rectangularWall(x, sl, "gfkf",
                                     callback=[self.wallCB(self.sx, sl)],
                                     label="slope", move="up")
                # Label panel
                self.rectangularWall(x, dh*lr, "Kfef",
                                     callback=[self.wallCB(self.sx, dh*lr)],
                                     label="label", move="up")
            else:
                # Sloped front without label
                self.rectangularWall(x, sl, "gfef",
                                     callback=[self.wallCB(self.sx, sl)],
                                     label="slope", move="up")
            # Back panel with wall mount edges
            self.rectangularWall(x, h, "hCec",
                                 callback=[self.wallCB(self.sx, h, True)],
                                 label="back", move="up")
            # Front panel of hopper
            self.rectangularWall(x, h-dh, "efef",
                                 callback=[self.wallCB(self.sx, h-dh)],
                                 label="front", move="up")

        # Non drawn spacer to move wall pieces to the right
        self.rectangularWall(x, 3, "DDDD", label="movement", move="right only")


        sideEdges = [
            t, 0,                # nudge along by thickness
            hd+df, (90-a, wh),   # hopper depth + dispenser flat, then rotate slope angle with a radius of an 'h' edge
            sl, (a, wh),         # slope length, then rotate back to vertical with a radius of an 'h' edge
            dh*lr, b,            # label height, then rotate to the angle between label and dispenser
            tl, -b,              # top slope length, then rotate back to vertical
            h-dh, 90,            # Additional hopper height, then rotate to horizontal
            hd+wh+t, 90,         # Hopper depth + 'h' edge width + thickness, then rotate to vertical
            h, 0,                # Wall edge to the bottom
            wh, 90,              # Width of an 'h' edge to close the box
            ]


        self.polygonWall(sideEdges, "ehhhehebe",correct_corners=False, label="left", move="up")
        self.polygonWall(sideEdges, "ehhhehebe",correct_corners=False, label="right", move="up mirror")
        for i in range(len(self.sx)-1):
            self.polygonWall(sideEdges, "efffefebe",correct_corners=False, label="divider", move="up")
