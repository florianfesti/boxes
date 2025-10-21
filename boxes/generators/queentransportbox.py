# Copyright (C) 2013-2014 Florian Festi
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
from boxes.lids import LidSettings, _TopEdge
import math

class Cutout:
    """Base class for cutouts"""
    DIMENSIONS = (0.0, 0.0)

    def cutout(self, box, x, y, color=Color.INNER_CUT):
        pass


class CircleCutout(Cutout):
    RADIUS = 12.0 / 2.0
    DIMENSIONS = (RADIUS * 2.0, RADIUS * 2.0)

    def cutout(self, box, x, y, color=Color.INNER_CUT):
        """
        Fügt den runden Käfig-Ausschnitt in die Platte ein.
        cx, cy = Mittelpunkt der Aussparung
        """
        with box.saved_context():
            box.set_source_color(color)
            box.circle(x, y, self.RADIUS)


class PolygonCutout(Cutout):
    PTS = ( (0.0, 0.0), )

    def cutout(self, box, x, y, color=Color.INNER_CUT):
        """
        Fügt den Käfig-Ausschnitt (aus SVG umgewandelt) in die Platte ein.
        cx, cy = Mittelpunkt der Aussparung
        """
        with box.saved_context() as ctx:
            box.set_source_color(color)
            ctx.translate(x, y)
            if self.PTS:
                ipts = iter(self.PTS)
                # Move to first transformed point, then line_to the rest
                px, py = next(ipts)
                ctx.move_to(px, py)
                for px, py in ipts:
                    ctx.line_to(px, py)

                ctx.stroke()


class PathCutout(Cutout):
    """General SVG path cutout. Supports M(oveTo), L(ineTo), C(urveTo) commands."""
    # approximate size from SVG viewBox (mm)
    DIMENSIONS = (0., 0.)
    OFFSET = (0., 0.)

    # SVG path data and transform (from the provided SVG)
    SEGMENTS = [('M', (0., 0.)),
                 ('L', (0., 0.)),
                 ('C', (0., 0., 0., 0., 0., 0.))
               ]

    def cutout(self, box, x, y, color=Color.INNER_CUT):
        with box.saved_context() as ctx:
            box.set_source_color(color)
            #
            ctx.translate(x, y)
            ctx.translate(*self.OFFSET)
            CMDS = {'M': ctx.move_to, 'L': ctx.line_to, 'C': ctx.curve_to}
            for command, params in self.SEGMENTS:
                CMDS[command](*params)
            ctx.stroke()


class NoneCutout(Cutout):
    """No cutout"""


class NicotIncubatorCageCutout(CircleCutout):
    """Nicot incubator cage"""
    RADIUS = 21.35 / 2.0
    DIMENSIONS = (RADIUS * 2.0, RADIUS * 2.0)


class NicotTransportCageCutout(PathCutout):
    """Nicot transport and introduction cage"""
    DIMENSIONS = (36.2, 15.5)
    OFFSET = (-32.555031,-21.874992)
    SEGMENTS = [
        ('M', (40.305031, 27.125)),
        ('L', (40.305031, 29.625)),
        ('L', (43.555031, 29.625)),
        ('L', (43.555031, 27.125)),
        ('L', (46.555031, 27.125)),
        ('L', (49.555031, 17.125)),
        ('L', (50.055031, 17.125)),
        ('L', (50.655037, 17.125)),
        ('L', (50.655037, 14.125)),
        ('L', (41.805031, 14.125)),
        ('C', (41.805031, 14.401142, 41.581173, 14.500713, 41.305031, 14.500713)),
        ('C', (41.028889, 14.500713, 40.805031, 14.401142, 40.805031, 14.125)),
        ('L', (24.305031, 14.125)),
        ('C', (24.305031, 14.401142, 24.081173, 14.500713, 23.805031, 14.500713)),
        ('C', (23.528889, 14.500713, 23.305031, 14.401142, 23.305031, 14.125)),
        ('L', (15.055031, 14.125)),
        ('L', (14.455027, 14.125)),
        ('L', (14.455027, 17.125)),
        ('L', (15.555031, 17.125)),
        ('L', (18.555031, 27.125)),
        ('L', (21.555031, 27.125)),
        ('L', (21.555031, 29.625)),
        ('L', (24.805031, 29.625)),
        ('L', (24.805031, 27.125)),
        ('L', (40.305031, 27.125))

    ]

