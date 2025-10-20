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

class Cutout:
    """Base class for cutouts"""
    DIMENSIONS = (0.0, 0.0)

    @staticmethod
    def transform_point(u, v, tx, ty):
        return (tx - u), (ty - v)

    def cutout(self, box, x, y, layer=0, color=Color.INNER_CUT):
        pass


class RoundCutout(Cutout):
    RADIUS = 12.0 / 2.0
    DIMENSIONS = (RADIUS * 2.0, RADIUS * 2.0)

    def cutout(self, box, x, y, layer=0, color=Color.INNER_CUT):
        """
        Fügt den runden Käfig-Ausschnitt in die Platte ein.
        cx, cy = Mittelpunkt der Aussparung
        """

        if layer != 0:
            with box.saved_context():
                box.set_source_color(color)
                fx, fy = self.transform_point(0.0, 0.0, x, y)
                box.circle(fx, fy, self.RADIUS)


class NicotIncubatorCageCutout(RoundCutout):
    """Nicot incubator cage"""
    RADIUS = 21.35 / 2.0
    DIMENSIONS = (RADIUS * 2.0, RADIUS * 2.0)


class PolygonCutout(Cutout):
    PTS = (( (0.0, 0.0), ), )

    def get_points(self, layer):
        return self.PTS[layer]

    def cutout(self, box, x, y, layer=0, color=Color.INNER_CUT):
        """
        Fügt den Käfig-Ausschnitt (aus SVG umgewandelt) in die Platte ein.
        cx, cy = Mittelpunkt der Aussparung
        """
        p = box.ctx

        with box.saved_context():
            box.set_source_color(color)
            transform_point = self.transform_point
            pts = self.get_points(layer)

            if pts:
                # Move to first transformed point, then line_to the rest
                fx, fy = transform_point(pts[0][0], pts[0][1], x, y)
                p.move_to(fx, fy)
                for u, v in pts[1:]:
                    fx, fy = transform_point(u, v, x, y)

                    p.line_to(fx, fy)

                p.stroke()


class SingleLayerPolygonCutout(PolygonCutout):

    def get_points(self, layer):
        """Always return the first and only layer, except for layer 0 which is empty"""
        if layer == 0:
            return tuple()
        return self.PTS[0]


class NicotTransportCageCutout(SingleLayerPolygonCutout):
    """Nicot transport and introduction cage"""
    DIMENSIONS = (36.2, 15.5)
    PTS = ((
            (-7.425925777777778, -6.722116592592595),
            (-7.425925777777778, -9.222116592592595),
            (-10.675925777777778, -9.222116592592595),
            (-10.675925777777778, -6.722116592592595),
            (-13.675925777777778, -6.722116592592595),
            (-16.675925777777778, 3.277883407407405),
            (-17.175925777777778, 3.277883407407405),
            (-17.775931777777778, 3.277883407407405),
            (-17.775931777777778, 6.277883407407405),
            (-8.925925777777778, 6.277883407407405),
            (-8.925925777777778, 5.9021704074074055),
            (-8.425925777777778, 5.9021704074074055),
            (-7.925925777777778, 6.277883407407405),
            (8.574074222222222, 6.277883407407405),
            (8.574074222222222, 5.9021704074074055),
            (9.074074222222222, 5.9021704074074055),
            (9.574074222222222, 6.277883407407405),
            (17.824074222222222, 6.277883407407405),
            (18.42407822222222, 6.277883407407405),
            (18.42407822222222, 3.277883407407405),
            (17.324074222222222, 3.277883407407405),
            (14.324074222222222, -6.722116592592595),
            (11.324074222222222, -6.722116592592595),
            (11.324074222222222, -9.222116592592595),
            (8.074074222222222, -9.222116592592595),
            (8.074074222222222, -6.722116592592595),
            (-7.425925777777778, -6.722116592592595)
    ),)

