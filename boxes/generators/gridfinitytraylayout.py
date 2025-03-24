import argparse

import boxes
from boxes import Boxes, lids, restore, boolarg
from boxes.Color import Color
from boxes.generators.traylayout import TrayLayout


class GridfinityTrayLayout(TrayLayout):
    """A Gridfinity Tray Generator based on TrayLayout"""

    description = """
This is a general purpose gridfinity tray generator.  You can create
somewhat arbitrarily shaped trays, or just do nothing for simple grid
shaped trays.

The dimensions are automatically calculated to fit perfectly into a
gridfinity grid (like the GridfinityBase, or any other Gridfinity
based base).

Edit the layout text graphics to adjust your tray.
You can replace the hyphens and vertical bars representing the walls
with a space character to remove the walls.  You can replace the space
characters representing the floor by a "X" to remove the floor for
this compartment.
"""
    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(boxes.edges.FingerJointSettings)
        self.addSettingsArgs(lids.LidSettings)
        self.outside = True # We're *always* outside for gridfinity
        self.pitch = 42.0 # gridfinity pitch is defined as 42.
        self.opening = 38
        self.opening_margin = 2
        self.argparser.add_argument("--h", type=str, default="50", help="height in mm or add 'u' at the end for Gridfinity units")
        self.argparser.add_argument("--hi", type=float, default=0, help="inner height of inner walls in mm (leave to zero for same as outer walls with optional reduction for stacking)")
        self.argparser.add_argument("--nx", type=int, default=3, help="number of gridfinity grids in X direction")
        self.argparser.add_argument("--ny", type=int, default=2, help="number of gridfinity grids in Y direction")
        self.argparser.add_argument("--countx", type=int, default=5, help="split x into this many grid sections.  0 means same as --nx")
        self.argparser.add_argument("--county", type=int, default=3, help="split y into this many grid sections.  0 means same as --ny")
        self.argparser.add_argument("--margin", type=float, default=0.75, help="Leave this much total margin on the outside, in mm")
        self.argparser.add_argument("--stacking", action="store", type=boolarg, default=False, help="support gridfinity compatible stacking")
        self.argparser.add_argument("--gen_pads", type=boolarg, default=True, help="generate pads to be used on the bottom of the box")
        self.argparser.add_argument("--pad_radius", type=float, default=0.8, help="The corner radius for each grid opening.  Typical is 0.8,")
        self.argparser.add_argument("--cut_pads_mag_diameter", type=float, default=6.5, help="if pads are cut add holes for magnets. Typical is 6.5, zero to disable,")
        self.argparser.add_argument("--cut_pads_mag_offset", type=float, default=7.75, help="if magnet hole offset from pitch corners.  Typical is 7.75.")
        if self.UI == "web":
            self.argparser.add_argument("--layout", type=str, help="You can hand edit this before generating", default="\n");
        else:
            self.argparser.add_argument(
                "--input", action="store", type=argparse.FileType('r'),
                default="traylayout.txt",
                help="layout file")
            self.layout = None

    def generate_layout(self):
        layout = ''
        countx = self.countx
        county = self.county
        if countx == 0:
            countx = self.nx
        if county == 0:
            county = self.ny

        stepx = self.x / countx
        stepy = self.y / county
        for i in range(countx):
            line = ' |' * i + f" ,> {stepx}mm\n"
            layout += line
        for i in range(county):
            layout += "+-" * countx + f"+\n"
            layout += "| " * countx + f"|{stepy}mm\n"
        layout += "+-" * countx + "+\n"
        return layout

    @restore
    def rectangularEtching(self, x, y, dx, dy, r=0, center_x=True, center_y=True):
        """
        Draw a rectangular hole

        :param x: x position
        :param y: y position
        :param dx: width
        :param dy: height
        :param r:  (Default value = 0) radius of the corners
        :param center_x:  (Default value = True) if True, x position is the center, else the start
        :param center_y:  (Default value = True) if True, y position is the center, else the start
        """
        r = min(r, dx/2., dy/2.)
        x_start = x if center_x else x + dx / 2.0
        y_start = y - dy / 2.0 if center_y else y
        self.moveTo(x_start, y_start, 180)
        self.edge(dx / 2.0 - r) # start with an edge to allow easier change of inner corners
        for d in (dy, dx, dy, dx / 2.0 + r):
            self.corner(-90, r)
            self.edge(d - 2 * r)

    def baseplate_etching(self):
        x = -self.thickness - self.margin / 2
        y = -self.thickness - self.margin / 2
        o = self.opening
        p = self.pitch
        m = self.opening_margin
        self.ctx.stroke()
        with self.saved_context():
            for xx in [0, self.nx-1]:
                for yy in [0, self.ny-1]:
                    self.set_source_color(Color.ETCHING)
                    self.rectangularEtching(x+p/2+xx*p, y+p/2+yy*p, o-m, o-m)
            self.ctx.stroke()

    def generatePad(self, x, y, r=0, move=None):
        """
        Draw a rectangular pad with radius edge

        :param x: x position
        :param y: y position
        :param r:  (Default value = 0) radius of the corners
        :param move:  (Default value = None)
        """
        if self.move(x, y, move, before=True):
            return

        r = min(r, x/2., y/2.)
        with self.saved_context():
            self.moveTo(x / 2, 0)
            self.edge(x / 2 - r) # start with an edge to allow easier change of inner corners
            for d in (y, x, y, x / 2.0 + r):
                self.corner(90, r)
                self.edge(d - 2 * r)

        self.moveTo(x/2, y/2)
        if self.cut_pads_mag_diameter > 0:
            # create a shorter variable names for use in the loop
            ofs = self.cut_pads_mag_offset
            dia = self.cut_pads_mag_diameter
            for xoff, yoff in ((1,1), (-1,1), (1,-1), (-1,-1)):
                hole_x = ((self.pitch // 2)-ofs)*xoff
                hole_y = ((self.pitch // 2)-ofs)*yoff
                self.hole(hole_x, hole_y, d=dia)

        self.move(x, y, move)

    def render(self):
        # Create a layout
        self.x = self.pitch * self.nx - self.margin
        self.y = self.pitch * self.ny - self.margin
        self.outer_x = self.x
        self.outer_y = self.y

        if self.h.isdigit():
            self.h = float(self.h)
        elif self.h.upper().endswith("U"):
            # gridfinity box units are 7mm, *inclusive* of the pad at the bottom, but most
            # people print their boxes with the stacking lip at the top which adds to the
            # total height of 4.4 mm (if using a pointed stacking lip) or approximately
            # 3.69mm if using a rounded R0.5 lip (see
            # https://www.printables.com/model/417152-gridfinity-specification).
            #
            # The gridfinity specification expects the wall thickness to be 2.15mm, but
            # the a common laser cutting thickness is 3mm, so it's not possible to
            # stack 3d printed gridfinity boxes on top of laser cut boxes or bases. You can
            # stack laser cut boxes on top of the 3d printed boxes. You can also mix laser
            # cut boxes and 3d printed boxes on a laser cut base.
            #
            # The goal of the above code is that a stack of laser cut boxes and a stack
            # of 3d printed boxes will end up the same total height

            self.h = (int(self.h[0:-1]) * 7) - self.thickness

            if self.stacking:
                self.h += 3.69
        else:
            raise ValueError("--h must be a number or a number followed by 'u'")

        if not self.hi and self.stacking:
            self.hi = self.h - 4.4

        self.prepare()
        self.walls()
        with self.saved_context():
            self.base_plate(callback=[self.baseplate_etching],
                            move="mirror right")
            if self.gen_pads:
                foot = self.opening - self.opening_margin
                for i in range(min(self.nx * self.ny, 4)):
                    self.generatePad(foot, foot, move="right", r=self.pad_radius)
        self.base_plate(callback=[self.baseplate_etching],
                        move="up only")
        self.lid(sum(self.x) + (len(self.x)-1) * self.thickness,
                 sum(self.y) + (len(self.y)-1) * self.thickness)