class NicotHatchingCageCutout(PathCutout):
    """Nicot hatching cage"""
    DIMENSIONS = (27.0, 27.0)
    SEGMENTS = [('M', (-9.721000000000004, -8.771999999999998)),
                 ('L', (-10.155346182387007, -8.265839332298988)),
                 ('C', (-13.886551020012014, -3.6821541920039706, -14.084879200641005, 2.832221276653023, -10.639422029363011, 7.634389722454024)),
                 ('L', (-13.888039878829005, 10.883002977682018)),
                 ('L', (-10.873861961053002, 13.897185158154024)),
                 ('L', (-7.625244111587008, 10.648571902926015)),
                 ('L', (-7.201256192106008, 10.944120092323026)),
                 ('C', (-1.3706305347910046, 14.78343744577301, 6.446125932330986, 13.377937282497022, 10.574118665392987, 7.747997846391023)),
                 ('C', (13.498296778466994, 3.7572195214790085, 13.925493259226002, -1.5399073009179816, 11.678636480890987, -5.947701805147979)),
                 ('C', (12.248662344696001, -7.575763913767979, 11.834613878094999, -9.385966038929986, 10.614878655487004, -10.605702986505982)),
                 ('C', (9.395143432878982, -11.825439934081977, 7.584941893271996, -12.239490960695981, 5.956878978515, -11.669467399319963)),
                 ('C', (0.6772758573989961, -14.36253149263198, -5.7526862178120055, -13.174189825958983, -9.721000000000004, -8.771999999999998))]


class AirHolesForNicotTransportCageCutout(Cutout):
    """Air hole cutout"""
    DIMENSIONS = NicotHatchingCageCutout.DIMENSIONS
    SIZE = (25., 3.)
    OFFSET = (0., -1.250)

    def cutout(self, box, x, y, color=Color.INNER_CUT):
        aw = box.aw
        ah = box.ah
        with box.saved_context():
            box.set_source_color(color)
            l, h = self.SIZE
            ox, oy = self.OFFSET
            box.rectangularHole(x + ox, y + oy - h, l, h, h/2., True, True)
            box.rectangularHole(x + ox, y + oy + h, l, h, h/2., True, True)


class HexHolesCutout(Cutout):
    """Nicot incubator cage"""
    DIMENSIONS = (20., 20.)
    RADIUS = 10.
    OFFSET = (0., 0.)
    IRADIUS = 2.
    LEVELS = 3

    def cutout(self, box, x, y, color=Color.INNER_CUT):
        with box.saved_context() as ctx:
            box.set_source_color(color)
            ctx.translate(x, y)
            ctx.translate(*self.OFFSET)
            draw = box.regularPolygonHole
            draw(0., 0., self.IRADIUS)
            cxy = [ (math.cos(a), math.sin(a)) for a in (math.radians(angle) for angle in range(30, 360, 60)) ]
            r = 2.5 * self.IRADIUS
            for cx, cy in cxy:
                draw(r * cx, r * cy, self.IRADIUS)
            if self.LEVELS > 2:
                r = 5. * self.IRADIUS
                for cx, cy in cxy:
                    draw(r * cx, r * cy, self.IRADIUS)
                    lx, ly = cxy[-1]
                r *= .5
                for cx, cy in cxy:
                    draw(r * (cx + lx), r * (cy + ly), self.IRADIUS)
                    lx, ly = cx, cy


class AirHolesForNicotIncubatorCageCutout(HexHolesCutout):
    """Nicot incubator cage"""
    RADIUS = NicotIncubatorCageCutout.RADIUS * 0.8
    DIMENSIONS = NicotIncubatorCageCutout.DIMENSIONS
    OFFSET = (0., 0.)
    IRADIUS = 2.
    LEVELS = 2


class AirHolesForNicotHatchingCageCutout(HexHolesCutout):
    """Nicot incubator cage"""
    DIMENSIONS = NicotHatchingCageCutout.DIMENSIONS
    RADIUS = min(NicotHatchingCageCutout.DIMENSIONS) / 2.
    OFFSET = (0., 0.)
    IRADIUS = 2.
    LEVELS = 3


