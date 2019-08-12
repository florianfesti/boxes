"""Half 19inch rack unit for musical equipment."""

from boxes import Boxes
from boxes.edges import Edge

class H19Rack(Boxes):
    """Half 19inch rack unit for musical equipment."""
    ru_count = 1
    holes = "xxmpwx"
    z = 20
    deepz = 124
    earside = 'r'

    # provided by default via boxes
    x, y, = 0, 0
    thickness = 3

    def __init__(self):
        super().__init__()
        self.argparser.add_argument(
            '--ru_count', action='store', type=float, default=self.ru_count,
            help='number of rack units')
        self.argparser.add_argument(
            '--holes', action='store', type=str, default=self.holes,
            help='holes, x=xlr, m=midi, p=9v-power, w=6.5mm-wire')
        self.argparser.add_argument(
            '--z', action='store', type=float, default=self.z,
            help='depth of the shorter (rackear) side')
        self.argparser.add_argument(
            '--deepz', action="store", type=float, default=self.deepz,
            help='depath of the longer (screwed to another half sized thing) side')

    def render(self):
        """Render box."""
        # pylint: disable=invalid-name
        t = self.thickness
        z = self.z
        self.x = x = 223 - (2 * t)
        self.y = y = (self.ru_count * 44.45) - 4.45 - (2 * t)
        deepz = self.deepz

        # front
        self.flangedWall(x, y, "FFFF", callback=[self.util_holes, self.rack_holes], r=t,
                         flanges=[0, 17, 0, 0], move="up")

        # top&bottom
        self.trapezoidWall(x, deepz, z, "fFeF", move="up")
        self.trapezoidWall(x, deepz, z, "fFeF", move="up")

        # side
        self.rectangularWall(deepz, y, "fffe", move="right")
        self.rectangularWall(z, y, "fffe", move="up")

    def rack_holes(self):
        """Rackmount holes."""
        t = self.thickness # pylint: disable=invalid-name
        self.rectangularHole(6 + t, 10, 10, 6.5, r=3.25)
        self.rectangularHole(self.y - 6 + t, 10, 10, 6.5, r=3.25)

    def util_holes(self):
        """Add holes."""
        self.moveTo(10, self.y / 2 + self.thickness)
        for hole in self.holes:
            self.hole_map.get(hole, lambda _: None)(self)

    def hole_xlr(self):
        """Hole for a xlr port."""
        self.moveTo(16)
        self.hole(-9.5, 12, 1)
        self.hole(0, 0, 11.8)
        self.hole(9.5, -12, 1)
        self.moveTo(16)

    def hole_midi(self):
        """Hole for a midi port."""
        self.moveTo(17)
        self.hole(-11.1, 0, 1)
        self.hole(0, 0, 7.5)
        self.hole(11.1, 0, 1)
        self.moveTo(17)

    def hole_power(self):
        """Hole for a 9v power port."""
        self.moveTo(11)
        self.rectangularHole(0, 0, 9, 11)
        self.moveTo(11)

    def hole_wire(self):
        """Hole for a wire."""
        self.moveTo(3)
        self.hole(0, 0, 3.25)
        print('hi')
        self.moveTo(3)

    hole_map = {
        'm': hole_midi,
        'p': hole_power,
        'w': hole_wire,
        'x': hole_xlr,
    }
