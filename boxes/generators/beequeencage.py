# Copyright (C) 2025 Martin Scharrer
#
# Based on boxes/generators/closedbox.py, Copyright (C) 2013-2014 Florian Festi
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

from boxes import Boxes, edges, boolarg
from boxes.Color import Color


class BeeQueenCageWallSettings(edges.Settings):
    """ Settings for walls of BeeQueenCage
    """
    NAME = None
    PREFIX = None

    absolute_params = {
        "airhole_width": (3.0, float, "width of air holes (0 for no holes) [mm]"),
        "airhole_separation": (1.5, float, "distance between air holes [mm]"),
        "radius": (1.0, float, "corner radius of air holes [mm]"),
        "top_margin": (4.0, float, "distance of air holes on top side [mm]"),
        "bottom_margin": (22.0, float, "distance of air holes on bottom side [mm]"),
        "side_margin": (4.0, float, "side distance of air holes [mm]"),
    }

    def __init__(self, thickness, relative: bool = True, **kw) -> None:
        self.values = {}
        for name, (value, t, description) in self.absolute_params.items():
            if isinstance(value, tuple):
                value = value[0]
            if type(value) not in (bool, int, float, str):
                raise ValueError("Type not supported: %r", value)
            self.values[name] = value

        self.thickness = thickness
        factor = 1.0
        if relative:
            factor = thickness
        for name, (value, t, description) in self.relative_params.items():
            self.values[name] = value * factor
        self.setValues(thickness, relative, **kw)

    @classmethod
    def parserArguments(cls, parser, prefix=None, **defaults):
        name = cls.NAME or cls.__doc__.split("\n")[0]
        if not prefix:
            prefix = cls.PREFIX or cls.__name__[:-len("Settings")]
        group = parser.add_argument_group(name)
        group.prefix = prefix

        for name, (default, t, description) in (sorted(cls.absolute_params.items()) +
                                                sorted(cls.relative_params.items())):
            aname = name.replace(" ", "_")
            group.add_argument(f"--{prefix}_{aname}",
                               type=t,
                               action="store", default=default,
                               choices=None,
                               help=description)

class BeeQueenCagePlugSettings(BeeQueenCageWallSettings):
    """ Settings for plug of BeeQueenCage
    """
    absolute_params = {
        'diameter_top': (25.0, float, "diameter of top part of the plug (0 for no plug) [mm]"),
        'diameter_bottom': (17.0, float,
                            "diameter of bottom part of the plug (Should correspondent to hole diameter) [mm]"),
        'diameter_inner': (9.65, float, "diameter of inner cutout in bottom part (0 for no inner cutout) [mm]"),
    }


class BeeQueenCage(Boxes):
    """Cage box to house a bee queen"""

    ui_group = "Beekeeping"

    description = """Cage box to house a bee queen.
The default opening on top is suitable for a Nicot queen-rearing cell cup block (CNE2) or a cork plug.
This makes the cage suitable as a hatching cage.

Holes can be configured per side. The default value of 3.0mm is suitable as air holes, but this can be changed to
produce queen excluders (4.2mm) or drone excluders (5.2mm). Some space should be left closed to provide cover for
the young queen against aggressive worker bees.

If required a plug can be added to close the top opening.
By default it contains a inner cutout to fit a Nicot cell cup (CNE3) making it a wooden alternative to the
plastic Nicot cell cup block (CNE2).
"""

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser("outside", x=25, y=25, h=70)

        # Custom UI parameters
        ap = self.argparser
        ap.add_argument("--d", type=float, default=17.0, help="Diameter of top hole [mm]")
        for name in ("front", "back", "left", "right"):
            ap.add_argument(f"--holes_{name}", type=boolarg, default=True,
                            help=f"create holes on the {name}")

        self.addSettingsArgs(BeeQueenCageWallSettings)

    def airholes(self, w, h, label):
        if label == "Top":
            self.render_top(w, h)
        elif label == "Bottom":
            pass
        elif getattr(self, f"holes_{label.lower()}"):
            label = ""
            g = self.wallSettings.airhole_width
            dg = self.wallSettings.airhole_separation
            r = self.wallSettings.radius
            tm = self.wallSettings.top_margin
            bm = self.wallSettings.bottom_margin
            sm = self.wallSettings.side_margin

            k = g + dg  # pitch of holes
            num_holes = int((h - tm - bm + dg / 2) / k)  # number of holes over height
            xch = w / 2.
            l = w - 2 * sm  # length of holes
            bh = (h - k * num_holes + dg + bm - tm) / 2.  # offset of first hole

            for n in range(0, num_holes):
                self.rectangularHole(xch, bh + n * k, l, g, r, True, False)

    def render_top(self, x, h):
        self.hole(x / 2., h / 2., d=self.d)

    def render_wall(self, edges, w, h, label, move="right"):
        self.rectangularWall(w, h, edges, bedBolts=[None] * 4,
                             move=move, label=label, callback=[lambda: self.airholes(w, h, label)])

    def render_plug(self):
        """ Render round plug for the bee queen cage"""
        dt = self.plugSettings.diameter_top
        db = self.plugSettings.diameter_bottom
        di = self.plugSettings.diameter_inner

        if dt > 0 and db > 0:
            with self.saved_context():
                self.parts.disc(dt, label="Plug\nTop", move="up",
                                callback=lambda: self.hole(0, 0, d=db, color=Color.ETCHING))
                self.parts.disc(db, label="Plug\nBottom", callback=None if di == 0 else lambda: self.hole(0, 0, d=di))

    def render(self):
        self.plugSettings = BeeQueenCagePlugSettings(
            self.thickness, True, **self.edgesettings.get("BeeQueenCagePlug", {}))
        self.wallSettings = BeeQueenCageWallSettings(
            self.thickness, True, **self.edgesettings.get("BeeQueenCageWall", {}))

        ox, oy, oh = x, y, h = self.x, self.y, self.h

        if self.outside:
            x = self.adjustSize(x)
            y = self.adjustSize(y)
            h = self.adjustSize(h)

        self.render_wall("FFFF", x, h, "Front", "right")
        self.render_wall("FFFF", x, h, "Back", "right")
        self.render_wall("FfFf", y, h, "Left", "right")
        self.render_wall("FfFf", y, h, "Right", "right")

        with self.saved_context():
            self.render_wall("ffff", x, y, "Top", "up" if 2 * oy <= oh else "right")
            self.render_wall("ffff", x, y, "Bottom", "right")

        # Move drawing point to the right for lid rendering
        if 2 * oy > oh:
            self.render_wall("ffff", x, y, "Top", "right only")
        self.render_wall("ffff", x, y, "Bottom", "right only")

        self.render_plug()