class QueenTransportBox(_TopEdge):
    """Box for Bee Queen Transport Cages"""

    description = "Queen Transport Box"

    ui_group = "Box"

    CUTOUTS = (NicotTransportCageCutout, NicotHatchingCageCutout, NicotIncubatorCageCutout, AirHolesForNicotTransportCageCutout, AirHolesForNicotIncubatorCageCutout, AirHolesForNicotHatchingCageCutout, NoneCutout)
    LAYERS = (NoneCutout, NicotTransportCageCutout, NoneCutout)
    DEFAULT = dict(sx="5:45*3:5", sy="5:30*3:5", sh="25:75", aw=3.0, ah="70:20", ax="10:20:10:20:10:20:10", ay="20:60:20", bottom_edge="s", top_edge="e")
    CHOICES = dict(top_edge="eStG", bottom_edge="Fhsše")
    LIDSETTINGS = dict(style="overthetop")

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(LidSettings, **self.LIDSETTINGS)
        self.addSettingsArgs(edges.StackableSettings)
        self.argparser.add_argument(
            "--top_edge", action="store",
            type=ArgparseEdgeType(self.CHOICES["top_edge"]),
            choices=list(self.CHOICES["top_edge"]),
            default=self.DEFAULT["top_edge"],
            help="edge type for top edge")
        self.argparser.add_argument(
            "--bottom_edge", action="store",
            type=ArgparseEdgeType(self.CHOICES["bottom_edge"]),
            choices=list(self.CHOICES["bottom_edge"]),
            default=self.DEFAULT["bottom_edge"],
            help="edge type for bottom edge")
        self.buildArgParser(sx=self.DEFAULT["sx"], sy=self.DEFAULT["sy"], sh=self.DEFAULT["sh"])
        self.argparser.add_argument(
            "--aw", action="store", type=float,
            default=self.DEFAULT["aw"],
            help="""air hole slot width in mm""")
        self.argparser.add_argument(
            "--ah", action="store", type=argparseSections,
            default=self.DEFAULT["ah"],
            help="""air hole sections bottom to top in mm""")
        self.argparser.add_argument(
            "--ax", action="store", type=argparseSections,
            default=self.DEFAULT["ax"],
            help="""air hole sections sections left to right in %% of the box width""")
        self.argparser.add_argument(
            "--ay", action="store", type=argparseSections,
            default=self.DEFAULT["ay"],
            help="""air hole sections back to front in %% of the box depth""")

        # add cutout selection based on CUTOUTS; use class names as keys and first docline as descriptions
        cutout_choices = [c.__name__.removesuffix('Cutout') for c in self.CUTOUTS]
        cutout_descriptions = "; ".join(
            f"{c.__name__}: {((c.__doc__ or '').strip().splitlines()[0]) if (c.__doc__ or '').strip() else ''}"
            for c in self.CUTOUTS
        )
        layers = [c.__name__.removesuffix('Cutout') for c in self.LAYERS]
        for n, default in enumerate(layers):
            layer = len(layers) - 1 - n
            self.argparser.add_argument(
                f"--layer{layer}", action="store",
                choices=cutout_choices, default=default,
                help=f"select cutout type for layer {layer}{" (bottom)" if layer == 0 else ""}." )

    def get_cutout(self, cutout_name):
        for cutout_class in self.CUTOUTS:
            if cutout_class.__name__.removesuffix('Cutout') == cutout_name:
                return cutout_class()
        raise ValueError(f"Cutout '{cutout_name}' not found.")

    def cutouts(self, layer=0):
        y = 0.
        cutout = self.get_cutout(getattr(self, f"layer{layer}"))
        for dy in self.sy:
            x = 0.
            for dx in self.sx:
                if dx > cutout.DIMENSIONS[0] and dy > cutout.DIMENSIONS[1]:
                    cutout.cutout(self, x + dx / 2., y + dy / 2.)
                x += dx
            y += dy

    def sideholes(self, l):
        t = self.thickness
        h = -0.5 * t
        for d in self.sh[:-1]:
            h += d + t
            self.fingerHolesAt(0, h, l, angle=0)

    def airholes(self, l, sections):
        aw = self.aw
        total = sum(sections)
        pl = l / 100.
        y = 0.0
        with self.saved_context():
            self.ctx.rotate(math.pi / -2.0)
            for h in self.ah:
                y += h
                px = 0.0
                for n, s in enumerate(sections):
                    if n % 2 == 1:
                        self.rectangularHole(px * pl - l, y, pl * s, aw, aw/2., False, True)
                    px += s

    def render(self):
        x = sum(self.sx)
        y = sum(self.sy)

        h = sum(self.sh) + self.thickness * (len(self.sh)-1)
        b = self.bottom_edge
        t_left, t_back, t_right, t_front = self.topEdges(self.top_edge)

        self.rectangularWall(
            x, h, [b, "F", t_back, "F"],
            ignore_widths=[1, 6],
            callback=[lambda: self.sideholes(x), lambda: self.airholes(x, self.ax)], move="right", label='Back')
        self.rectangularWall(
            y, h, [b, "f", t_left, "f"], callback=[lambda: self.sideholes(y), lambda: self.airholes(y, self.ay)],
            ignore_widths=[1, 6],
            move="up", label='Left')
        self.rectangularWall(
            y, h, [b, "f", t_right, "f"], callback=[lambda: self.sideholes(y), lambda: self.airholes(y, self.ay)],
            ignore_widths=[1, 6], label='Right')
        self.rectangularWall(
            x, h, [b, "F", t_front, "F"],
            ignore_widths=[1, 6],
            callback=[lambda: self.sideholes(x), lambda: self.airholes(x, self.ax)], move="left up", label='Front')
        with self.saved_context():
            if b not in "eš":
                self.rectangularWall(
                    x, y, "ffff", callback=[lambda: self.cutouts(layer=0)], label=f'Bottom Layer')
            for layer in range(1, len(self.sh)):
                self.rectangularWall(
                    x, y, "ffff", callback=[lambda: self.cutouts(layer)], move="up", label=f'Layer {layer}')
        self.rectangularWall(x, y, "ffff", move="right only")
        self.lid(x, y, self.top_edge)
