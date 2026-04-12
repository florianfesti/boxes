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
    The value is still stored and passed to argparse as a plain ``float``.
    """

    def __init__(self, step: float = 1.0) -> None:
        self.step = step

    def __call__(self, s: str) -> float:
        return float(s)

    def html(self, name: str, default: str | float, translate: Any) -> str:
        step = self.step
        return (
            f'<span class="stepper-wrap">'
            f'<button type="button" class="stepper-btn"'
            f' onclick="stepInput(\'{name}\', -{step})">&#8722;</button>'
            f'<input name="{name}" id="{name}" class="stepper-input"'
            f' aria-labeledby="{name}_id {name}_description"'
            f' type="text" value="{default}">'
            f'<button type="button" class="stepper-btn"'
            f' onclick="stepInput(\'{name}\', {step})">+</button>'
            f'</span>'
        )


class IntStepper:
    """Argparse type that adds −/+ stepper buttons to any integer parameter in the web UI.

    Usage – replace ``type=int`` with ``type=IntStepper(step)``::

        self.argparser.add_argument(
            "--my_count", action="store", type=IntStepper(1), default=10,
            help="My integer parameter")

    ``step`` controls how much each button click changes the value (default: 1).
    The value is still stored and passed to argparse as a plain ``int``.
    """

    def __init__(self, step: int = 1) -> None:
        self.step = step

    def __call__(self, s: str) -> int:
        return int(s)

    def html(self, name: str, default: str | int, translate: Any) -> str:
        step = self.step
        return (
            f'<span class="stepper-wrap">'
            f'<button type="button" class="stepper-btn"'
            f' onclick="stepInputInt(\'{name}\', -{step})">&#8722;</button>'
            f'<input name="{name}" id="{name}" class="stepper-input"'
            f' aria-labeledby="{name}_id {name}_description"'
            f' type="text" value="{default}">'
            f'<button type="button" class="stepper-btn"'
            f' onclick="stepInputInt(\'{name}\', {step})">+</button>'
            f'</span>'
        )
