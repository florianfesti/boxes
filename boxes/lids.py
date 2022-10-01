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

class _ChestLid(Boxes):

    def getR(self, x, angle=0):
        t = self.thickness
        d = x - 2*math.sin(math.radians(angle)) * (3*t)

        r = d / 2.0 / math.cos(math.radians(angle))
        return r

    def side(self, x, angle=0, move="", label=""):
        if "a" not in self.edges:
            s = edges.FingerJointSettings(self.thickness, True,
                                          finger=1.0, space=1.0)
            s.edgeObjects(self, "aA.")

        t = self.thickness
        r = self.getR(x, angle)
        if self.move(x+2*t, 0.5*x+3*t, move, True, label=label):
            return

        self.moveTo(t, 0)
        self.edge(x)
        self.corner(90+angle)
        self.edges["a"](3*t)
        self.corner(180-2*angle, r)
        self.edges["a"](3*t)
        self.corner(90+angle)

        self.move(x+2*t, 0.5*x+3*t, move, False, label=label)

    def top(self, x, y, angle=0, move=None, label=""):
        if "a" not in self.edges:
            s = edges.FingerJointSettings(self.thickness, True,
                                          finger=1.0, space=1.0)
            s.edgeObjects(self, "aA.")

        t = self.thickness
        l = math.radians(180-2*angle) * self.getR(x, angle)

        tw = l + 6*t
        th = y+2*t

        if self.move(tw, th, move, True, label=label):
            return

        self.edges["A"](3*t)
        self.edges["X"](l, y+2*t)
        self.edges["A"](3*t)
        self.corner(90)
        self.edge(y+2*t)
        self.corner(90)
        self.edges["A"](3*t)
        self.edge(l)
        self.edges["A"](3*t)
        self.corner(90)
        self.edge(y+2*t)
        self.corner(90)

        self.move(tw, th, move, label=label)

    def drawAddOnLid(self, x, y, style):
        if style == "flat":
            self.rectangularWall(x, y, "eeee", move="right", label="lid bottom")
            self.rectangularWall(x, y, "EEEE", move="up", label="lid top")
        elif style == "chest":
            self.side(x, move="right", label="lid right")
            self.side(x, move="up", label="lid left")
            self.side(x, move="left only", label="invisible")
            self.top(x, y, move="up", label="lid top")
        else:
            return False
        return True

class _TopEdge(Boxes):

    def addTopEdgeSettings(self, fingerjoint={}, stackable={}, hinge={},
                           cabinethinge={}, lid={}, click={},
                           roundedtriangle={}, mounting={}, handle={}):
        self.addSettingsArgs(edges.FingerJointSettings, **fingerjoint)
        self.addSettingsArgs(edges.StackableSettings, **stackable)
        self.addSettingsArgs(edges.HingeSettings, **hinge)
        self.addSettingsArgs(edges.CabinetHingeSettings, **cabinethinge)
        self.addSettingsArgs(edges.LidSettings, **lid)
        self.addSettingsArgs(edges.ClickSettings, **click)
        self.addSettingsArgs(edges.RoundedTriangleEdgeSettings, **roundedtriangle)
        self.addSettingsArgs(edges.MountingSettings, **mounting)
        self.addSettingsArgs(edges.HandleEdgeSettings, **handle)

    def topEdges(self, top_edge):
        """Return top edges belonging to given main edge type
        as a list containing edge for left, back, right, front.
        """
        tl = tb = tr = tf = self.edges.get(top_edge, self.edges["e"])

        if tl.char == "i":
            tb = tf = "e"
            tr = "j"
        elif tl.char == "k":
            tb = tf = "e"
        elif tl.char == "L":
            tl = "M"
            tb = "e"
            tr = "N"
        elif tl.char == "v":
            tb = tr = tf = "e"
        elif tl.char == "t":
            tl = tr = "e"
        elif tl.char == "G":
            tl = tb = tr = tf = "e"
            if self.edges["G"].settings.side == edges.MountingSettings.PARAM_LEFT:
                tl = "G"
            elif self.edges["G"].settings.side == edges.MountingSettings.PARAM_RIGHT:
                tr = "G"
            elif self.edges["G"].settings.side == edges.MountingSettings.PARAM_FRONT:
                tf = "G"
            else: #PARAM_BACK
                tb = "G"
        elif tl.char == "y":
            tl = tb = tr = tf = "e"
            if self.edges["y"].settings.on_sides == True:
                tl = tr = "y"
            else:
                tb = tf = "y"
        elif tl.char == "Y":
            tl = tb = tr = tf = "h"
            if self.edges["Y"].settings.on_sides == True:
                tl = tr = "Y"
            else:
                tb = tf = "Y"
        return [tl, tb, tr, tf]

    def drawLid(self, x, y, top_edge, bedBolts=[None, None]):
        d2, d3 = bedBolts
        if top_edge == "c":
            self.rectangularWall(x, y, "CCCC", bedBolts=[d2, d3, d2, d3], move="up", label="top")
        elif top_edge == "f":
            self.rectangularWall(x, y, "FFFF", move="up", label="top")
        elif top_edge in "FhŠY":
            self.rectangularWall(x, y, "ffff", move="up", label="top")
        elif top_edge == "L":
            self.rectangularWall(x, y, "nlmE", move="up", label="lid top")
        elif top_edge == "i":
            self.rectangularWall(x, y, "IEJe", move="up", label="lid top")
        elif top_edge == "k":
            outset =  self.edges["k"].settings.outset
            self.edges["k"].settings.setValues(self.thickness, outset=True)
            lx = x/2.0-0.1*self.thickness
            self.edges['k'].settings.setValues(self.thickness, grip_length=5)
            self.rectangularWall(lx, y, "IeJe", move="right", label="lid top left")
            self.rectangularWall(lx, y, "IeJe", move="up", label="lid top right")
            self.rectangularWall(lx, y, "IeJe", move="left only", label="invisible")
            self.edges["k"].settings.setValues(self.thickness, outset=outset)
        elif top_edge == "S":
            self.rectangularWall(x, y, "ffff", move="up", label="lid top")
            self.rectangularWall(x, 0, "sFeF", move="up", label="lid top left")
            self.rectangularWall(x, 0, "sFeF", move="up", label="lid top right")
            self.rectangularWall(y, 0, "sfef", move="up", label="lid top front")
            self.rectangularWall(y, 0, "sfef", move="up", label="lid top back")
        elif top_edge == "v":
            self.rectangularWall(x, y, "VEEE", move="up", label="lid top")
            self.edges["v"].parts(move="up")
        else:
            return False
        return True

