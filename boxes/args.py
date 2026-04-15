# Copyright (C) 2026 boxes-acatoire contributors
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

"""Custom argparse types used by Boxes.py generators.

Every class here follows the same pattern that argparse expects for a
*type* converter: it is callable (``__call__`` converts a raw string to
the target Python type) and optionally has an ``html()`` method that the
web server uses to render a custom widget instead of a plain text input.

Quick-reference
---------------
* ``ArgparseEdgeType``  – dropdown of valid edge-type letters
* ``BoolArg`` / ``boolarg``  – checkbox  (``type=boolarg``)
* ``FloatStepper(step)``  – text input with −/+ buttons, returns ``float``
* ``IntStepper(step)``   – text input with −/+ buttons, returns ``int``

All four are re-exported through ``boxes.__init__`` so generators that do
``from boxes import *`` get them automatically.
"""
from __future__ import annotations

from typing import Any
from xml.sax.saxutils import quoteattr

from . import edges as _edges


class ArgparseEdgeType:
    """argparse type to select from a set of edge types"""

    names = _edges.getDescriptions()
    edges: list[str] = []

    def __init__(self, edges: str | None = None) -> None:
        if edges:
            self.edges = list(edges)

    def __call__(self, pattern: str) -> str:
        if len(pattern) != 1:
            raise ValueError("Edge type can only have one letter.")
        if pattern not in self.edges:
            raise ValueError("Use one of the following values: " +
                             ", ".join(self.edges))
        return pattern

    def html(self, name: str, default: str, translate: Any) -> str:
        options = "\n".join(
            """<option value="%s"%s>%s</option>""" %
            (e, ' selected="selected"' if e == default else "",
             translate("{} {}".format(e, self.names.get(e, "")))) for e in self.edges)
        return """<select name="{}" id="{}" aria-labeledby="{} {}" size="1">\n{}</select>\n""".format(
            name, name, name + "_id", name + "_description", options)

    def inx(self, name: str, viewname: str, arg: Any) -> str:
        return (
            '        <param name="%s" type="optiongroup" appearance="combo" gui-text="%s" gui-description=%s>\n' %
            (name, viewname, quoteattr(arg.help or "")) +
            ''.join('            <option value="{}">{} {}</option>\n'.format(
                e, e, self.names.get(e, ""))
                    for e in self.edges) +
            '      </param>\n')


class BoolArg:
    """argparse type rendered as a checkbox in the web UI."""

    def __call__(self, arg: str) -> bool:
        if not arg or arg.lower() in ("none", "0", "off", "false"):
            return False
        return True

    def html(self, name: str, default: str | bool, _: Any) -> str:
        if isinstance(default, str):
            default = self(default)
        return (
            """<input name="%s" type="hidden" value="0">\n"""
            """<input name="%s" id="%s" aria-labeledby="%s %s" type="checkbox" value="1"%s>""" %
            (name, name, name, name + "_id", name + "_description",
             ' checked="checked"' if default else "")
        )


#: Singleton instance – pass as ``type=boolarg`` to ``add_argument``.
boolarg = BoolArg()


