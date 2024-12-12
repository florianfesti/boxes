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

class WallHopperEdge(edges.BaseEdge):
    # Character used to identify this edge type in wall specifications
    char = "j"

    def __call__(self, length, **kw):

        # Get configuration from settings
        dd = self.settings.dispenser_depth
        dh = self.settings.dispenser_height
        a = self.settings.slope_angle     # Base angle for slope
        sr = self.settings.slope_ratio if self.slope_ratio < 1 else 0.999 # Fraction of height for front slope
        lr = self.settings.label_ratio if self.label_ratio < 1 else 0.999 # Fraction of height for label
        label = self.settings.label     # Whether to include label area
        h = self.settings.h        # Total height of bin

        # Check that sa generates a valid dispenser
        minsa = 0 # 0 degrees is a flat front
        maxsa = math.degrees(math.atan(dd/(dh*sr))) # equivalent to no flat section on the dispenser
        if a < minsa:
            a = minsa
        elif a > maxsa:
            a = maxsa

        # Check that ratios are valid
        if not self.label:
            lr = 0
        if sr + lr >= 0.95:
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

        # Draw the edge profile sequence:
        self.corner(-90)
        self.edges["e"](-df)
        self.corner(90)
        self.edges["f"](h-dh)
        self.corner(-b)
        self.edges["e"](tl)
        self.corner(b)
        self.edges["f"](lr*dh)
        self.corner(a)
        self.edges["f"](sl)
        self.corner(-a)


    def margin(self) -> float:
        # Calculate the margin required for this edge type
        # Same calculation as width of slope projection
        # Add material thickness if a label area is included
        t = self.settings.thickness if self.settings.label else 0
        return (self.settings.dispenser_height * self.settings.slope_ratio) * math.tan(math.radians(self.settings.slope_angle)) + t

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

        self.buildArgParser(x=80, h=150)

        self.argparser.add_argument(
            "--hopper_depth",  action="store", type=float, default=60,
            help="Depth of the hopper")
        self.argparser.add_argument(
            "--dispenser_depth",  action="store", type=float, default=50,
            help="Depth of the dispenser")
        self.argparser.add_argument(
            "--dispenser_height",  action="store", type=float, default=70,
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


    def render(self):
        self.generateWallEdges() # creates the aAbBcCdD| edges

        # Add custom edge for the front profile
        self.addPart(WallHopperEdge(self, self))

        hd = self.hopper_depth
        dd = self.dispenser_depth
        dh = self.dispenser_height
        sr = self.slope_ratio if self.slope_ratio < 1 else 0.999
        a = self.slope_angle
        lr = self.label_ratio if self.label_ratio < 1 else 0.999

        x = self.x
        h = self.h

        # Check that sa generates a valid dispenser
        minsa = 0 # 0 degrees is a flat front
        maxsa = math.degrees(math.atan(dd/(dh*sr))) # equivalent to no flat section on the dispenser
        if a < minsa:
            a = minsa
        elif a > maxsa:
            a = maxsa

        wh = self.edges["h"].startwidth()

        # Check that ratios are valid
        if not self.label:
            lr = 0
        if sr + lr >= 0.95:
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
            self.rectangularWall(x, hd+df, "ffGf", label="bottom", move="up")

            if self.label:
                # Sloped front with label area
                self.rectangularWall(x, sl,
                                   "gfkf", label="slope", move="up")
                # Label panel
                self.rectangularWall(x, dh*lr,
                                   "Kfef", label="label", move="up")
            else:
                # Sloped front without label
                self.rectangularWall(x, sl,
                                   "gfef", label="slope", move="up")
            # Back panel with wall mount edges
            self.rectangularWall(x, h, "hCec", label="back", move="up")
            # Front panel of hopper
            self.rectangularWall(x, h-dh, "efef", label="front", move="up")

        # Non drawn spacer to move wall pieces to the right
        self.rectangularWall(self.x, 3, "DDDD", label="movement", move="right only")

        # This one doesn't work, as it's not applying compensation to the
        # dimensions to account for the 'h' edge, also the finger joints
        # for the top of the hopper are slightly off for some reason
        self.polygonWall([
            hd+df, (90-a, wh),
            sl, (a, wh),
            dh*lr, b,
            tl, -b,
            h-dh, 90,
            hd+wh, 90,
            h, 0,
            wh, 90,
            ],
            "hhhehebe",correct_corners=False, label="left", move="up", )

        # This one works, but it generates a thin line that I don't want
        # and don't know how to get rid of
        self.rectangularWall(hd+df,h, "hBej", label="right", move="up")
