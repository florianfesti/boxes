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

class PirateChest(Boxes):
    """Box with polygon lid with chest hinges."""

    description = """Do not assemble sides before attaching the lid! 
    Hinge of the lid has to be placed first because it is impossible 
    to get it in position without removing the side wall. The lid can 
    be a bit tricky to assemble. Keep track of how the parts fit together. 
    Part with label "lid back" is placed in the hinges"""

    ui_group = "Box"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings, finger=1.0,space=1.0)
        self.addSettingsArgs(edges.HingeSettings)

        self.buildArgParser("x", "y", "h", "outside")
        self.argparser.add_argument(
            "--n",  action="store", type=int, default=5,
            help="number of sides on the lid. n ≥ 3")


    def render(self):
        # adjust to the variables you want in the local scope
        x, y, h = self.x, self.y, self.h
        if self.outside:
            x = self.adjustSize(x)
            y = self.adjustSize(y)
            h = self.adjustSize(h, "f", False)
        t = self.thickness
        n = self.n

        if (n < 3):
            raise ValueError("number of sides on the lid must be greater or equal to 3 (got %i)" % n)
        
        hy = self.edges["O"].startwidth()
        h -= hy
        if (h < 0):
            raise ValueError("box to low to allow for hinge (%i)" % h)

        # create edge for non 90 degree joints in the lid
        fingerJointSettings = copy.deepcopy(self.edges["f"].settings)
        fingerJointSettings.setValues(self.thickness, angle=180./(n-1))
        fingerJointSettings.edgeObjects(self, chars="gGH")

        # render all parts
        self.ctx.save()

        self.rectangularWall(x, y, "FFFF", move="up", label="Bottom")
        frontlid, toplids, backlid = self.topside(y, n = n, move="only", bottom='P')

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

        e1 = edges.CompoundEdge(self, "Fe", (h, hy))
        e2 = edges.CompoundEdge(self, "eF", (hy, h))
        e_back = ("f", e1, "e", e2)

        with self.saved_context():
            self.rectangularWall(x, h+hy, e_back, move="right", label="back") # extend back to correct height
            self.rectangularWall(0, h, "ePee", move="right only")
            self.rectangularWall(y, h, "ffOf", ignore_widths=[2], move="right", label="left")
        self.rectangularWall(x, h, "fFOF", move="up only")
        self.rectangularWall(x, 0, "peee", move="up only")

        self.topside(y, n = n, move="right", bottom='p', label="lid left")
        self.topside(y, n = n, move="right", bottom='P', label="lid right")


    def topside(self, y, n, bottom, move=None, label=""):
        radius, hp, side  = self.regularPolygon((n - 1) * 2, h=y/2.0)

        tx = y + 2 * self.edges.get('f').spacing()
        lidheight = hp if n % 2 else radius
        ty = lidheight + self.edges.get('f').spacing() + self.edges.get(bottom).spacing()
        
        if self.move(tx, ty, move, before=True):
            return side/2 + self.edges.get(bottom).spacing(), side, side/2

        self.moveTo(self.edges.get('f').margin(), self.edges.get(bottom).margin())

        self.edges.get(bottom)(y)

        self.corner(90)
        if bottom == 'p':
            self.edges.get('f')(side/2 + self.edges.get(bottom).spacing())
        else:
            self.edges.get('f')(side/2)
        
        self.corner(180 / (n - 1))
        for _ in range(n-2):
            self.edges.get('f')(side)
            self.corner(180 / (n - 1))

        if bottom == 'P':
            self.edges.get('f')(side/2 + self.edges.get(bottom).spacing())
        else:
            self.edges.get('f')(side/2)
        
        self.corner(90)

        self.move(tx, ty, move, label=label)

        return side/2 + self.edges.get(bottom).spacing(), side, side/2
