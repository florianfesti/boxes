"""Generator for keypads with mechanical switches."""

from copy import deepcopy

from boxes import Boxes, boolarg
from boxes.edges import FingerJointSettings
from .keyboard import Keyboard


class Keypad(Boxes, Keyboard):
    """Generator for keypads with mechanical switches."""
    ui_group = 'Box'
    btn_size = 15.6
    space_between_btn = 4
    box_padding = 10
    triangle = 25.0

    def __init__(self):
        super().__init__()
        self.argparser.add_argument(
            '--h', action='store', type=int, default=30,
            help='height of the box'
        )
        self.argparser.add_argument(
            '--btn_x', action='store', type=int, default=3,
            help='number of buttons per row'
        )
        self.argparser.add_argument(
            '--btn_y', action='store', type=int, default=4,
            help='number of buttons per column'
        )
        self.argparser.add_argument(
            '--top1_thickness', action='store', type=float, default=1.5,
            help=('thickness of the button hold layer, cherry like switches '
                  'need 1.5mm or smaller to snap in')
        )
        self.argparser.add_argument(
            '--top2_enable', action='store', type=boolarg, default=False,
            help=('enables another top layer that can hold CPG151101S11 '
                  'sockets')
        )
        self.argparser.add_argument(
            '--top2_thickness', action='store', type=float, default=1.5,
            help=('thickness of the hotplug layer, CPG151101S11 sockets '
                  'need 1.2mm to 1.5mm')
        )
        self.addSettingsArgs(FingerJointSettings, surroundingspaces=1)

    def _get_x_y(self):
        """Gets the keypad's size based on the number of buttons."""
        x = self.btn_x * (self.btn_size) + (self.btn_x - 1) * self.space_between_btn + 2*self.box_padding
        y = self.btn_y * (self.btn_size) + (self.btn_y - 1) * self.space_between_btn + 2*self.box_padding
        return x, y

    def render(self):
        """Renders the keypad."""
        # deeper edge for top to add multiple layers
        deep_edge = deepcopy(self.edges['f'].settings)
        deep_edge.thickness = self.thickness + self.top1_thickness
        if self.top2_enable:
            deep_edge.thickness += self.top2_thickness
        deep_edge.edgeObjects(self, 'gGH', True)

        d1, d2 = 2., 3.
        x, y = self._get_x_y()
        h = self.h

        # box sides
        self.rectangularWall(x, h, "GFEF", callback=[self.wallx_cb], move="right")
        self.rectangularWall(y, h, "GfEf", callback=[self.wally_cb], move="up")
        self.rectangularWall(y, h, "GfEf", callback=[self.wally_cb])
        self.rectangularWall(x, h, "GFEF", callback=[self.wallx_cb], move="left up")

        # keypad lids
        self.rectangularWall(x, y, "ffff", callback=self.to_grid_callback(self.support_hole), move="right")
        self.rectangularWall(x, y, "ffff", callback=self.to_grid_callback(self.key_hole), move="up")
        if self.top2_enable:
            self.rectangularWall(x, y, "ffff", callback=self.to_grid_callback(self.hotplug))

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

    def to_grid_callback(self, inner_callback):
        scheme = [(0, self.btn_y)]*self.btn_x
        def callback():
            # move to first key center
            key_margin = self.box_padding + self.btn_size / 2
            self.moveTo(key_margin, key_margin)
            self.apply_callback_on_columns(
                inner_callback, scheme, self.btn_size + self.space_between_btn
            )

        return [callback]

    def hotplug(self):
        """Callback for the key stabelizers."""
        self.pcb_holes()

    def support_hole(self):
        self.outer_hole()

    def key_hole(self):
        self.castle_shaped_plate_cutout()

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
