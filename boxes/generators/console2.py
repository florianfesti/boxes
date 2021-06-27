#!/usr/bin/env python3
# Copyright (C) 2013-2020 Florian Festi
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

class Console2(Boxes):
    """Console with slanted panel and service hatches"""

    ui_group = "Box"

    description = """
This box is designed as a housing for electronic projects. It has hatches that can be re-opened with simple tools. It intentionally cannot be opened with bare hands - if build with thin enough material.

#### Caution
There is a chance that the latches of the back wall or the back wall itself interfere with the front panel or it's mounting frame/lips. The generator does not check for this. So depending on the variant choosen you might need to make the box deeper (increase y parameter) or the panel angle steeper (increase angle parameter) until there is enough room.

It's also possible that the frame of the panel interferes with the floor if the hi parameter is too small.

#### Assembly instructions
The main body is easy to assemble by starting with the floor and then adding the four walls and (if present) the top piece.

If the back wall is removable you need to add the lips and latches. The U-shaped clamps holding the latches in place need to be clued in place without also gluing the latches themselves. Make sure the springs on the latches point inwards and the angled ends point to the side walls as shown here:

![Back wall details](static/samples/Console2-backwall-detail.jpg)

If the panel is removable you need to add the springs with the tabs to the side lips. This photo shows the variant which has the panel glued to the frame:

![Back wall details](static/samples/Console2-panel-detail.jpg)

If space is tight you may consider not glueing the cross pieces in place and remove them after the glue-up. This may prevent the latches of the back wall and the panel from interfereing with each other.

The variant using finger joints only has the two side lips without the cross bars.

#### Re-Opening

The latches at the back wall lock in place when closed. To open them they need to be pressed in and can then be moved aside.

To remove the panel you have to press in the four tabs at the side. It is easiest to push them in and then pull the panel up a little bit so the tabs stay in.
"""

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=.5)
        self.addSettingsArgs(edges.StackableSettings)

        self.buildArgParser(x=100, y=100, h=100, bottom_edge="s",
                            outside=False)
        self.argparser.add_argument(
            "--front_height",  action="store", type=float, default=30,
            help="height of the front below the panel (in mm)")
        self.argparser.add_argument(
            "--angle",  action="store", type=float, default=50,
            help="angle of the front panel (90°=upright)")
        self.argparser.add_argument(
            "--removable_backwall",  action="store", type=boolarg, default=True,
            help="have latches at the backwall")
        self.argparser.add_argument(
            "--removable_panel",  action="store", type=boolarg, default=True,
            help="The panel is held by tabs and can be removed")
        self.argparser.add_argument(
            "--glued_panel",  action="store", type=boolarg, default=True,
            help="the panel is glued and not held by finger joints")

    def borders(self):
        x, y, h, fh = self.x, self.y, self.h, self.front_height
        t = self.thickness

        panel = min((h-fh)/math.cos(math.radians(90-self.angle)),
                    y/math.cos(math.radians(self.angle)))
        top = y - panel * math.cos(math.radians(self.angle))
        h = fh + panel * math.sin(math.radians(self.angle))

        if top>0.1*t:
            borders = [y, 90, fh, 90-self.angle, panel, self.angle, top,
                       90, h, 90]
        else:
            borders = [y, 90, fh, 90-self.angle, panel, self.angle+90, h, 90]
        return borders

    def latch(self, move=None):
        t = self.thickness
        s = 0.1 * t

        tw, th = 8*t, 3*t

        if self.move(tw, th, move, True):
            return
        
        self.moveTo(0, 1.2*t)
        self.polyline(t, -90, .2*t, 90, 2*t, -90, t, 90, t, 90, t, -90, 3*t,
                      90, t, -90, t, 90, t, 90, 2*t, 90, 0.5*t,
                      -94, 4.9*t, 94, .5*t, 86, 4.9*t, -176, 5*t,
                      -90, 1.0*t, 90, t, 90, 1.8*t, 90)

        self.move(tw, th, move)

    def latch_clamp(self, move=None):
        t = self.thickness
        s = 0.1 * t

        tw, th = 4*t, 4*t

        if self.move(tw, th, move, True):
            return

        self.moveTo(0.5*t)
        self.polyline(t-0.5*s, 90, 2.5*t+.5*s, -90, t+s, -90, 2.5*t+.5*s, 90, t-0.5*s, 90,
                      t, -90, 0.5*t, 90, 2*t, 45, 2**.5*t, 45, 2*t, 45, 2**.5*t, 45, 2*t, 90, 0.5*t, -90, t, 90)

        self.move(tw, th, move)

    @restore
    @holeCol
    def latch_hole(self, posx):
        t = self.thickness
        s = 0.1 * t

        self.moveTo(posx, 2*t, 180)

        path = [1.5*t, -90, t, -90, t-0.5*s, 90]
        path = path + [2*t] + list(reversed(path))
        path = path[:-1] + [3*t] + list(reversed(path[:-1]))

        self.polyline(*path)

    def panel_side(self, l, move=None):
        t = self.thickness
        s = 0.1 * t

        tw, th = l, 3*t

        if not self.glued_panel:
            th += t

        if self.move(tw, th, move, True):
            return

        self.rectangularHole(3*t, 1.5*t, 3*t, 1.05*t)
        self.rectangularHole(l-3*t, 1.5*t, 3*t, 1.05*t)
        self.rectangularHole(l/2, 1.5*t, 2*t, t)
        if self.glued_panel:
            self.polyline(*([l, 90, t, 90, t, -90, t, -90, t, 90, t, 90]*2))
        else:
            self.polyline(l, 90, 3*t, 90)
            self.edges["f"](l)
            self.polyline(0, 90, 3*t, 90)
        self.move(tw, th, move)

    def panel_lock(self, l, move=None):
        t = self.thickness

        l -= 4*t
        tw, th = l, 2.5*t

        if self.move(tw, th, move, True):
            return

        end = [l/2-3*t, -90, 1.5*t, (90, .5*t), t, (90, .5*t),
               t, 90, .5*t, -90, 0.5*t, -90, 0, (90, .5*t), 0, 90,]

        self.moveTo(l/2-t, 2*t, -90)
        self.polyline(*([t, 90, 2*t, 90, t, -90] + end + [l] +
                        list(reversed(end))))
        self.move(tw, th, move)

    def panel_cross_beam(self, l, move=None):
        t = self.thickness

        tw, th = l+2*t, 3*t

        if self.move(tw, th, move, True):
            return

        self.moveTo(t, 0)
        self.polyline(*([l, 90, t, -90, t, 90, t, 90, t, -90, t, 90]*2))

        self.move(tw, th, move)

    def side(self, borders, bottom="s", move=None, label=""):

        t = self.thickness
        bottom = self.edges.get(bottom, bottom)
        
        tw =  borders[0] + 2* self.edges["f"].spacing()
        th = borders[-2] + bottom.spacing() + self.edges["f"].spacing()
        if self.move(tw, th, move, True):
            return

        d1 = t * math.cos(math.radians(self.angle))
        d2 = t * math.sin(math.radians(self.angle))
        
        self.moveTo(t, 0)
        bottom(borders[0])
        self.corner(90)
        self.edges["f"](borders[2]+bottom.endwidth()-d1)
        self.edge(d1)
        self.corner(borders[3])
        if self.removable_panel:
            self.rectangularHole(3*t, 1.5*t, 2.5*t, 1.05*t)
        if not self.removable_panel and not self.glued_panel:
            self.edges["f"](borders[4])
        else:
            self.edge(borders[4])
        if self.removable_panel:
            self.rectangularHole(-3*t, 1.5*t, 2.5*t, 1.05*t)
        if len(borders) == 10:
            self.corner(borders[5])
            self.edge(d2)
            self.edges["f"](borders[6]-d2)
        self.corner(borders[-3])
        if self.removable_backwall:
            self.rectangularHole(self.latchpos, 1.55*t, 1.1*t, 1.1*t)
            self.edge(borders[-2]-t)
            self.edges["f"](t+bottom.startwidth())
        else:
            self.edges["f"](borders[-2]+bottom.startwidth())
        self.corner(borders[-1])
        
        self.move(tw, th, move, label=label)
        
    def render(self):
        x, y, h = self.x, self.y, self.h
        t = self.thickness
        bottom = self.edges.get(self.bottom_edge)

        if self.outside:
            self.x = x = self.adjustSize(x)
            self.y = y = self.adjustSize(y)
            self.h = h = self.adjustSize(h, bottom)

        d1 = t * math.cos(math.radians(self.angle))
        d2 = t * math.sin(math.radians(self.angle))

        self.latchpos = latchpos = 6*t

        borders = self.borders()
        self.side(borders, bottom, move="right", label="Left Side")
        self.side(borders, bottom, move="right", label="Right Side")

        self.rectangularWall(borders[0], x, "ffff", move="right", label="Floor")
        self.rectangularWall(
            borders[2]-d1, x, ("F", "e", "F", bottom), ignore_widths=[7, 4],
            move="right", label="Front")

        if self.glued_panel:
            self.rectangularWall(borders[4], x, "EEEE", move="right", label="Panel")
        elif self.removable_panel:
            self.rectangularWall(borders[4], x-2*t, "hEhE", move="right", label="Panel")
        else:
            self.rectangularWall(borders[4], x, "FEFE", move="right", label="Panel")

        if len(borders) == 10:
            self.rectangularWall(borders[6]-d2, x, "FEFe", move="right", label="Top")

        if self.removable_backwall:
            self.rectangularWall(
                borders[-2]-1.05*t, x, "EeEe",
                callback=[
                    lambda:self.latch_hole(latchpos),
                    lambda: self.fingerHolesAt(.5*t, 0, borders[-2]-4.05*t-latchpos),
                    lambda:self.latch_hole(borders[-2]-1.2*t-latchpos),
                    lambda: self.fingerHolesAt(.5*t, 3.05*t+latchpos, borders[-2]-4.05*t-latchpos)],
                move="right",
                label="Back Wall")
            self.rectangularWall(2*t, borders[-2]-4.05*t-latchpos, "EeEf", move="right", label="Guide")
            self.rectangularWall(2*t, borders[-2]-4.05*t-latchpos, "EeEf", move="right", label="Guide")
            self.rectangularWall(t, x, ("F", bottom, "F", "e"),
                                 ignore_widths=[0, 3], move="right", label="Bottom Back")
        else:
            self.rectangularWall(borders[-2], x, ("F", bottom, "F", "e"),
                                 ignore_widths=[0, 3], move="right", label="Back Wall")

        # hardware for panel
        if self.removable_panel:
            if self.glued_panel:
                self.panel_cross_beam(x-2.05*t, "rotated right")
                self.panel_cross_beam(x-2.05*t, "rotated right")

            self.panel_lock(borders[4], "up")
            self.panel_lock(borders[4], "up")
            self.panel_side(borders[4], "up")
            self.panel_side(borders[4], "up")

        # hardware for back wall
        if self.removable_backwall:
            self.latch(move="up")
            self.latch(move="up")
            self.partsMatrix(4, 2, "up", self.latch_clamp)
