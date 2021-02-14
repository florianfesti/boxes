"""Generator for a split atreus keyboard."""

from copy import deepcopy

from boxes import Boxes, Color, holeCol, restore, boolarg
from boxes.edges import FingerJointSettings
from .keyboard import Keyboard


class Atreus21(Boxes, Keyboard):
    """Generator for a split atreus keyboard."""
    ui_group = 'Misc'
    btn_size = 15.6
    half_btn = btn_size / 2
    border = 6

    row_offsets=[3, 6, 11, 5, 0, btn_size * .5]
    row_keys=[4, 4, 4, 4, 4, 1]

    def __init__(self):
        super().__init__()

    def render(self):
        """Renders the keyboard."""

        self.moveTo(10, 30)
        case_x, case_y = self._case_x_y()

        margin = 2 * self.border + 1

        for reverse in [False, True]:
            # keyholder
            self.outer()
            self.half(reverse=reverse)
            self.holes()
            self.moveTo(case_x + margin)

            # support
            self.outer()
            self.half(self.support, reverse=reverse)
            self.holes()
            self.moveTo(-case_x - margin, case_y + margin)

            # hotplug
            self.outer()
            self.half(self.hotplug, reverse=reverse)
            self.holes()
            self.moveTo(case_x + margin)

            # border
            self.outer()
            self.rim()
            self.holes()
            self.moveTo(-case_x - margin, case_y + margin)

    def holes(self, diameter=3, margin=1.5):
        case_x, case_y = self._case_x_y()
        for x in [-margin, case_x + margin]:
            for y in [-margin, case_y + margin]:
                self.hole(x, y, d=diameter)

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

    def half(self, hole_cb=None, reverse=False):
        row_offsets=self.row_offsets
        row_keys=self.row_keys
        scheme = list(zip(row_offsets, row_keys))
        if hole_cb == None:
            hole_cb = self.key
        self.moveTo(self.half_btn, self.half_btn)
        self.apply_callback_on_columns(
            hole_cb,
            scheme,
            self.STANDARD_KEY_SPACING,
            reverse,
        )
        self.moveTo(-self.half_btn, -self.half_btn)

    def support(self):
        self.outer_hole()

    def hotplug(self):
        self.pcb_holes()

    def key(self):
        self.castle_shaped_plate_cutout()

    # get case sizes
    def _case_x_y(self):
        margin = self.STANDARD_KEY_SPACING - self.btn_size
        x = len(self.row_offsets) * self.STANDARD_KEY_SPACING - margin
        y = sum([
            max(self.row_keys) * self.STANDARD_KEY_SPACING,  # total button sizes
            max(self.row_offsets),  # offset of highest row
            -margin,
        ])
        return x, y
