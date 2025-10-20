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
from boxes.generators.drillbox import DrillBox
from boxes.lids import LidSettings

class Cutout:
    DIMENSIONS = (0.0, 0.0)

    @staticmethod
    def transform_point(u, v, tx, ty):
        return (tx - u), (ty - v)

    def cutout(self, box, x, y, layer=0, color=Color.INNER_CUT):
        pass


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


class QueenCageCutout(SingleLayerPolygonCutout):
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


class QueenTransportBox(DrillBox):
    """A simple Box"""

    description = "Queen Transport Box"

    ui_group = "Box"

    CUTOUT_DIMENSIONS = (36.2, 15.5)

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings,
                             space=3, finger=3, surroundingspaces=1)
        self.addSettingsArgs(edges.RoundedTriangleEdgeSettings, outset=1)
        self.addSettingsArgs(edges.StackableSettings)
        self.addSettingsArgs(edges.MountingSettings)
        self.addSettingsArgs(LidSettings, style="overthetop")
        self.argparser.add_argument(
            "--top_edge", action="store",
            type=ArgparseEdgeType("eStG"), choices=list("eStG"),
            default="e", help="edge type for top edge")
        self.buildArgParser(sx="5:45*3:5", sy="5:25*3:5", sh="25:75", bottom_edge="s")

    def cutouts(self, layer=0):
        y = 0
        d = 1.
        cutout = QueenCageCutout()
        for dy in self.sy:
            x = 0
            for dx in self.sx:
                if dx > cutout.DIMENSIONS[0] and dy > cutout.DIMENSIONS[1]:
                    cutout.cutout(self, x + dx / 2., y + dy / 2., layer)
                x += dx
            y += dy


    def render(self):
        x = sum(self.sx)
        y = sum(self.sy)

        h = sum(self.sh) + self.thickness * (len(self.sh)-1)
        b = self.bottom_edge
        t1, t2, t3, t4 = self.topEdges(self.top_edge)

        self.rectangularWall(
            x, h, [b, "f", t1, "F"],
            ignore_widths=[1, 6],
            callback=[lambda: self.sideholes(x)], move="right", label='Front')
        self.rectangularWall(
            y, h, [b, "f", t2, "F"], callback=[lambda: self.sideholes(y)],
            ignore_widths=[1, 6],
            move="up", label='Left')
        self.rectangularWall(
            y, h, [b, "f", t3, "F"], callback=[lambda: self.sideholes(y)],
            ignore_widths=[1, 6], label='Right')
        self.rectangularWall(
            x, h, [b, "f", t4, "F"],
            ignore_widths=[1, 6],
            callback=[lambda: self.sideholes(x)], move="left up", label='Back')
        if b != "e":
            self.rectangularWall(
                x, y, "ffff", callback=[lambda: self.cutouts(layer=0)], move="up", label=f'Bottom Layer')
        for layer in range(1, len(self.sh)):
            self.rectangularWall(
                x, y, "ffff", callback=[lambda: self.cutouts(layer)], move="up", label=f'Layer {layer}')
        self.lid(x, y, self.top_edge)

