"""Generator for a split atreus keyboard."""

from copy import deepcopy

from boxes import Boxes, Color, holeCol, restore, boolarg
from boxes.edges import FingerJointSettings


class Atreus21(Boxes):
    """Generator for a split atreus keyboard."""
    ui_group = 'Misc'
    btn_size = 15.6
    btn_outer = btn_size + 3.4
    border = 6

    row_offsets=[3, 6, 11, 5, 0, btn_size * .5]
    row_keys=[4, 4, 4, 4, 4, 1]

    def __init__(self):
        super().__init__()
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

    def render(self):
        """Renders the keypad."""
        # deeper edge for top to add multiple layers
        deep_edge = deepcopy(self.edges['f'].settings)
        deep_edge.thickness = self.thickness + self.top1_thickness
        if self.top2_enable:
            deep_edge.thickness += self.top2_thickness
        deep_edge.edgeObjects(self, 'gGH', True)

        self.moveTo(10, 30)
        case_x, case_y = self._case_x_y()

        self.hole(0, 0, d=0.7)

        for reverse in [False, True]:
            # keyholder
            self.outer()
            self.half(reverse=reverse)
            self.holes()
            self.moveTo(case_x + 13)

            # support
            self.outer()
            self.half(self.support, reverse=reverse)
            self.holes()
            self.moveTo(-case_x - 13, case_y + 13)

            # hotplug
            self.outer()
            self.half(self.hotplug, reverse=reverse)
            self.holes()
            self.moveTo(case_x + 13)

            # border
            self.outer()
            self.rim()
            self.holes()
            self.moveTo(-case_x - 13, case_y + 13)


    def holes(self):
        case_x, case_y = self._case_x_y()
        self.hole(-1.5, -1.5, d=3)
        self.hole(case_x + 1.5, -1.5, d=3)
        self.hole(-1.5, case_y + 1.5, d=3)
        self.hole(case_x + 1.5, case_y + 1.5, d=3)

    def micro(self):
        x = 17.9
        y = 33
        b = self.border
        case_x, case_y = self._case_x_y()
        self.rectangularHole(
            x * -.5 + case_x + b * .5,
            y * -.5 + case_y + b * .5,
            x, y
        )

    def rim(self):
        s = 5
        x, y = self._case_x_y()
        self.moveTo(x * .5, y * .5)
        self.rectangularHole(0, 0, x, y, 5)
        self.moveTo(x * -.5, y * -.5)

    def outer(self):
        x, y = self._case_x_y()
        b = self.border
        self.moveTo(0, -b)
        corner = [90, b]
        self.polyline(*([x, corner, y, corner] * 2))
        self.moveTo(0, b)
    
    def half(self, cb=None, reverse=False):
        row_offsets=self.row_offsets
        row_keys=self.row_keys
        scheme = list(zip(row_offsets, row_keys))
        if reverse:
            scheme.reverse()
        for offset, keys in scheme:
            self.moveTo(0, offset)
            self.key_row(keys, cb)
            self.moveTo(self.btn_outer)
            self.moveTo(0, -offset)

        total_moved_rows = len(row_offsets) * (self.btn_outer)
        self.moveTo(total_moved_rows * -1, 0)

    def key_row(self, n, hole_cb=None):
        """Callback for the key holes."""
        if hole_cb == None:
            hole_cb = self.key
        for _ in range(n):
            hole_cb()
        self.moveTo(0, -n * (self.btn_outer))

    def support(self):
        btn = [11.6, (-90, 2)] * 4
        self.set_source_color(Color.BLUE)
        self.moveTo(0, 2, 90)
        self.polyline(*btn)
        self.moveTo(-2, 0, 270)
        self.moveTo(0, self.btn_outer)
        self.set_source_color(Color.BLACK)

    def hotplug(self):
        self.moveTo(7.8 , 7.8)
        self.hole(0, 0, d=4)
        self.hole(1.27 * -3, 1.27 * 2, d=2.9)
        self.hole(1.27 * 2, 1.27 * 4, d=2.9)

        # pcb mounts
        self.hole(1.27 * -4, 0, d=1.7)
        self.hole(1.27 * 4, 0, d=1.7)

        self.moveTo(-7.8, -7.8)
        self.moveTo(0, self.btn_outer)

    def key(self):
        self.set_source_color(Color.BLUE)

        # draw clock wise to work with burn correction
        btn_half_side = [0.98, 90, 0.81, -90, 3.5, -90, 0.81, 90, 2.505]
        btn_full_side = [*btn_half_side, 0, *btn_half_side[::-1]]
        btn = [*btn_full_side, -90] * 4

        self.moveTo(0.81, 0.81, 90)
        self.polyline(*btn)
        self.moveTo(0, 0, 270)
        self.moveTo(-0.81, -0.81)
        self.moveTo(0, self.btn_outer)

        self.set_source_color(Color.BLACK)

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

    # get case sizes
    def _case_x_y(self):
        x = len(self.row_offsets) * self.btn_outer - 4
        y = sum([
            max(self.row_keys) * self.btn_outer,  # total button sizes
            max(self.row_offsets),  # offset of highest row
            -4,
        ])
        return x, y
