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
from boxes.lids import _TopEdge

class NightLightBox(_TopEdge):
    """Simple decorative lamp with creatively laser cut plates"""

    ui_group = "Misc"
    description = "This is a simple light box with a closed compartment for electronics and the backlighting."

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=1)
        self.addSettingsArgs(edges.StackableSettings)
        self.addSettingsArgs(edges.HingeSettings, outset=True, pinwidth=0.4, style="flush", axle=2.5)
        self.argparser.add_argument(
            "--BoxStyle",  action="store", type=str, default="large face",
            choices=["minimalist", "large face", "extra customizable face"],
            help="style of the front lock")
        self.argparser.add_argument(
            "--PlateVisibleWidth",  action="store", type=float, default=150.0,
            help="width of the window in the front panel in mm")
        self.argparser.add_argument(
            "--PlateVisibleHeight",  action="store", type=float, default=75.0,
            help="height of the window in the front panel in mm")
        self.argparser.add_argument(
            "--WoodPlatesCount",  action="store", type=int, default=3,
            help="Number of decorative wood plates")
        self.argparser.add_argument(
            "--WoodPlateThickness",  action="store", type=float, default=5.0,
            help="Thickness of the wood plates in mm")
        self.argparser.add_argument(
            "--DiffuserPlateThickness",  action="store", type=float, default=5.0,
            help="Thickness of the background acrylic diffuser plate in mm")
        self.argparser.add_argument(
            "--BackgroundDepth",  action="store", type=float, default=40.0,
            help="Depth of the background zone for the electronics and LEDs in mm")
        self.argparser.add_argument(
            "--InterPlateSpacing",  action="store", type=float, default=10,
            help="Space between the decorative plates in mm")
        self.argparser.add_argument(
            "--hooks",  action="store", type=boolarg, default=False,
            help="add hooks to decorative plates (allowing one sides plates)")
        self.argparser.add_argument(
            "--Margin",  action="store", type=float, default=0.5,
            help="Margin for moving parts in mm")
        DiffuserPlateLock_group = self.argparser.add_argument_group("Night lightbox diffuser plate lock to prevent unwanted access to the electronics")
        DiffuserPlateLock_group.add_argument(
            "--DiffuserPlateTLockScrewDiameter",  action="store", type=float, default=3.0,
            help="Diameter of the background acrylic diffuser plate locking screw hole in mm")
        DiffuserPlateLock_group.add_argument(
            "--DiffuserPlateTLockScrewLength",  action="store", type=float, default=20.0,
            help="Length of the background acrylic diffuser plate locking screw in mm")
        DiffuserPlateLock_group.add_argument(
            "--DiffuserPlateTLockNutThickness",  action="store", type=float, default=2.1,
            help="Thickness of the background acrylic diffuser plate locking nut in mm")
        DiffuserPlateLock_group.add_argument(
            "--DiffuserPlateTLockNutWidth",  action="store", type=float, default=5.1,
            help="Width of the background acrylic diffuser plate locking nut in mm")
        BackSideOptions_group = self.argparser.add_argument_group("Night lightbox options for the back side (holes for connectors, marking)")
        BackSideOptions_group.add_argument(
            "--BackExtraHoles",  action="store", type=str, default="R 20 15 11.5 8\nC 11.58 15 3\nC 28.42 15 3",
            help="extra holes for connectors or buttons ; enter one line per hole ; first parameter should be R for rectangle or C for circle ; then X and Y position for the center of the hole, and then the X and Y size of the rectangle or the circle diameter, all in mm ; parameters should be separated by spaces")



    def railSlots(self, xSize, ySize):
        # to be updated
        t = self.thickness
        self.fingerHolesAt(t*1.5, self.InterPlateSpacing - t - self.Margin/2, t*2 + self.DiffuserPlateThickness + (self.InterPlateSpacing + self.WoodPlateThickness) * self.WoodPlatesCount)
        self.fingerHolesAt(xSize - (t*1.5), self.InterPlateSpacing - t - self.Margin/2, t*2 + self.DiffuserPlateThickness + (self.InterPlateSpacing + self.WoodPlateThickness) * self.WoodPlatesCount)

    def woodPlate(self, move=None, label=""):
        t = self.thickness
        if self.move(self.PlateVisibleWidth + t*(6 if self.BoxStyle == "minimalist" else 10), self.PlateVisibleHeight + t*(4 if self.BoxStyle == "minimalist" else 8), move, True):
            return
        # visible zone
        if self.BoxStyle == "minimalist" :
            self.rectangularHole(t*3, t*2, self.PlateVisibleWidth, self.PlateVisibleHeight, center_x=False, center_y=False, color=Color.ANNOTATIONS)
        else :
            self.rectangularHole(t*5, t*4, self.PlateVisibleWidth, self.PlateVisibleHeight, center_x=False, center_y=False, color=Color.ANNOTATIONS)
        self.moveTo(t + self.Margin/2, 0, 0)
        # bottom
        self.polyline(t - self.Margin, 90, t + self.Margin, -90, t + self.Margin, -90, t + self.Margin, 90,
                        self.PlateVisibleWidth + t*(0 if self.BoxStyle == "minimalist" else 4) - self.Margin, 90,
                        t + self.Margin, -90, t + self.Margin, -90, t + self.Margin, 90, t - self.Margin, 90)
        # right side
        self.polyline(self.PlateVisibleHeight + t*(2 if self.BoxStyle == "minimalist" else 6) + self.Margin, -90,
                        t + self.Margin/2)
        if self.hooks:
            self.polyline(0, -90, t, 90, 0, (90, t), t, (90, t))
        else:
            self.polyline(0, 90, t*2 - self.Margin*2, 90)
        # top
        self.polyline(self.PlateVisibleWidth + t*(6 if self.BoxStyle == "minimalist" else 10))
        # left side
        if self.hooks:
            self.polyline(0, (90, t), t, (90, t), 0, 90, t, -90)
        else:
            self.polyline(0, 90, t*2 - self.Margin*2, 90)
        self.polyline(t + self.Margin/2, -90,
                        self.PlateVisibleHeight + t*(2 if self.BoxStyle == "minimalist" else 6) + self.Margin, 90)
        # move plate
        self.move(self.PlateVisibleWidth + t*(6 if self.BoxStyle == "minimalist" else 10), self.PlateVisibleHeight + t*(4 if self.BoxStyle == "minimalist" else 8), move, label=label)

    def boltAndScrewHole(self):
        t = self.thickness
        self.polyline(0, 90, t, 90, self.DiffuserPlateTLockNutWidth/2 - self.DiffuserPlateTLockScrewDiameter/2, -90, self.DiffuserPlateTLockNutThickness, -90,
                        self.DiffuserPlateTLockNutWidth/2 - self.DiffuserPlateTLockScrewDiameter/2, 90, self.DiffuserPlateTLockScrewLength - self.DiffuserPlateTLockNutThickness - t*2, -90,
                        self.DiffuserPlateTLockScrewDiameter, -90, self.DiffuserPlateTLockScrewLength - self.DiffuserPlateTLockNutThickness - t*2, 90,
                        self.DiffuserPlateTLockNutWidth/2 - self.DiffuserPlateTLockScrewDiameter/2, -90, self.DiffuserPlateTLockNutThickness, -90,
                        self.DiffuserPlateTLockNutWidth/2 - self.DiffuserPlateTLockScrewDiameter/2, 90, t, 90)

    def diffuserPlate(self, move=None, label=""):
        t = self.thickness
        if self.move(self.PlateVisibleWidth + t*(4 if self.BoxStyle == "minimalist" else 8), self.PlateVisibleHeight + t*(4 if self.BoxStyle == "minimalist" else 8), move, True):
            return
        # bottom
        self.polyline(t - self.Margin, 90, t + self.Margin, -90, t + self.Margin, -90, t + self.Margin, 90,
                        self.PlateVisibleWidth + t*(0 if self.BoxStyle == "minimalist" else 4) - self.Margin, 90,
                        t + self.Margin, -90, t + self.Margin, -90, t + self.Margin, 90, t - self.Margin, 90)
        # right side
        self.edge(t*6 - self.DiffuserPlateTLockScrewDiameter/2)
        self.boltAndScrewHole()
        self.polyline(self.PlateVisibleHeight + t*(-2 if self.BoxStyle == "minimalist" else 2) - self.Margin - self.DiffuserPlateTLockScrewDiameter/2, 90)
        # top
        self.polyline(self.PlateVisibleWidth + t*(4 if self.BoxStyle == "minimalist" else 8) - self.Margin, 90)
        # left side
        self.edge(self.PlateVisibleHeight + t*(-2 if self.BoxStyle == "minimalist" else 2) - self.Margin - self.DiffuserPlateTLockScrewDiameter/2)
        self.boltAndScrewHole()
        self.polyline(t*6 - self.DiffuserPlateTLockScrewDiameter/2, 90)
        # move plate
        self.move(self.PlateVisibleWidth + t*(4 if self.BoxStyle == "minimalist" else 8), self.PlateVisibleHeight + t*(4 if self.BoxStyle == "minimalist" else 8), move, label=label)

    def elecCompartmentTop(self, move=None, label=""):
        t = self.thickness
        if self.move(t * 4 + self.PlateVisibleWidth + self.Margin, self.BackgroundDepth - t*2.5 - self.Margin, move, True):
            return
        # bottom
        self.polyline(t * (4 if self.BoxStyle == "minimalist" else 8) + self.PlateVisibleWidth + self.Margin, 90)
        # right side
        self.edge(t*1.5)
        self.edges["f"](self.BackgroundDepth - t*5 - self.Margin)
        self.corner(90)
        # top
        self.polyline(t * (4 if self.BoxStyle == "minimalist" else 8) + self.PlateVisibleWidth + self.Margin, 90)
        # left side
        self.edges["f"](self.BackgroundDepth - t*5 - self.Margin)
        self.polyline(t*1.5, 90)
        # move plate
        self.move(t * 4 + self.PlateVisibleWidth + self.Margin, self.BackgroundDepth - t*2.5 - self.Margin, move, label=label)

    def side(self, ySize, hSize, move=None, label=""):
        t = self.thickness
        be = self.edges["s"] # bottom edge
        if self.move(ySize + t, hSize + t*4, move, True):
            return
        # rectangular hole for background guiding
        if self.BoxStyle == "minimalist" :
            self.rectangularHole(ySize - self.BackgroundDepth - self.DiffuserPlateThickness - t - self.Margin*1.5, self.PlateVisibleHeight + t*4, t, t, center_x=False, center_y=False)
        else :
            self.rectangularHole(ySize - self.BackgroundDepth - self.DiffuserPlateThickness - t - self.Margin*1.5, self.PlateVisibleHeight + t*8, t, t, center_x=False, center_y=False)
        # round hole for background lock screw
        self.hole(ySize - self.BackgroundDepth - self.DiffuserPlateThickness/2 - self.Margin/2, t*10, self.DiffuserPlateTLockScrewDiameter/2)
        # bottom
        be(ySize)
        self.corner(90)
        # right side
        self.edge(be.endwidth())
        self.edges["f"](hSize)
        self.corner(90)
        # top
        self.edges["i"].settings.style = "flush_inset"
        self.edges["i"](t*5)
        self.edges["F"](self.BackgroundDepth - t*5 - self.Margin/2)
        self.polyline(self.DiffuserPlateThickness + self.InterPlateSpacing + self.Margin/2, 90)
        for i in range(self.WoodPlatesCount):
            self.polyline(t*2 + self.Margin, -90, self.WoodPlateThickness + self.Margin, -90,
                        t*2 + self.Margin, 90, self.InterPlateSpacing - self.Margin, 90)
        # left side
        self.edges["f"](hSize)
        self.edge(be.startwidth())
        self.corner(90)
        # move plate
        self.move(ySize + t, hSize + t*8, move, label=label)

    def rail(self, move=None, label=""):
        t = self.thickness
        if self.move(self.WoodPlatesCount * (self.InterPlateSpacing + self.WoodPlateThickness) + self.DiffuserPlateThickness + t*2, t*3, move, True):
            return
        # bottom
        self.edges["f"](t*2 + self.DiffuserPlateThickness + (self.InterPlateSpacing + self.WoodPlateThickness) * self.WoodPlatesCount)
        self.corner(90)
        # right side
        self.polyline(t*2, 90)
        # top
        self.polyline(t - self.Margin/2, 90)
        for i in range(self.WoodPlatesCount):
            self.polyline(t + self.Margin, -90, self.WoodPlateThickness + self.Margin, -90,
                        t + self.Margin, 90, self.InterPlateSpacing - self.Margin, 90)
        self.polyline(t + self.Margin, -90, self.DiffuserPlateThickness + self.Margin, -90,
                        t + self.Margin, 90, t - self.Margin/2, 90)
        # left side
        self.polyline(t*2, 90)
        # move plate
        self.move(self.WoodPlatesCount * (self.InterPlateSpacing + self.WoodPlateThickness) + self.DiffuserPlateThickness + t*2, t*3, move, label=label)

    def backExtraHoles(self):
        # for each line, make a hole
        for line in self.BackExtraHoles.split("\n") :
            holeParams=line.split(" ")
            # rectangular hole
            if line[0] == "R" :
                self.rectangularHole(float(holeParams[1]), float(holeParams[2]), float(holeParams[3]), float(holeParams[4]))
            # round hole
            elif line[0] == "C" :
                self.hole(float(holeParams[1]), float(holeParams[2]), float(holeParams[3])/2)

    def render(self):
        t = self.thickness
        # define box inner depth
        y = self.BackgroundDepth + self.DiffuserPlateThickness + (self.WoodPlateThickness + self.InterPlateSpacing) * self.WoodPlatesCount + self.InterPlateSpacing #+ t*2
        if self.BoxStyle == "minimalist" :
            # define box inner width
            x = t * 4 + self.PlateVisibleWidth + self.Margin
            # define box inner height
            h = self.PlateVisibleHeight + t * 4 + self.Margin
        else :
            # define box inner width
            x = t * 8 + self.PlateVisibleWidth + self.Margin
            # define box inner height
            h = self.PlateVisibleHeight + t * 8 + self.Margin

        self.ctx.save()

        # sides
        self.side(y, h, move="mirror", label="left")
        self.side(y, h, move="left up", label="right")

        #rails
        self.rail(move="up", label="rail")
        self.rail(move="up mirror", label="rail")

        # floor
        self.rectangularWall(x, y, "ffff", callback=[lambda:self.railSlots(x, y)], move="up", label="bottom")

        # back
        self.rectangularWall(x, h, "sFeF", callback=[lambda:self.backExtraHoles()], move="up", label="back")

        # front and optional customizable front face
        if self.BoxStyle == "extra customizable face" :
            self.rectangularWall(x, h, "sFeF", callback=[lambda:self.rectangularHole(self.PlateVisibleWidth/2 + t*4 + self.Margin/2,self.PlateVisibleHeight/2 + t*4,self.PlateVisibleWidth, self.PlateVisibleHeight),
                                                                        lambda:self.rectangularHole(t*1.5, t*1.5, t, t),
                                                                        lambda:self.rectangularHole(self.PlateVisibleWidth/2 + t*4 + self.Margin/2, t*1.5, t, t),
                                                                        lambda:self.rectangularHole(self.PlateVisibleHeight + t*6.5 + self.Margin, t*1.5, t, t)], move="up", label="front")
            self.rectangularWall(x, h, "EEEE", callback=[lambda:self.rectangularHole(self.PlateVisibleWidth/2 + t*4 + self.Margin/2,self.PlateVisibleHeight/2 + t*4,self.PlateVisibleWidth, self.PlateVisibleHeight, color=Color.ANNOTATIONS),
                                                                        lambda:self.rectangularHole(t*1.5, t*1.5, t, t),
                                                                        lambda:self.rectangularHole(self.PlateVisibleWidth/2 + t*4 + self.Margin/2, t*1.5, t, t),
                                                                        lambda:self.rectangularHole(self.PlateVisibleHeight + t*6.5 + self.Margin, t*1.5, t, t)], move="up", label="customizable face")
            self.rectangularWall(t*2, t, move="up")
            self.rectangularWall(t*2, t, move="up")
        elif self.BoxStyle == "minimalist" :
            self.rectangularWall(x, h, "sFeF", callback=[lambda:self.rectangularHole(self.PlateVisibleWidth/2 + t*2,self.PlateVisibleHeight/2 + t*2,self.PlateVisibleWidth, self.PlateVisibleHeight)], move="up", label="front")
        else:
            self.rectangularWall(x, h, "sFeF", callback=[lambda:self.rectangularHole(self.PlateVisibleWidth/2 + t*4,self.PlateVisibleHeight/2 + t*4,self.PlateVisibleWidth, self.PlateVisibleHeight)], move="up", label="front")

        # electronics compartment top
        self.elecCompartmentTop(move="up", label="elec. comp.")

        # difuser guides
        self.rectangularWall(t*2, t, "eeee", move="up", label="guide")
        self.rectangularWall(t*2, t, "eeee", move="up", label="guide")

        # top / lid
        self.drawLid(y - t, x, "i")

        # diffuser plate
        self.diffuserPlate(move="up", label="Diffuser")

        # wood plates with horizontal LEDs
        for i in range(self.WoodPlatesCount):
            self.woodPlate(move="up", label="Insert cut and\nengraved art here")
