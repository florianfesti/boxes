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

class StackableBinEdge(edges.BaseEdge):
    # Character used to identify this edge type in wall specifications
    char = "j"

    def __call__(self, length, **kw):
        # ASCII art showing edge profile geometry:
        #               _
        #               |                  /
        #               |                / b  <- Angle between vertical and hyp2
        #               |              /
        #               |      hyp2  /        <- Upper hypotenuse length
        #               |          /
        #               |        /
        #    _          |      /
        #    |          |     |
        #    |          |     |
        #    l          h     |              <- Total height
        #    |          |     |
        #    _    _     |     | ---- w ----  <- Width of slope projection
        #         |     |       \
        #         |     |         \
        #         f     |      hyp1 \        <- Lower hypotenuse length
        #         |     |             \
        #         |     |               \ a   <- Base angle from settings
        #         _     _                 \

        # Get configuration from settings
        a = self.settings.angle     # Base angle for slope
        f = self.settings.front     # Fraction of height for front slope
        l = self.settings.label_height  # Fraction of height for label
        label = self.settings.label     # Whether to include label area
        h = self.settings.h        # Total height of bin

        # If label is disabled, set label height to 0
        if not label:
            l = 0

        # Calculate key dimensions:
        w = (h * f) * math.tan(math.radians(a))      # Width of slope projection
        hyp1 = (h * f) / math.cos(math.radians(a))   # Length of lower slope
        hyp2 = math.sqrt(w**2 + ((1-(l+f))*h)**2)    # Length of upper slope
        b = math.degrees(math.atan(w/((1-l-f)*h)))   # Angle between vertical and hyp2

        # Draw the edge profile sequence:
        self.corner(-b)                           # Rotate to start upper diagonal
        self.edges["e"](hyp2)                     # Draw upper diagonal section
        self.corner(b)                            # Return to vertical
        self.edges["f"](l*h)                      # Draw label section if enabled
        self.corner(a)                            # Rotate to lower diagonal
        self.edges["f"](hyp1)                     # Draw lower diagonal section
        self.corner(-a)                           # Return to horizontal

    def margin(self) -> float:
        # Calculate the margin required for this edge type
        # Same calculation as width of slope projection
        # Add material thickness if a label area is included
        t = self.settings.thickness if self.settings.label else 0
        return (self.settings.h * self.settings.front) * math.tan(math.radians(self.settings.angle)) + t

class WallStackableBin(_WallMountedBox):
    """A wall-mounted bin that can stack or hang from a wall."""
    description = '''
####Features:
- Configurable dimensions (width, height, depth)
- Adjustable front slope angle for easy access
- Optional label area on front face
- Stackable design with interlocking geometry
- Multiple wall mounting options

####Stacking Compatibility:
The stacking mechanism requires careful consideration of wall mounting types.
Bins using "plain" wall mounts can stack on bins with other mount types.
Note: Using the "outside" dimension option is generally not compatible with stacking.

####Assembly Notes:
1. The generator produces three pieces with angled finger joints. 
Bottom panel, sloped front panel and label panel (if enabled).
2. Joint lengths vary to accommodate the slope angles
3. Orient pieces as shown in the generated layout to assemble correctly.
'''
    def __init__(self) -> None:
        super().__init__()

        self.addSettingsArgs(edges.StackableSettings, bottom_stabilizers=2.4)

        self.buildArgParser("outside")
        self.buildArgParser(x=90, h=130, y=150)

        self.argparser.add_argument(
            "--front", action="store", type=float, default=0.3,
            help="fraction of bin height covered with slope")
        self.argparser.add_argument(
            "--angle", action="store", type=float, default=30,
            help="angle of the bottom slope")

        self.argparser.add_argument(
            "--label", action="store", type=boolarg, default=True,
            help="include a label area on the front")
        self.argparser.add_argument(
            "--label_height", action="store", type=float, default=0.2,
            help="fraction of bin height covered with label (if label is enabled)")

    def render(self):
        # Generate standard wall mounting edges (A-D and vertical separator |)
        self.generateWallEdges()

        # Add custom stackable bin edge for the front profile
        self.addPart(StackableBinEdge(self, self))

        # Configure angled finger joints for the sloped sections
        # First set: For bottom-to-slope connection
        angledsettings = copy.deepcopy(self.edges["f"].settings)
        angledsettings.setValues(self.thickness, True, angle=90-self.angle)
        angledsettings.edgeObjects(self, chars="gG")

        # Second set: For slope-to-label connection
        angledsettings = copy.deepcopy(self.edges["f"].settings)
        angledsettings.setValues(self.thickness, True, angle=self.angle)
        angledsettings.edgeObjects(self, chars="kK")

        # Adjust dimensions if outside measurements specified
        if self.outside:
            self.x = self.adjustSize(self.x)
            self.h = self.adjustSize(self.h, "s", "S")
            self.y = self.adjustSize(self.y, "h", "b")

        with self.saved_context():
            # Bottom panel with finger joints
            self.rectangularWall(self.x, self.y, "ffGf", label="bottom", move="up")

            if self.label:
                # Sloped front with label area
                self.rectangularWall(self.x, self.h*self.front/math.cos(math.radians(self.angle)),
                                   "gFkF", label="slope", move="up")
                # Label panel
                self.rectangularWall(self.x, self.h*self.label_height,
                                   "KFeF", label="label", move="up")
            else:
                # Sloped front without label
                self.rectangularWall(self.x, self.h*self.front/math.cos(math.radians(self.angle)),
                                   "gFeF", label="slope", move="up")

            # Back panel with wall mount edges
            self.rectangularWall(self.x, self.h, "hCec", label="back", move="up")

        # Spacer for wall mounting
        self.rectangularWall(self.x, 3, "DDDD", label="movement", move="right only")

        # Side panels with wall mount and stackable edges
        self.rectangularWall(self.y, self.h, "sBSj", label="left side", move="up")
        self.rectangularWall(self.y, self.h, "sBSj", label="right side", move="mirror up")