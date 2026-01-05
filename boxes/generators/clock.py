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

class Clock(Boxes):
    """Clock (old style with clock hands)"""

    ui_group = "Misc"
    description = """
A simple round clock for mounting a classical clock mechanism behind it, with three legs

![back](static/samples/Clock-2.jpg)
![side](static/samples/Clock-3.jpg)
"""

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.argparser.add_argument(
            "--ClockHandsMaxLength",  action="store", type=float, default=70.0,
            help="Length of the longest clock hand (from the central axis) in mm")
        self.argparser.add_argument(
            "--ExternalRadius",  action="store", type=float, default=100.0,
            help="External radius of the clock in mm")
        self.argparser.add_argument(
            "--BackLegDistance",  action="store", type=float, default=50.0,
            help="Distance between the front plate and the back leg in mm")
        self.argparser.add_argument(
            "--Margin",  action="store", type=float, default=2.0,
            help="Margin between clock hands and external frame in mm")
        self.argparser.add_argument(
            "--NeedlesAxisHoleDiameter",  action="store", type=float, default=8.0,
            help="Diameter of the needles axis hole in mm")
        self.argparser.add_argument(
            "--HourLines",  action="store", type=float, default=0.08,
            help="Length of the hour lines as fraction of the dial radius")
        self.argparser.add_argument(
            "--MinuteLines",  action="store", type=float, default=0.04,
            help="Length of the minute lines as fraction of the dial radius")
        self.argparser.add_argument(
            "--NumberStyle",  action="store", type=str, default="Roman",
            choices=("None", "Arabic", "Roman"),
            help="Style of the hour numbers")
        self.argparser.add_argument(
            "--FontSize",  action="store", type=float, default=0.12,
            help="Hight of the hour numbers as fraction of the dial radius")

    def roman(self, i : int):
        if i > 8:
            r = "X"
            i -= 10
        elif i > 3:
            r = "V"
            i -= 5
        else:
            r = ""

        if i >= 0:
            r += "I" * i
        else:
            r = "I" * -i + r
        return r

    def mainPlate(self, move=None, label=""):
        t = self.thickness
        Re = self.ExternalRadius
        Ri = self.ClockHandsMaxLength + self.Margin
        Rm = (Re+Ri)/2
        Af = math.pi/6 # angle of the front feet from the vertical
        Ab = math.pi/6 # angle of the bottom back foot support from the vertical
        At = math.pi/3 # angle of the top back foot support from the vertical
        if self.move(Re*2, Re*2, move, True):
            return
        #holes for back leg support
        self.rectangularHole(Re - (Rm * math.sin(Ab)), Re - (Rm * math.cos(Ab)), t - self.burn, t - self.burn)
        self.rectangularHole(Re + (Rm * math.sin(Ab)), Re - (Rm * math.cos(Ab)), t - self.burn, t - self.burn)
        self.rectangularHole(Re - (Rm * math.sin(At)), Re - (Rm * math.cos(At)), t - self.burn, t - self.burn)
        self.rectangularHole(Re + (Rm * math.sin(At)), Re - (Rm * math.cos(At)), t + self.burn, t - self.burn)

        #hole for the needles
        self.hole(Re, Re, d=self.NeedlesAxisHoleDiameter)

        #main shape
        self.circle(Re, Re, Re)


        # etchings

        # ring location
        self.set_source_color(Color.ETCHING)
        self.circle(Re, Re, r=Ri)

        # dial design

        self.moveTo(Re, Re)
        fontsize = self.FontSize * Ri
        for i in range(60):
            with self.saved_context():
                self.moveTo(0, 0, i*360/60)
                self.moveTo(Ri, 0, 180)
                self.set_source_color(Color.ETCHING)
                if i % 5:
                    self.edge(self.MinuteLines*Ri)
                else:
                    self.edge(self.HourLines*Ri)
                    if self.NumberStyle != "None":
                        self.moveTo(fontsize*0.7, 0, -i*6-180)
                        nr = int(14-(i/5))%12+1
                        if self.NumberStyle == "Roman":
                            nr = self.roman(nr)
                        else:
                            nr = str(nr)
                        self.text(nr, y=-0.1*fontsize, align="middle center",
                                  fontsize=fontsize, color=Color.ETCHING)
        self.ctx.stroke()
        # move plate
        self.move(Re*2, Re*2, move, label=label)

    def frontRing(self, move=None, label=""):
        Re = self.ExternalRadius
        Ri = self.ClockHandsMaxLength + self.Margin
        if self.move(Re*2, Re*2, move, True):
            return
        self.hole(Re, Re, r=Ri)
        self.circle(Re, Re, Re)
        # move plate
        self.move(Re*2, Re*2, move, label=label)

    def frontLegs(self, move=None, label=""):
        t = self.thickness
        Re = self.ExternalRadius
        Ri = self.ClockHandsMaxLength + self.Margin
        Rm = (Re+Ri)/2
        Tf = (Re-Ri)/2 # foot thickness
        Af = math.pi/6 # angle of the front feet from the vertical
        Afd = Af*180/math.pi
        Ab = math.pi/6 # angle of the bottom back foot support from the vertical
        At = math.pi/3 # angle of the top back foot support from the vertical
        if self.move(Tf*4 + Rm * (1 - math.cos(Af)) / math.sin(Af) + Rm * 2 * math.sin(Ab) - t*3, Tf*2 + Rm * (1 - math.cos(Af)) + t*2 + Rm * (math.cos(Ab) - math.cos(At)), move, True):
            return

        self.moveTo(Tf,0)
        self.polyline(Tf*2, [90 - Afd, Tf/2], Tf + Rm * (1 - math.cos(Af)) / math.cos(Af), -90 + Afd, Rm * 2 * math.sin(Ab) - t - Tf*2,
                            -90 + Afd, Tf + Rm * (1 - math.cos(Af)) / math.cos(Af), [90 - Afd, Tf/2], Tf*2, [180, Tf/2],
                            Tf, [-90 + Afd, Tf/2], Tf + Rm * (1 - math.cos(Af)) / math.cos(Af), 90 - Afd, t, -90,
                            t + Rm * (math.cos(Ab) - math.cos(At)), 90, Rm * 2 * math.sin(Ab) - t*3, 90, t + Rm * (math.cos(Ab) - math.cos(At)),
                            -90, t, 90 - Afd, Tf + Rm * (1 - math.cos(Af)) / math.cos(Af), [-90 + Afd, Tf/2], Tf, [180, Tf/2])

        # move plate
        self.move(Tf*4 + Rm * (1 - math.cos(Af)) / math.sin(Af) + Rm * 2 * math.sin(Ab) - t*3, Tf*2 + Rm * (1 - math.cos(Af)) + t*2 + Rm * (math.cos(Ab) - math.cos(At)), move, label=label)

    def backLeg(self, move=None, label=""):
        t = self.thickness
        Re = self.ExternalRadius
        Ri = self.ClockHandsMaxLength + self.Margin
        Rm = (Re+Ri)/2
        Tf = (Re-Ri)/2 # foot thickness
        Af = math.pi/6 # angle of the front feet from the vertical
        Ab = math.pi/6 # angle of the bottom back foot support from the vertical
        At = math.pi/3 # angle of the top back foot support from the vertical
        if self.move(t*2 + Tf*3 + Rm * (1 - math.cos(Af)) + Rm * (math.cos(Ab) - math.cos(At)), t*2, move, True):
            return

        self.polyline(t, 90 + self.burn/2, t, -90, t - self.burn, -90, t, 90, Rm * (math.cos(Ab) - math.cos(At)) - t + self.burn, 90,
                        t, -90, t - self.burn, -90, t, 90, Tf*2 - t + Rm * (1 - math.cos(Af)) + self.burn/2, [180, t],
                        t*2 + Tf*2 - t + Rm * (1 - math.cos(Af)) + Rm * (math.cos(Ab) - math.cos(At)), 90, t*2, 90)

        # move plate
        self.move(t*2 + Tf*3 + Rm * (1 - math.cos(Af)) + Rm * (math.cos(Ab) - math.cos(At)), t*2, move, label=label)

    def legsSupport(self, width, move=None, label=""):
        t = self.thickness
        Re = self.ExternalRadius
        Ri = self.ClockHandsMaxLength + self.Margin
        Rm = (Re+Ri)/2
        Af = math.pi/6 # angle of the front feet from the vertical
        Ab = math.pi/6 # angle of the bottom back foot support from the vertical
        At = math.pi/3 # angle of the top back foot support from the vertical
        h = self.BackLegDistance
        Rc = min(width/2, h - t*2)
        if self.move(width + t, h+t*3, move, True):
            return

        self.polyline(t, 90, t, -90, t, 90, t, -90, width - t*3, -90, t, 90, t, -90, t, 90, t, 90, h+t*2 - Rc, [90, Rc],
                        width/2 + self.burn/2 - Rc, 90, t, -90, t - self.burn, -90,
                        t, 90, width/2 + self.burn/2 - Rc, [90, Rc], h+t*2 - Rc, 90)

        # move plate
        self.move(width + t, h+t*3, move, label=label)

    def render(self):
        t = self.thickness
        Re = self.ExternalRadius
        Ri = self.ClockHandsMaxLength + self.Margin
        Rm = (Re+Ri)/2
        Af = math.pi/6 # angle of the front feet from the vertical
        Ab = math.pi/6 # angle of the bottom back foot support from the vertical
        At = math.pi/3 # angle of the top back foot support from the vertical
        FootLen = (Re * (1 - math.sin(Af)) + t*2)/math.cos(Af)

        # main plate
        self.mainPlate("up", "main plate")

        # front ring
        self.frontRing("up", "front ring")

        # legs and support plates
        self.frontLegs("up", "front legs")
        self.backLeg("up", "back leg")
        self.legsSupport(Rm * 2 * math.sin(At), "up", "top leg support")
        self.legsSupport(Rm * 2 * math.sin(Ab), "up", "bottom leg support")
