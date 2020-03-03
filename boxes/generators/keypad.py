"""Generator for keypads with mechanical switches."""

from copy import deepcopy

from boxes import Boxes
from boxes.edges import FingerJointSettings


class Keypad(Boxes):
    """Generator for keypads with mechanical switches."""
    ui_group = 'Box'
    btn_size = 15.6
    triangle = 25.

    def __init__(self):
        super().__init__()
        self.argparser.add_argument(
            '--h', action='store', type=int, default=30,
            help='height of the box'
        )
        self.argparser.add_argument(
            '--btn_x', action='store', type=int, default=3,
            help='number of buttons in x-row'
        )
        self.argparser.add_argument(
            '--btn_y', action='store', type=int, default=4,
            help='number of buttons in x-row'
        )
        self.argparser.add_argument(
            '--top_thickness', action='store', type=float, default=1.5,
            help='thickness of the top layer, cherry needs 1.5mm or smaller'
        )
        self.addSettingsArgs(FingerJointSettings, surroundingspaces=1)

    def _get_x_y(self):
        """Gets the keypad's size based on the number of buttons."""
        x = self.btn_x * (self.btn_size) + (self.btn_x - 1) * 4 + 20
        y = self.btn_y * (self.btn_size) + (self.btn_y - 1) * 4 + 20
        return x, y

    def render(self):
        """Renders the keypad."""
        # deeper edge for top to add multiple layers
        deep_edge = deepcopy(self.edges['f'].settings)
        deep_edge.thickness = self.thickness + self.top_thickness
        deep_edge.edgeObjects(self, 'gGH', True)

        d1, d2 = 2., 3.
        x, y = self._get_x_y()
        h = self.h

        # box sides
        self.rectangularWall(x, h, "GFEF", callback=[self.wallx_cb], move="right")
        self.rectangularWall(y, h, "GfEf", callback=[self.wally_cb], move="up")
        self.rectangularWall(y, h, "GfEf", callback=[self.wally_cb])
        self.rectangularWall(x, h, "GFEF", callback=[self.wallx_cb], move="left up")

        # electronics box lid
        self.rectangularWall(x, y, "FFFF", move="right")

        # keypad lids
        self.rectangularWall(x, y, "ffff", callback=[self.support_hole], move="up")
        self.rectangularWall(x, y, "ffff", callback=[self.key_hole])

        # screwable
        tr = self.triangle
        trh = tr / 3
        self.rectangularWall(
            x, y,
            callback=[lambda: self.hole(trh, trh, d=d2)] * 4,
            move='left up'
        )
        self.rectangularTriangle(
            tr, tr, "ffe", num=4,
            callback=[None, lambda: self.hole(trh, trh, d=d1)]
        )


    def support_hole(self):
        """Callback for the key stabelizers."""
        # draw clock wise to work with burn correction
        btn = [11.6, (-90, 2)] * 4

        s = self.btn_size
        self.moveTo(10, 10)
        for _ in range(self.btn_y):
            for _ in range(self.btn_x):
                self.moveTo(0, 2, 90)
                self.polyline(*btn)
                self.moveTo(0, 0, 270)
                self.moveTo(s + 4, -2)
            self.moveTo(self.btn_x * (s + 4) * -1, s + 4)

    def key_hole(self):
        """Callback for the key holes."""
        # draw clock wise to work with burn correction
        btn_half_side = [0.98, 90, 0.81, -90, 3.5, -90, 0.81, 90, 2.505]
        btn_full_side = [*btn_half_side, 0, *btn_half_side[::-1]]
        btn = [*btn_full_side, -90] * 4

        s = self.btn_size
        self.moveTo(10, 10)
        for _ in range(self.btn_y):
            for _ in range(self.btn_x):
                self.moveTo(0.81, 0.81, 90)
                self.polyline(*btn)
                self.moveTo(0, 0, 270)
                self.moveTo(-0.81, -0.81)
                self.moveTo(s + 4)
            self.moveTo(self.btn_x * (s + 4) * -1, s + 4)

    # stolen form electronics-box
    def wallx_cb(self):
        """Callback for triangle holes on x-side."""
        x, _ = self._get_x_y()
        t = self.thickness
        self.fingerHolesAt(0, self.h - 1.5 * t, self.triangle, 0)
        self.fingerHolesAt(x, self.h - 1.5 * t, self.triangle, 180)

    # stolen form electronics-box
    def wally_cb(self):
        """Callback for triangle holes on y-side."""
        _, y = self._get_x_y()
        t = self.thickness
        self.fingerHolesAt(0, self.h - 1.5 * t, self.triangle, 0)
        self.fingerHolesAt(y, self.h - 1.5 * t, self.triangle, 180)
