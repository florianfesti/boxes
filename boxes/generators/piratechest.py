#!/usr/bin/env python3
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

class Piratechest(Boxes): # Change class name!
    """Box with polygon lid with chest hinges."""

    description = """Do not assemble sides before attaching the lid! 
    Hinge of the lid has to be placed first because it is impossible 
    to get it in position without removing the side wall. The lid can 
    be a bit tricky to assemble. Keep track of how the parts fit together."""

    ui_group = "Box" # see ./__init__.py for names

    def __init__(self) -> None:
        Boxes.__init__(self)

        # Uncomment the settings for the edge types you use
        # use keyword args to set default values
        self.addSettingsArgs(edges.FingerJointSettings, finger=1.0,space=1.0)
        # self.addSettingsArgs(edges.StackableSettings)
        self.addSettingsArgs(edges.HingeSettings)
        # self.addSettingsArgs(edges.LidSettings)
        # self.addSettingsArgs(edges.ClickSettings)
        # self.addSettingsArgs(edges.FlexSettings)

        # remove cli params you do not need
        self.buildArgParser(x=100, y=100, h=100)
        # Add non default cli params if needed (see argparse std lib)
        self.argparser.add_argument(
            "--n",  action="store", type=int, default=5,
            help="number of sides on the lid")


    def render(self):
        # adjust to the variables you want in the local scope
        x, y, h = self.x, self.y, self.h
        t = self.thickness
        n = self.n

        # Create new Edges here if needed E.g.:
        s = edges.FingerJointSettings(self.thickness, relative=False,
                                      space = 10, finger=10,
                                      width=self.thickness)
        p = edges.FingerJointEdge(self, s)
        p.char = "a" # 'a', 'A', 'b' and 'B' is reserved for beeing used within generators
        self.addPart(p)
        # code from regularbox
        fingerJointSettings = copy.deepcopy(self.edges["f"].settings)
        fingerJointSettings.setValues(self.thickness, angle=180./(n-1))
        fingerJointSettings.edgeObjects(self, chars="gGH")
        # render your parts here

        self.ctx.save()

        self.rectangularWall(x, y, "FFFF", move="up", label="Bottom")
        frontlid, toplids, backlid = self.topside(y, n = n, move="only", bottem='P')

        self.rectangularWall(x, backlid, "qFgF", move="up", label="lid back")
        for _ in range(n-2):
            self.rectangularWall(x, toplids, "GFgF", move="up", label="lid top")
        self.rectangularWall(x, frontlid, "GFeF", move="up", label="lid front")

        self.ctx.restore()
        self.rectangularWall(x, y, "FFFF", move="right only")

        with self.saved_context():
            self.rectangularWall(x, h, "fFQF", ignore_widths=[2, 5], move="right", label="front")
            self.rectangularWall(y, h, "ffof", ignore_widths=[5], move="right", label="right")
            self.rectangularWall(0, h, "eeep", move="right only")
        self.rectangularWall(x, h, "fFoF", move="up only")
        self.rectangularWall(x, 0, "Peee", move="up only")

        hy = self.edges["O"].startwidth()
        hy2 = self.edges["P"].startwidth()
        e1 = edges.CompoundEdge(self, "Fe", (h, hy))
        e2 = edges.CompoundEdge(self, "eF", (hy, h))
        e_back = ("f", e1, "e", e2)

        with self.saved_context():
            #self.rectangularWall(x, h, "fFeF", ignore_widths=[2, 5], move="right", label="back")
            self.rectangularWall(x, h+hy, e_back, move="right", label="back") # extend back to correct height
            self.rectangularWall(0, h, "ePee", move="right only")
            self.rectangularWall(y, h, "ffOf", ignore_widths=[2], move="right", label="left")
        self.rectangularWall(x, h, "fFOF", move="up only")
        self.rectangularWall(x, 0, "peee", move="up only")


        self.topside(y, n = n, move="right", bottem='p', label="lid left")
        self.topside(y, n = n, move="right", bottem='P', label="lid right")


 

    def topside(self, y, n, bottem='e', move=None, label=""):
        radius, hp, side  = self.regularPolygon((n - 1) * 2, h=y/2.0)
        t = self.thickness
        
        #edge = self.edges.get('f')

        tx = y + 2 * self.edges.get('f').spacing()
        lidheight = hp if n % 2 else radius
        ty = lidheight + self.edges.get('f').spacing() + self.edges.get(bottem).spacing()
        
        if self.move(tx, ty, move, before=True):
            if bottem in "pP":
                return side/2 + self.edges.get(bottem).spacing(), side, side/2
            else:
                return side/2, side, side/2

        self.moveTo(self.edges.get('f').margin(), self.edges.get(bottem).margin())

        self.edges.get(bottem)(y)

        self.corner(90)
        if bottem == 'p':
            self.edges.get('f')(side/2 + self.edges.get(bottem).spacing())
        else:
            self.edges.get('f')(side/2)
        
        #self.edgeCorner(self.edges.get('f'), self.edges.get('f'), 180 / (n - 1))
        self.corner(180 / (n - 1))
        for i in range(n-2):
            self.edges.get('f')(side)
            #self.edgeCorner(self.edges.get('f'), self.edges.get('f'), 180 / (n - 1))
            self.corner(180 / (n - 1))

        if bottem == 'P':
            self.edges.get('f')(side/2 + self.edges.get(bottem).spacing())
        else:
            self.edges.get('f')(side/2)
        
        self.corner(90)

        self.move(tx, ty, move, label=label)

        if bottem in "pP":
            return side/2 + self.edges.get(bottem).spacing(), side, side/2
        else:
            return side/2, side, side/2
