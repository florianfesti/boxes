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


class QueenTransportBox(DrillBox):
    """A simple Box"""

    description = "Queen Transport Box"

    ui_group = "Box"

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
        self.buildArgParser(sx="25*3", sy="30*3", sh="1:90", bottom_edge="s")

    def cutouts(self, toplayer=False):
        y = 0
        d = 1.
        for dy in self.sy:
            x = 0
            for dx in self.sx:
                self.cutout(x + dx / 2., y + dy / 2.)
                if toplayer:
                    pass  # TODO: add cutout extras for top layer
                x += dx
            y += dy

    def cutout(self, x, y):
        """
        Fügt den Käfig-Ausschnitt (aus SVG umgewandelt) in die Platte ein.
        cx, cy = Mittelpunkt der Aussparung
        """
        p = self.ctx

        p.save()
        # Der Originalpfad (SVG <path d="...">) in Path-Befehle übersetzt:
        p.move_to(27.125, 40.305031)
        p.line_to(29.625, 40.305031)
        p.line_to(29.625, 43.555031)
        p.line_to(27.125, 43.555031)
        p.line_to(27.125, 46.555031)
        p.line_to(17.125, 49.555031)
        p.line_to(17.125, 50.055031)
        p.line_to(17.125, 50.655037)
        p.line_to(14.125, 50.655037)
        p.line_to(14.125, 41.805031)

        # Diese Linien wurden im SVG durch C-Kommandos (Cubic Bézier) erzeugt,
        # aber da sie sehr kurz und linear sind, können sie als line_to() interpretiert werden.
        p.line_to(14.500713, 41.805031)
        p.line_to(14.500713, 41.305031)
        p.line_to(14.125, 40.805031)
        p.line_to(14.125, 24.305031)
        p.line_to(14.500713, 24.305031)
        p.line_to(14.500713, 23.805031)
        p.line_to(14.125, 23.305031)
        p.line_to(14.125, 15.055031)
        p.line_to(14.125, 14.455027)
        p.line_to(17.125, 14.455027)
        p.line_to(17.125, 15.555031)
        p.line_to(27.125, 18.555031)
        p.line_to(27.125, 21.555031)
        p.line_to(29.625, 21.555031)
        p.line_to(29.625, 24.805031)
        p.line_to(27.125, 24.805031)
        p.line_to(27.125, 40.305031)
        # p.close_path()

        # Der ursprüngliche SVG-Pfad war gedreht (transform="matrix(-0,1,-1,-0,...)")
        # Das entspricht einer 90°-Drehung + Spiegelung. Wir wenden die Transformation an:
        p.rotate(90)
        p.scale(1, -1)

        # Jetzt verschieben wir den Pfad so, dass sein Mittelpunkt bei (cx, cy) liegt:
        p.translate(x, -y)

        # Pfad ausschneiden
        p.stroke()
        p.restore()

    def render(self):
        x = sum(self.sx)
        y = sum(self.sy)

        h = sum(self.sh) + self.thickness * (len(self.sh)-1)
        b = self.bottom_edge
        t1, t2, t3, t4 = self.topEdges(self.top_edge)

        self.rectangularWall(
            x, h, [b, "f", t1, "F"],
            ignore_widths=[1, 6],
            callback=[lambda: self.sideholes(x)], move="right")
        self.rectangularWall(
            y, h, [b, "f", t2, "F"], callback=[lambda: self.sideholes(y)],
            ignore_widths=[1, 6],
            move="up")
        self.rectangularWall(
            y, h, [b, "f", t3, "F"], callback=[lambda: self.sideholes(y)],
            ignore_widths=[1, 6])
        self.rectangularWall(
            x, h, [b, "f", t4, "F"],
            ignore_widths=[1, 6],
            callback=[lambda: self.sideholes(x)], move="left up")
        if b != "e":
            self.rectangularWall(x, y, "ffff", move="right")
        for d in self.sh[:-2]:
            self.rectangularWall(
                x, y, "ffff", callback=[self.cutouts], move="right")
        self.rectangularWall(
            x, y, "ffff",
            callback=[lambda: self.cutouts(toplayer=True)],
            move="right")
        self.lid(x, y, self.top_edge)