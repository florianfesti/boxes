#!/usr/bin/env python3
# Copyright (C) 2020  Luca Schmid
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
from math import atan, degrees, fmod, sqrt

class MarbleCatcher(Boxes):
    """Box for catching marbles at the end of their journey"""

    ui_group = "Unstable"

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=1.0, finger=2.0, space=2.0)

        self.buildArgParser(x=100, y=28, h=22, outside=True)
        self.argparser.add_argument("--grid", type=float, default=15.0, help="grid spacing")
        self.argparser.add_argument("--numclips", type=int, default=2, help="number of clips")


    def rectangularWallWithClips(self, x, y, edges="eeee", move=None, num_clips=[0,0,0,0], draw_clips=True):
        """
        Rectangular wall with clips for box like objects

        :param x: width
        :param y: height
        :param edges:  (Default value = "eeee") bottom, right, top, left
        :param move:  (Default value = None)
        :param num_clips: (Default value = [0,0,0,0]) number of clips to add bottom, right, top, left
        :param draw_clips: (Default value = True) whether or not to actually draw clips

        """
        if len(edges) != 4:
            raise ValueError("four edges required")
        edges = [self.edges.get(e, e) for e in edges]

        bottom = self.grid if draw_clips and num_clips[0] > 0 else 0
        right = self.grid if draw_clips and num_clips[1] > 0 else 0
        top = self.grid if draw_clips and num_clips[2] > 0 else 0
        left = self.grid if draw_clips and num_clips[-1] > 0 else 0
        overallwidth = x + edges[-1].spacing() + edges[1].spacing() + left + right
        overallheight = y + edges[0].spacing() + edges[2].spacing() + bottom + top

        if self.move(overallwidth, overallheight, move, before=True):
            return

        self.moveTo(edges[-1].spacing())
        self.moveTo(0, edges[0].margin())
        self.moveTo(left, bottom)
        for i, l in enumerate((x, y, x, y)):
            e1, e2 = edges[i], edges[(i+1)%4]
            n = num_clips[i]

            if n:
                s = (l-self.grid*n) / (n+1)
                r = fmod(s, self.grid)
                q = s - r
                p = r * (n+1) / 2

                a = (self.grid - self.thickness) / 2
                c = self.grid - a
                for j in range(n):
                    edges[i]((p if j == 0 else 0) + q)
                    if draw_clips:
                        self.corner(-90)
                        self.edge(c)
                        self.corner(90, a)
                        self.corner(90)
                        self.edge(self.grid)
                        self.corner(-90)
                        self.edge(self.thickness)
                        self.corner(-90)
                        self.edge(self.grid)
                        self.corner(90)
                        self.corner(90, a)
                        self.edge(c)
                        self.corner(-90)
                    else:
                        self.edge(self.grid)
                edges[i](q+p)
            else:
                edges[i](l)
            self.edgeCorner(e1, e2, 90)

        self.move(overallwidth, overallheight, move)


    def render(self):
        x, y, h, grid = self.x, self.y, self.h, self.grid

        if self.outside:
            x = self.adjustSize(x)
            y = self.adjustSize(y)
            h = self.adjustSize(h)

        self.rectangularWallWithClips(x, y, 'ffff', move='down', num_clips=[self.numclips,0]*2, draw_clips=False)
        self.rectangularWall(y, h, 'hfef', move='down')
        self.rectangularWallWithClips(x, h, 'hFeF', move='down', num_clips=[self.numclips,0,0,0])
        self.rectangularWall(y, h, 'hfef', move='down')
        self.rectangularWallWithClips(x, h, 'hFeF', move='down', num_clips=[self.numclips,0,0,0])