class FloatStepper:
    """Argparse type that adds −/+ stepper buttons to any float parameter in the web UI.

    Usage – replace ``type=float`` with ``type=FloatStepper(step)``::

        self.argparser.add_argument(
            "--my_param", action="store", type=FloatStepper(0.5), default=10.0,
            help="My parameter [mm]")

    ``step`` controls how much each button click changes the value (default: 1.0).

    ``auto_default`` – when the field shows ``"auto"`` and +/− is clicked the
    stepper jumps to ``auto_default ± step`` rather than ``0 ± step``.

    ``auto`` – when ``True`` an **Auto** button is rendered to the right of the
    − button.  Clicking it writes ``"auto"`` into the field (the Python type
    converter returns ``None`` for that string).  The argparse default should
    be ``None`` when this mode is used.

    The value is stored as a plain ``float`` (or ``None`` when auto is active).
    """

    def __init__(self, step: float = 1.0,
                 auto_default: float | None = None,
                 auto: bool = False) -> None:
        self.step = step
        self.auto_default = auto_default
        self.auto = auto

    def __call__(self, s: str) -> float | None:
        if s.strip().lower() == "auto":
            return None
        return float(s)

    def html(self, name: str, default: str | float | None, translate: Any) -> str:
        step = self.step
        auto_arg = f", {self.auto_default}" if self.auto_default is not None else ""
        display = "auto" if default is None else str(default)
        auto_btn = (
            f'<button type="button" class="stepper-btn stepper-auto"'
            f' onclick="setInputAuto(\'{name}\')">auto</button>'
        ) if self.auto else ""
        return (
            f'<span class="stepper-wrap">'
            f'{auto_btn}'
            f'<button type="button" class="stepper-btn"'
            f' onclick="stepInput(\'{name}\', -{step}{auto_arg})">&#8722;</button>'
            f'<input name="{name}" id="{name}" class="stepper-input"'
            f' aria-labeledby="{name}_id {name}_description"'
            f' type="text" value="{display}">'
            f'<button type="button" class="stepper-btn"'
            f' onclick="stepInput(\'{name}\', {step}{auto_arg})">+</button>'
            f'</span>'
        )


class DPadArg:
    """Argparse type rendered as a d-pad (cross) of radio buttons in the web UI.

    Choices are rendered as five buttons arranged in a plus-sign layout::

              [ ↑ top ]
        [ ← left ] [ · center ] [ right → ]
              [ ↓ bottom ]
    """

    _GLYPHS: dict[str, str] = {
        "top":    "↑",
        "left":   "←",
        "center": "·",
        "right":  "→",
        "bottom": "↓",
    }
    _GRID: dict[str, tuple[int, int]] = {
        "top":    (2, 1),
        "left":   (1, 2),
        "center": (2, 2),
        "right":  (3, 2),
        "bottom": (2, 3),
    }

    def __init__(self, choices: tuple[str, ...] | list[str]) -> None:
        self.choices: list[str] = list(choices)

    def __call__(self, value: str) -> str:
        if value not in self.choices:
            raise ValueError(f"Invalid d-pad choice {value!r}. "
                             f"Use one of: {', '.join(self.choices)}")
        return value

    def html(self, name: str, default: str, _: Any) -> str:
        buttons: list[str] = []
        for choice in self.choices:
            col, row = self._GRID.get(choice, (2, 2))
            glyph = self._GLYPHS.get(choice, choice)
            checked = ' checked="checked"' if choice == str(default) else ""
            buttons.append(
                f'<label class="dpad-btn dpad-{choice}" '
                f'style="grid-column:{col};grid-row:{row}">'
                f'<input type="radio" name="{name}" value="{choice}"{checked}>'
                f'<span>{glyph}</span>'
                f'</label>'
            )
        return (
            f'<span class="dpad-grid" id="{name}">'
            + "".join(buttons)
            + "</span>"
        )

    def inx(self, name: str, viewname: str, arg: Any) -> str:
        return (
            f'        <param name="{name}" type="optiongroup" appearance="combo"'
            f' gui-text="{viewname}" gui-description={quoteattr(arg.help or "")}>\n'
            + "".join(
                f'            <option value="{c}">{c}</option>\n'
                for c in self.choices
            )
            + "      </param>\n"
        )


