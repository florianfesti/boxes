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

from boxes import Boxes, edges
from boxes.Color import Color


class BeeQueenCageWallSettings(edges.Settings):
    """ Settings for walls of BeeQueenCage
    """
    NAME = None
    PREFIX = None

    params = {
        "airhole_width": (3.0, float, "width of air holes (0 for no holes) [mm]"),
        "airhole_separation": (1.5, float, "distance between air holes [mm]"),
        "radius": (1.0, float, "corner radius of air holes [mm]"),
        "top_margin": (4.0, float, "distance of air holes on top side [mm]"),
        "bottom_margin": (22.0, float, "distance of air holes on bottom side [mm]"),
        "side_margin": (4.0, float, "side distance of air holes [mm]"),
    }

    @classmethod
    def parserArguments(cls, parser, prefix=None, **defaults):
        name = cls.NAME or cls.__doc__.split("\n")[0]
        if not prefix:
            prefix = cls.PREFIX or cls.__name__[:-len("Settings")]
        group = parser.add_argument_group(name)
        group.prefix = prefix

        for name, (default, t, description) in cls.params.items():
            aname = name.replace(" ", "_")
            group.add_argument(f"--{prefix}_{aname}",
                               type=t,
                               action="store", default=default,
                               choices=None,
                               help=description)


class BeeQueenCageFrontWallSettings(BeeQueenCageWallSettings):
    """ Settings for front wall of BeeQueenCage
    """


class BeeQueenCageBackWallSettings(BeeQueenCageWallSettings):
    """ Settings for back wall of BeeQueenCage
    """


class BeeQueenCageLeftWallSettings(BeeQueenCageWallSettings):
    """ Settings for left wall of BeeQueenCage
    """


class BeeQueenCageRightWallSettings(BeeQueenCageWallSettings):
    """ Settings for right wall of BeeQueenCage
    """


class BeeQueenCageBottomWallSettings(BeeQueenCageWallSettings):
    """ Settings for bottom wall of BeeQueenCage
    """


class BeeQueenCagePlugSettings(BeeQueenCageWallSettings):
    """ Settings for plug of BeeQueenCage
    """
    params = {
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

        self.addSettingsArgs(BeeQueenCageFrontWallSettings)
        self.addSettingsArgs(BeeQueenCageBackWallSettings)
        self.addSettingsArgs(BeeQueenCageLeftWallSettings)
        self.addSettingsArgs(BeeQueenCageRightWallSettings)
        self.addSettingsArgs(BeeQueenCageBottomWallSettings)
        self.addSettingsArgs(BeeQueenCagePlugSettings)

    def airholes(self, w, h, label):
        if label == "Top":
            self.render_top(w, h)
        else:
            g = getattr(self, f"BeeQueenCage{label}Wall_airhole_width", 0)
            dg = getattr(self, f"BeeQueenCage{label}Wall_airhole_separation", 0)
            r = getattr(self, f"BeeQueenCage{label}Wall_radius", 0)
            tm = getattr(self, f"BeeQueenCage{label}Wall_top_margin", 0)
            bm = getattr(self, f"BeeQueenCage{label}Wall_bottom_margin", 0)
            sm = getattr(self, f"BeeQueenCage{label}Wall_side_margin", 0)

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
        dt = getattr(self, "BeeQueenCagePlug_diameter_top", 0)
        db = getattr(self, "BeeQueenCagePlug_diameter_bottom", 0)
        di = getattr(self, "BeeQueenCagePlug_diameter_inner", 0)

        if dt > 0 and db > 0:
            with self.saved_context():
                self.parts.disc(dt, label="Plug\nTop", move="up",
                                callback=lambda: self.hole(0, 0, d=db, color=Color.ETCHING))
                self.parts.disc(db, label="Plug\nBottom", callback=None if di == 0 else lambda: self.hole(0, 0, d=di))

    def render(self):
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
