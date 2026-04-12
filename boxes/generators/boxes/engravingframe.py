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


class EngravingFrame(Boxes):
    """A frame for an engraving ; can be either standing or hanging, both in portrait or landscape"""

    description = "This box is a frame for an engraving."

    ui_group = "Box"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.argparser.add_argument(
            "--EngravingWidth",  action="store", type=float, default=100.0,
            help="width of the visible part of the engraving in mm")
        self.argparser.add_argument(
            "--EngravingHeight",  action="store", type=float, default=100.0,
            help="height of the visible part of the engraving in mm")
        self.argparser.add_argument(
            "--EngravingThickness",  action="store", type=float, default=5.0,
            help="thickness of the engraving plate (and any acrylic window you may add) in mm")
        self.argparser.add_argument(
            "--Margin",  action="store", type=float, default=1.0,
            help="margin for the engraving plate insertion in mm")
        self.argparser.add_argument(
            "--FrameThickness",  action="store", type=float, default=20.0,
            help="width of the frame in mm")
        self.argparser.add_argument(
            "--FrameOuterCornersRadius",  action="store", type=float, default=5.0,
            help="radius of the frame outer corners in mm")
        self.argparser.add_argument(
            "--FrameInnerCornersRadius",  action="store", type=float, default=5.0,
            help="radius of the frame inner corners in mm")
        self.argparser.add_argument(
            "--AddCoveringFrontPlate",  action="store", type=boolarg, default=True,
            help="Add a covenring front plate to glue (hiding the finger joints)")
        self.argparser.add_argument(
            "--AddDummyFingers",  action="store", type=boolarg, default=False,
            help="Add dummy finger holes and plugs for the unity of the frame (if not covered)")
        self.argparser.add_argument(
            "--BackSupportAngle",  action="store", type=float, default=10.0,
            help="angle of the back support in degrees ; set 0 or negative value to ignore")

    def backplate(self, move, label):
        if self.move(self.EngravingWidth + self.Margin + self.thickness*6, self.EngravingHeight + self.Margin + self.thickness*6, move, True):
            return

        # plate
        self.moveTo(self.thickness)
        self.polyline(self.thickness, 90, self.thickness, -90)
        self.edges["F"](self.EngravingWidth + self.thickness*2 + self.Margin)
        self.polyline(0, -90, self.thickness, 90, self.thickness, 90, self.thickness, -90, self.thickness, 90, self.thickness, 90, self.thickness, -90)
        self.edges["F"](self.EngravingHeight + self.thickness*2 + self.Margin)
        self.polyline(0, -90, self.thickness, 90, self.thickness, 90, self.thickness, -90, self.thickness, 90, self.thickness, 90,
                        self.thickness, -90, self.EngravingWidth + self.thickness*2 + self.Margin, -90, self.thickness, 90, self.thickness, 90,
                        self.thickness, -90, self.thickness, 90, self.thickness, 90, self.thickness, -90)
        self.edges["F"](self.EngravingHeight + self.thickness*2 + self.Margin)
        self.polyline(0, -90, self.thickness, 90, self.thickness, 90, self.thickness, -90, self.thickness, 90)

        # move plate
        self.move(self.EngravingWidth + self.Margin + self.thickness*6, self.EngravingHeight + self.Margin + self.thickness*6, move, label=label)

    def frameplate(self, isCoverPlate, move, label):
        if self.move(self.EngravingWidth + self.FrameThickness * 2, self.EngravingHeight + self.FrameThickness * 2, move, True):
            return

        # central hole
        self.rectangularHole(self.FrameThickness + self.EngravingWidth/2, self.FrameThickness + self.EngravingHeight/2, self.EngravingWidth, self.EngravingHeight, r=self.FrameInnerCornersRadius)

        # finger holes
        if (not isCoverPlate):
            self.fingerHolesAt(self.FrameThickness - self.thickness - self.Margin/2, self.FrameThickness - self.Margin/2 - self.thickness*1.5, self.EngravingWidth + self.thickness*2 + self.Margin, angle=0)
            self.fingerHolesAt(self.FrameThickness - self.Margin/2 - self.thickness*1.5, self.FrameThickness - self.thickness - self.Margin/2, self.EngravingHeight + self.thickness*2 + self.Margin, angle=90)
            self.fingerHolesAt(self.FrameThickness + self.EngravingWidth + self.Margin/2 + self.thickness*1.5, self.FrameThickness - self.thickness - self.Margin/2, self.EngravingHeight + self.thickness*2 + self.Margin, angle=90)
            if (self.AddDummyFingers):
                self.fingerHolesAt(self.FrameThickness - self.thickness - self.Margin/2, self.FrameThickness + self.EngravingHeight + self.Margin/2 + self.thickness*1.5, self.EngravingWidth + self.thickness*2 + self.Margin, angle=0)

        # plate
        self.moveTo (self.FrameOuterCornersRadius)
        self.polyline(self.EngravingWidth + self.FrameThickness * 2 - self.FrameOuterCornersRadius * 2, [90, self.FrameOuterCornersRadius],
                        self.EngravingHeight + self.FrameThickness * 2 - self.FrameOuterCornersRadius * 2, [90, self.FrameOuterCornersRadius],
                        self.EngravingWidth + self.FrameThickness * 2 - self.FrameOuterCornersRadius * 2, [90, self.FrameOuterCornersRadius],
                        self.EngravingHeight + self.FrameThickness * 2 - self.FrameOuterCornersRadius * 2, [90, self.FrameOuterCornersRadius])

        # move plate
        self.move(self.EngravingWidth + self.FrameThickness * 2, self.EngravingHeight + self.FrameThickness * 2, move, label=label)

    def engravingPlate(self, move, label):
        if self.move(self.EngravingWidth + self.thickness*2, self.EngravingHeight + self.thickness*2, move, True):
            return

        # engraving area
        self.rectangularHole(self.thickness, self.thickness, self.EngravingWidth, self.EngravingHeight, 0, False, False, color=Color.ANNOTATIONS)

        # plate
        self.moveTo(self.thickness)
        self.polyline(self.EngravingWidth, [90, self.thickness],self.EngravingHeight, [90, self.thickness],
                        self.EngravingWidth, [90, self.thickness],self.EngravingHeight, [90, self.thickness])

        # move plate
        self.move(self.EngravingWidth + self.thickness*2, self.EngravingHeight + self.thickness*2, move, label=label)

    def supportFoot(self, move, label):
        if self.move(self.H * math.tan(self.a) + self.thickness * 4, self.thickness * 5, move, True):
            return
        self.fingerHolesAt(self.thickness*0, self.thickness * 2.5, self.H * math.tan(self.a) + self.thickness * 2, 0)

        self.polyline(self.H * math.tan(self.a) + self.thickness * 4, [90, self.thickness], self.thickness * 3, [90, self.thickness],
                        self.H * math.tan(self.a) + self.thickness * 4, [90, self.thickness], self.thickness * 3, [90, self.thickness])

        # move plate
        self.move(self.H * math.tan(self.a) + self.thickness * 4, self.thickness * 5, move, label=label)

    def supportHorizontalPlate(self, move, label):
        if self.move(self.L * math.tan(self.a) + self.thickness * 2 + self.Margin, self.thickness * 3, move, True):
            return

        self.rectangularHole(self.thickness * 1.5, self.thickness * 1.5, self.thickness + self.Margin, self.thickness + self.Margin)

        self.polyline(self.L * math.tan(self.a) + self.thickness * 2 + self.Margin, 90, self.thickness + self.burn/2, 90,
                        self.L * math.tan(self.a)/2, -90, self.thickness - self.burn, -90, self.L * math.tan(self.a)/2, 90,
                        self.thickness + self.burn/2, 90, self.L * math.tan(self.a) + self.thickness * 2 + self.Margin, 90,
                        self.thickness * 3, 90)

        # move plate
        self.move(self.L * math.tan(self.a) + self.thickness * 2 + self.Margin, self.thickness * 3, move, label=label)

    def supportVerticalPlate(self, move, label):
        if self.move(self.H/math.cos(self.a), self.H * math.tan(self.a) + self.thickness * 2, move, True):
            return

        self.polyline(self.L + self.burn/2, 90, self.L * math.tan(self.a)/2, -90, self.thickness - self.burn, -90, self.L * math.tan(self.a)/2, 90,
                        self.thickness + self.H * math.tan(self.a) * math.sin(self.a) + self.burn/2, 90 + self.BackSupportAngle)
        self.edges["f"](self.H * math.tan(self.a) + self.thickness * 2)
        self.polyline(0, 90, self.thickness*3 + self.burn/2, 90, self.thickness, -90, self.thickness - self.burn, -90, self.thickness, 90,
                        self.H - self.thickness*7 + self.burn, 90, self.thickness, -90, self.thickness - self.burn, -90, self.thickness, 90, self.thickness + self.burn/2,
                        [90, self.thickness], self.thickness, 90 - self.BackSupportAngle)

        # move plate
        self.move(self.H/math.cos(self.a), self.H * math.tan(self.a) + self.thickness * 2, move, label=label)

    def supportVerticalSpacer(self, length, move, label):
        if self.move(length + self.Margin + self.thickness*6, self.thickness * 2, move, True):
            return

        self.polyline(length + self.Margin + self.thickness*6, [180, self.thickness], self.thickness + self.burn/2, 90, self.thickness, -90,
                        self.thickness - self.burn, -90, self.thickness, 90, length + self.Margin + self.thickness * 2 + self.burn, 90,
                        self.thickness, -90, self.thickness - self.burn, -90, self.thickness, 90, self.thickness + self.burn/2,
                        [180, self.thickness])

        # move plate
        self.move(length + self.Margin + self.thickness*6, self.thickness * 2, move, label=label)

    def render(self):
        self.a = self.BackSupportAngle * math.pi/180
        self.L = min(self.EngravingWidth + self.thickness*3, self.EngravingHeight + self.thickness*3)
        self.H = (2*self.thickness + self.L) / math.cos(self.a)

        # optional cover plate
        if (self.AddCoveringFrontPlate):
            self.frameplate(True, "up", "frame cover")

        # front plate
        self.frameplate(False, "up", "frame plate")
        if (self.AddDummyFingers) :
            self.rectangularWall(self.EngravingWidth + self.thickness*2, 0, "eefe", move="up", label="dummy fingers")

        # back plate
        self.backplate(move="up", label="back plate")

        # side plates
        self.rectangularWall(self.EngravingHeight + self.thickness * 2 + self.Margin, self.EngravingThickness + self.Margin, "fEfE", move="up", label="side")
        self.rectangularWall(self.EngravingHeight + self.thickness * 2 + self.Margin, self.EngravingThickness + self.Margin, "fEfE", move="mirror up", label="side")

        # bottom plate
        self.rectangularWall(self.EngravingWidth + self.thickness * 2 + self.Margin, self.EngravingThickness + self.Margin, "fefe", move="up", label="bottom")

        # engraving plate
        self.engravingPlate(move="up", label="engraving plate")

        if (self.BackSupportAngle > 0) :
            x=1
            # back support feet
            self.supportFoot(move="up", label="foot")
            self.supportFoot(move="up", label="foot")

            # back support horizontal plates
            self.supportHorizontalPlate("up", "support horizontal")
            self.supportHorizontalPlate("up", "support horizontal")

            # back support vertical plates
            self.supportVerticalPlate("up", "support vertical")
            self.supportVerticalPlate("up", "support vertical")

            # horizontal spacers
            self.supportVerticalSpacer(self.EngravingWidth, "up", "spacer width")
            self.supportVerticalSpacer(self.EngravingWidth, "up", "spacer width")
            self.supportVerticalSpacer(self.EngravingHeight, "up", "spacer height")
            self.supportVerticalSpacer(self.EngravingHeight, "up", "spacer height")