class DPadMoverArg:
    """Argparse type rendered as a d-pad mover widget in the web UI.

    Renders a cross of four arrow buttons + a centre reset button arranged
    in a 3×3 grid, plus a step-size stepper below.  Clicking an arrow calls
    ``dpadStep()`` (defined in ``self.js``) which adds ``±step`` to the
    target x or y field via the existing ``stepInput()`` helper.  The centre
    button calls ``dpadReset()`` to zero both fields.

    Usage in ``parserArguments``::

        x_field = f"{prefix}_text_x"
        y_field = f"{prefix}_text_y"
        group.add_argument(f"--{prefix}_text_x",  type=FloatStepper(1.0), default=0.0, ...)
        group.add_argument(f"--{prefix}_text_y",  type=FloatStepper(1.0), default=0.0, ...)
        group.add_argument(f"--{prefix}_text_step",
                           type=DPadMoverArg(x_field, y_field, step=0.5), default=1.0, ...)

    The *step* constructor argument controls the ±increment on the step
    stepper itself (not the d-pad movement amount, which is read live from
    the step field at click time).
    """

    def __init__(self, x_field: str, y_field: str, step: float = 0.5) -> None:
        self.x_field = x_field
        self.y_field = y_field
        self.step = step

    def __call__(self, s: str) -> float:
        return float(s)

    def html(self, name: str, default: str | float, _: Any) -> str:
        xid = self.x_field
        yid = self.y_field
        sid = name          # the step arg's id == its name
        s = self.step
        disp = str(default)

        def btn(direction: str, glyph: str, col: int, row: int,
                dx: int, dy: int) -> str:
            if dx == 0 and dy == 0:
                onclick = f"dpadReset('{xid}','{yid}')"
                extra_class = " dpad-center"
            else:
                onclick = f"dpadStep('{xid}','{yid}','{sid}',{dx},{dy})"
                extra_class = ""
            return (
                f'<button type="button"'
                f' class="dpad-btn dpad-{direction}{extra_class}"'
                f' style="grid-column:{col};grid-row:{row}"'
                f' onclick="{onclick}">{glyph}</button>'
            )

        grid = (
            btn("top",    "↑", 2, 1,  0,  1) +
            btn("left",   "←", 1, 2, -1,  0) +
            btn("center", "·", 2, 2,  0,  0) +
            btn("right",  "→", 3, 2,  1,  0) +
            btn("bottom", "↓", 2, 3,  0, -1)
        )
        stepper = (
            f'<span class="dpad-step-label">step</span>'
            f'<button type="button" class="stepper-btn"'
            f' onclick="stepInput(\'{sid}\', -{s})">&#8722;</button>'
            f'<input name="{name}" id="{sid}" class="stepper-input"'
            f' type="text" value="{disp}">'
            f'<button type="button" class="stepper-btn"'
            f' onclick="stepInput(\'{sid}\', {s})">+</button>'
            f'<span class="dpad-step-label">mm</span>'
        )
        return (
            f'<span class="dpad-mover">'
            f'<span class="dpad-grid">{grid}</span>'
            f'<span class="stepper-wrap">{stepper}</span>'
            f'</span>'
        )


class IntStepper:
    """Argparse type that adds −/+ stepper buttons to any integer parameter in the web UI.

    Usage – replace ``type=int`` with ``type=IntStepper(step)``::

        self.argparser.add_argument(
            "--my_count", action="store", type=IntStepper(1), default=10,
            help="My integer parameter")

    ``step`` controls how much each button click changes the value (default: 1).

    ``auto_default`` – when the field currently shows **0** the first click will
    jump to ``auto_default ± step`` instead of ``0 ± step``.

    The value is still stored and passed to argparse as a plain ``int``.
    """

    def __init__(self, step: int = 1, auto_default: int | None = None) -> None:
        self.step = step
        self.auto_default = auto_default

    def __call__(self, s: str) -> int:
        return int(s)

    def html(self, name: str, default: str | int, translate: Any) -> str:
        step = self.step
        auto_arg = f", {self.auto_default}" if self.auto_default is not None else ""
        return (
            f'<span class="stepper-wrap">'
            f'<button type="button" class="stepper-btn"'
            f' onclick="stepInputInt(\'{name}\', -{step}{auto_arg})">&#8722;</button>'
            f'<input name="{name}" id="{name}" class="stepper-input"'
            f' aria-labeledby="{name}_id {name}_description"'
            f' type="text" value="{default}">'
            f'<button type="button" class="stepper-btn"'
            f' onclick="stepInputInt(\'{name}\', {step}{auto_arg})">+</button>'
            f'</span>'
        )
