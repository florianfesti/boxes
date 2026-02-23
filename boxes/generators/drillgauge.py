# Copyright (C) 2013-2016 Florian Festi
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

from boxes import *


class DrillGauge(Boxes):
    """A drill gauge with a narrowing slot"""

    ui_group = "Misc"

    description = "Make sure to use a burn setting that is tight but does not require force!"

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.MountingSettings, style=edges.MountingSettings.PARAM_EXT)

        self.argparser.add_argument(
            "--sizes",  action="store", type=argparseSections,
            default="1.0:1.5:2.0:2.5:3.0:3.3:3.5:4.0:4.2:4.5" + "".join(f":{i/2:.1f}" for i in range(2*5,2*13+1)),
            help="List of the sizes")
        self.argparser.add_argument(
            "--fontsize",  action="store", type=float, default=8,
            help="Size of the numbers")
        self.argparser.add_argument(
            "--text_placement",  action="store", type=str, default="left",
            choices=("left", "right"),
            help="Have the text left or right?")
        self.argparser.add_argument(
            "--mounting_holes",  action="store", type=str, default="none",
            choices=("none", "left", "right", "top", "bottom"),
            help="Add mounting holes")

    def _step45(self, s):
        if not s:
            return
        direction = -1 if s > 0 else 1
        self.polyline(0, -45*direction, 2**0.5*abs(s), 45*direction)

    def gauge(self):
        max_size = max(self.sizes)
        fs = self.fontsize
        text_left = self.text_placement == "left"
        t = self.thickness
        self.moveTo((5*fs  if text_left else 3*t) + max_size/2, 3*t, 90)

        def draw_size(left):
            @restore
            def draw_text(self, left=True):
                self.ctx.stroke()
                self.set_source_color(Color.ETCHING)
                direction = -1 if left else 1
                self.text(f"{s:.1f}", length/2+direction*0.1*fs, (3 + (max_size - s) / 2 + 2 * fs * (nr%2)),
                          angle=direction * 90,
                          align="middle right" if left else "middle left",
                          fontsize=fs, color=Color.ETCHING)
                if nr % 2:
                    self.moveTo(length/2, fs/4, 90)
                    self.edge(2*fs + (max_size - s)/2)

                self.ctx.stroke()

            length = max(fs/2, s/2)
            self._step45((s - last) / 2)
            if ((left and text_left) or
                (not left and not text_left)):
                draw_text(self, text_left)
            self.edge(length)

        last = 0
        for nr, s in enumerate(self.sizes):
            draw_size(True)
            last = s
        self.corner(-180, self.sizes[-1] / 2)
        for nr, s in reversed(tuple(enumerate(self.sizes))):
            draw_size(False)
            last = s
        self._step45((0 - last) / 2)

    def height(self, sizes):
        return self.max_size * (0.5 + 0.5**0.5) + sum(max(self.min_height, size/2) for size in self.sizes)

    def render(self):
        t = self.thickness
        self.max_size = max(self.sizes)
        self.min_height = self.fontsize / 2

        edges = {
            "none":   "eeee",
            "bottom": "Geee",
            "right":  "eGee",
            "top":    "eeGe",
            "left":   "eeeG",
            }[self.mounting_holes]

        self.rectangularWall(5*self.fontsize+self.max_size+3*t, 6*t+self.height(self.sizes), edges, callback=[self.gauge])
