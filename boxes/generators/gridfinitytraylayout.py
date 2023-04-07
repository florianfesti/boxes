import boxes
from boxes import Boxes
from boxes.generators.traylayout import TrayLayout
from boxes.Color import Color
from boxes import restore, lids

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
        self.buildArgParser(h=50)
        self.outside = True # We're *always* outside for gridfinity
        self.pitch = 42.0 # gridfinity pitch is defined as 42.
        self.opening = 38
        self.opening_margin = 2
        self.argparser.add_argument("--hi", type=float, default=0, help="inner height of inner walls in mm (leave to zero for same as outer walls)")
        self.argparser.add_argument("--nx", type=int, default=3, help="number of gridfinity grids in X direction")
        self.argparser.add_argument("--ny", type=int, default=2, help="number of gridfinity grids in Y direction")
        self.argparser.add_argument("--countx", type=int, default=5, help="split x into this many grid sections.  0 means same as --nx")
        self.argparser.add_argument("--county", type=int, default=3, help="split y into this many grid sections.  0 means same as --ny")
        self.argparser.add_argument("--margin", type=float, default=0.75, help="Leave this much total margin on the outside, in mm")
        self.argparser.add_argument("--layout", type=str, help="You can hand edit this before generating", default="");
        
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

        :param x: position
        :param y: position
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
    
    def render(self):
        # Create a layout
        self.x = self.pitch * self.nx - self.margin
        self.y = self.pitch * self.ny - self.margin
        self.outer_x = self.x
        self.outer_y = self.y

        self.prepare()
        self.walls()
        with self.saved_context():
            self.base_plate(callback=[self.baseplate_etching],
                            move="mirror right")
            foot = self.opening - self.opening_margin
            for i in range(min(self.nx * self.ny, 4)):
                self.rectangularWall(foot, foot, move="right")
        self.base_plate(callback=[self.baseplate_etching],
                        move="up only")
        self.lid(sum(self.x) + (len(self.x)-1) * self.thickness,
                 sum(self.y) + (len(self.y)-1) * self.thickness)
