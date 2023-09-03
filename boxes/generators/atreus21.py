"""Generator for a split atreus keyboard."""

from boxes import Boxes, restore
from .keyboard import Keyboard


class Atreus21(Boxes, Keyboard):
    """Generator for a split atreus keyboard."""
    ui_group = 'Misc'
    btn_size = 15.6
    half_btn = btn_size / 2
    border = 6

    def __init__(self) -> None:
        super().__init__()
        self.add_common_keyboard_parameters(
            # By default, columns from Atreus 21
            default_columns_definition=f'4@3/4@6/4@11/4@5/4@0/1@{self.btn_size * 0.5}'
        )

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

    @restore
    def rim(self):
        x, y = self._case_x_y()
        self.moveTo(x * .5, y * .5)
        self.rectangularHole(0, 0, x, y, 5)

    @restore
    def outer(self):
        x, y = self._case_x_y()
        b = self.border
        self.moveTo(0, -b)
        corner = [90, b]
        self.polyline(*([x, corner, y, corner] * 2))

    @restore
    def half(self, hole_cb=None, reverse=False):
        if hole_cb is None:
            hole_cb = self.key
        self.moveTo(self.half_btn, self.half_btn)
        self.apply_callback_on_columns(
            hole_cb,
            self.columns_definition,
            reverse=reverse,
        )

    def support(self):
        self.configured_plate_cutout(support=True)

    def hotplug(self):
        self.pcb_holes(
            with_hotswap=self.hotswap_enable,
            with_pcb_mount=self.pcb_mount_enable,
            with_diode=self.diode_enable,
            with_led=self.led_enable,
        )

    def key(self):
        self.configured_plate_cutout()

    # get case sizes
    def _case_x_y(self):
        spacing = Keyboard.STANDARD_KEY_SPACING
        margin = spacing - self.btn_size
        x = len(self.columns_definition) * spacing - margin
        y = max(offset + keys * spacing for (offset, keys) in self.columns_definition) - margin
        return x, y