class NicotHatchingCageCutout(Cutout):
    """Nicot hatching cage (drawn from provided SVG path)"""
    # approximate size from SVG viewBox (mm)
    DIMENSIONS = (27.0, 27.0)

    # SVG path data and transform (from the provided SVG)
    _segments = [('M', (-9.721000000000004, -8.771999999999998)),
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


    def cutout(self, box, x, y, layer=0, color=Color.INNER_CUT):
        if layer == 0:
            return

        with box.saved_context() as ctx:
            box.set_source_color(color)
            #
            ctx.translate(x, y)
            CMDS = {'M': ctx.move_to, 'L': ctx.line_to, 'C': ctx.curve_to}
            for command, params in self._segments:
                CMDS[command](*params)
            ctx.stroke()


class NicotHatchingAndIncubatorCageCutout(Cutout):
    """Nicot hatching and incubator cage (combination of both cutouts)"""
    DIMENSIONS = (27.0, 27.0)

    def cutout(self, box, x, y, layer=0, color=Color.INNER_CUT):
        if layer == 0:
            return
        if layer == 1:
            NicotIncubatorCageCutout().cutout(box, x, y, layer, color)
        else:
            NicotHatchingCageCutout().cutout(box, x, y, layer, color)


class QueenTransportBox(_TopEdge):
    """Box for Bee Queen Transport Cages"""

    description = "Queen Transport Box"

    ui_group = "Box"

    CUTOUTS = (NicotTransportCageCutout, NicotHatchingCageCutout, NicotIncubatorCageCutout, NicotHatchingAndIncubatorCageCutout)

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.RoundedTriangleEdgeSettings, outset=1)
        self.addSettingsArgs(edges.StackableSettings)
        self.addSettingsArgs(edges.MountingSettings)
        self.addSettingsArgs(LidSettings, style="overthetop")
        self.argparser.add_argument(
            "--top_edge", action="store",
            type=ArgparseEdgeType("eStG"), choices=list("eStG"),
            default="e", help="edge type for top edge")
        self.argparser.add_argument(
            "--bottom_edge", action="store",
            type=ArgparseEdgeType("Fhsše"), choices=list("Fhsše"),
            default="s",
            help="edge type for bottom edge")
        self.buildArgParser(sx="5:45*3:5", sy="5:30*3:5", sh="25:75")
        self.argparser.add_argument(
            "--aw", action="store", type=float,
            default="3.0",
            help="""air hole slot width in mm""")
        self.argparser.add_argument(
            "--ah", action="store", type=argparseSections,
            default="70:20",
            help="""air hole sections bottom to top in mm""")
        self.argparser.add_argument(
            "--ax", action="store", type=argparseSections,
            default="10:20:10:20:10:20:10",
            help="""air hole sections sections left to right in %% of the box width""")
        self.argparser.add_argument(
            "--ay", action="store", type=argparseSections,
            default="20:60:20",
            help="""air hole sections back to front in %% of the box depth""")
        # add cutout selection based on CUTOUTS; use class names as keys and first docline as descriptions
        cutout_choices = [c.__name__.removesuffix('Cutout') for c in self.CUTOUTS]
        cutout_descriptions = "; ".join(
            f"{c.__name__}: {((c.__doc__ or '').strip().splitlines()[0]) if (c.__doc__ or '').strip() else ''}"
            for c in self.CUTOUTS
        )
        self.argparser.add_argument(
            "--cutout", action="store",
            choices=cutout_choices, default=cutout_choices[0],
            help=f"select cutout type.")

    def get_cutout(self, cutout_name):
        for cutout_class in self.CUTOUTS:
            if cutout_class.__name__.removesuffix('Cutout') == cutout_name:
                return cutout_class()
        raise ValueError(f"Cutout '{cutout_name}' not found.")

    def cutouts(self, layer=0):
        y = 0
        d = 1.
        cutout = self.get_cutout(self.cutout)
        for dy in self.sy:
            x = 0
            for dx in self.sx:
                if dx > cutout.DIMENSIONS[0] and dy > cutout.DIMENSIONS[1]:
                    cutout.cutout(self, x + dx / 2., y + dy / 2., layer)
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
        t1, t2, t3, t4 = self.topEdges(self.top_edge)

        self.rectangularWall(
            x, h, [b, "F", t1, "F"],
            ignore_widths=[1, 6],
            callback=[lambda: self.sideholes(x), lambda: self.airholes(x, self.ax)], move="right", label='Front')
        self.rectangularWall(
            y, h, [b, "f", t2, "f"], callback=[lambda: self.sideholes(y), lambda: self.airholes(y, self.ay)],
            ignore_widths=[1, 6],
            move="up", label='Left')
        self.rectangularWall(
            y, h, [b, "f", t3, "f"], callback=[lambda: self.sideholes(y), lambda: self.airholes(y, self.ay)],
            ignore_widths=[1, 6], label='Right')
        self.rectangularWall(
            x, h, [b, "F", t4, "F"],
            ignore_widths=[1, 6],
            callback=[lambda: self.sideholes(x), lambda: self.airholes(x, self.ax)], move="left up", label='Back')
        if b not in "eš":
            self.rectangularWall(
                x, y, "ffff", callback=[lambda: self.cutouts(layer=0)], move="up", label=f'Bottom Layer')
        for layer in range(1, len(self.sh)):
            self.rectangularWall(
                x, y, "ffff", callback=[lambda: self.cutouts(layer)], move="up", label=f'Layer {layer}')
        self.lid(x, y, self.top_edge)
