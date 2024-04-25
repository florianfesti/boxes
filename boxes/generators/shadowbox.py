# Copyright (C) 2024 Oliver Jensen
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


class Shadowbox(Boxes):
    """The frame and spacers necessary to display a shadowbox / lightbox."""

    description = """
The frame needed to build a shadowbox from paper cutouts.
The cutout used in the photographs can be downloaded [here](https://3axis.co/laser-cut-my-neighbor-totoro-3d-lightbox-lamp-cdr-file/eoxldrxo/).

See the diagram below for dimensions.

![diagram](static/samples/Shadowbox-diagram.jpg)

![backlit](static/samples/Shadowbox-backlit.jpg)
"""

    ui_group = "Misc"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.DoveTailSettings, angle=10, depth=1.5, radius=0.1, size=1)
        self.buildArgParser(x=200, y=260)
        self.argparser.add_argument(
            "--layers", action="store", type=int, default=7,
            help="the number of paper layers; don't forget the back (blank) layer!")
        self.argparser.add_argument(
            "--framewidth", action="store", type=float, default=10,
            help="the width of the paper layer frames")
        self.argparser.add_argument(
            "--frameheight", action="store", type=float, default=10,
            help="the height of the paper layer frames")
        self.argparser.add_argument(
            "--extraheight", action="store", type=float, default=20,
            help="cumulative height of your paper layers, play between frames, the LED strip, battery/wiring, anything else you want to fit in the case")
        self.argparser.add_argument(
            "--casejoinery", action="store", type=boolarg, default=True,
            help="whether or not to join sides to front plate (disable if doing manual joins on fancy wood)")

    def render(self):
        x, y = self.x, self.y
        t = self.thickness
        extraheight = self.extraheight
        frameheight = self.frameheight
        framewidth = self.framewidth
        casejoinery = self.casejoinery
        layers = self.layers
        height = layers * t + extraheight

        # inner frames horizontal bars
        for _ in range(2*layers):
            self.polygonWall([
                x, 90,
                frameheight, 90,
                framewidth, 0, x - framewidth*2, 0, framewidth, 90,
                frameheight, 90],
                "eeDeDe", move="up")

        # inner frames vertical bars
        for _ in range(2*layers):
            self.rectangularWall(y - frameheight*2, framewidth, "eded", move="up")

        # faceplate
        hypotenuse = math.sqrt((frameheight+t)**2 + (framewidth+t)**2)
        angle = math.degrees(math.acos((framewidth+t) / hypotenuse))
        edgetypes = 'eFeeee' if casejoinery else 'eeeeee'

        vframe_poly = [
            t, 0, y, 0, t, 90+angle,
            hypotenuse, 90-angle,
            y - frameheight*2, 90-angle,
            hypotenuse, 90+angle]
        hframe_poly = [
            t, 0, x, 0, t, 180-angle,
            hypotenuse, angle,
            x - framewidth*2, angle,
            hypotenuse, 180-angle]

        self.polygonWall(vframe_poly, edgetypes, move="up")
        self.polygonWall(vframe_poly, edgetypes, move="up")

        self.polygonWall(hframe_poly, edgetypes, move="up")
        self.polygonWall(hframe_poly, edgetypes, move="up")

        # case sides
        if casejoinery:
            top_edge = 'f'
        else:
            top_edge = 'e'
        self.rectangularWall(x, height, f"ef{top_edge}f", move="up")
        self.rectangularWall(x, height, f"ef{top_edge}f", move="up")
        self.rectangularWall(y, height, f"eF{top_edge}F", move="up")
        self.rectangularWall(y, height, f"eF{top_edge}F", move="up")
