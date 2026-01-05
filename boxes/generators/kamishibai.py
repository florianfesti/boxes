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
from boxes.edges import HingeSettings
pass

class Kamishibai(_TopEdge):
    """Kamishibai butai (japanese image theatre)"""

    ui_group = "Misc"
    description = """
    This is a kamishibai butai (japanese image theatre), with several options for covering the different
    holes when put away.
    Magenta cuts should be performed before the blue cuts.
    The recommended wood thickness is 5 mm at least, particularly if you go for big sizes (which works
    fine with A4 or A3). If you use 3 mm, you should not use the screwing option (disabled by default),
    so you can assemble your box with glue or force the pieces together (using a bigger burn parameter).
    Please note that using the screwing option often means adding feet (which can be 3D printed for
    example). It makes the box easier to mount and unmount for repairing purposes, and the feet protect
    the wood from whatever surface the box is put on. Screws are not compatible with a small frame
    thickness (i.e. with sheets with a small margin).
    For assembling the box, please follow the following steps:
    1. Assemble the front side and back side pieces to the front and back of the front and back panels
    respectively
    2. Assemble the top handle pieces together and insert two of the plates into the two holes (centered);
    then insert the assembled handles into the dansle ceiling and add the two other plates
    3. Insert the front and back panels into the bottom panel
    4. Attach the handle between the top of the front and back panels, then add the top panel but do not
    fasten it yet, just keep it loose on top
    5. Assemble the locks together to the doors if enabled:
       5.1 lock with key : lock front - lock external - plate cut from the door (also add the door now) -
       lock internal
       5.2 lock simple : lock grip - lock external - plate cut from the door (also add the door now) -
       lock internal
       5.3 small extra locks for top and bottom : lock grip - plate cut from the door (also add the door
       now) - lock internal - lock spacer - lock locker
    6. Add the hinges to the doors if needed (for two-panes front doors)
    7. fasten the top
    8. Attach two side panel inner plates to a side panel with the two pegs (use glue if necessary) and
    repeat a second time
    9. If you use a lock with key, add the last short peg to the back plate (you may want to sand it a bit
    on the other half so that the key can be attached easily enough, but it should not fal off either)
    10. You should now be able to close and open all the doors
    Usage recommendations:
    1. Add your paper sheets from one side or the other (normally you leave either left or right closed,
    depending on which is more comfortable for you)
    2. Thick paper is easier to handle ; if you print on a home printer, use the thickest you printer can
    print (probably around 200 grams per square meter) ; if you want extra quality, go to a printing shop
    and ask them for 300 grams per square meter printing
    3. You can also buy virgin drawing paper to write your own stories
    4. If you decided to go for the lock with key, you can ask one of the participants to unlock the box,
    it really helps in immersing into toe story
    5. If you need a kamishibai for showing images during a guided tour, you may choose to use the
    one-panel front, and use transparent acrylic for the back and front panels to keep you sheets
    protected from light rain ; you may need to cut the box from a rain-resistant material
    (outside-compatible plywood or acrylic)
    """

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=1.5)
        self.addSettingsArgs(edges.SlideOnLidSettings, hole_width=15.0, spring="none", second_pin=True, play=0.1)
        # ~ self.addSettingsArgs(edges.HingeSettings, outset=True, pinwidth=0.4, style="flush", axle=2.5, hingestrength=2)
        self.addSettingsArgs(edges.HingeSettings, outset=True, pinwidth=0.4, style="flush", axle=2.5, hingestrength=1)
        self.argparser.add_argument(
            "--SheetWidth",  action="store", type=float, default=297.0,
            help="width of the sheets in mm")
        self.argparser.add_argument(
            "--SheetHeight",  action="store", type=float, default=210.0,
            help="height of the sheets in mm")
        self.argparser.add_argument(
            "--SheetsStackDepth",  action="store", type=float, default=30.0,
            help="Depth of the sheets stack in mm")
        self.argparser.add_argument(
            "--FrameThickness",  action="store", type=float, default=20.0,
            help="Frame thickness in mm")
        self.argparser.add_argument(
            "--FrameCornerRadius",  action="store", type=float, default=5.0,
            help="Radius of the frame corners in mm")
        self.argparser.add_argument(
            "--Margin",  action="store", type=float, default=2.0,
            help="Margin for sheets and moving parts in mm")
        self.argparser.add_argument(
            "--HandleThickness",  action="store", type=int, default=2,
            help="Thickness of the top handle in multiples of thickness (Set to 0 for no handle)")
        self.argparser.add_argument(
            "--HandleWidth",  action="store", type=float, default=120.0,
            help="Width of the top handle in mm (Set to 0 for no handle) ; the SheetStackDepth should be at least 4 x thickness more")
        self.argparser.add_argument(
            "--HandleMargin",  action="store", type=float, default=0.0,
            help="Margin for the top handle in mm (Set to 0 for no margin)")
        self.argparser.add_argument(
            "--BackExtraDepth",  action="store", type=int, default=4,
            help="Back extra depth (for adding buttons for example), in multiples of thickness ; set to 0 to let the system calculate the smallest one")
        self.argparser.add_argument(
            "--PegsWidthMargin",  action="store", type=float, default=0.5,
            help="Margin for the pegs width in mm ; set to a lower value if the pieces are forced together, a higher value if the pieces slide easily into each other (using screws or glue to assemble)")
        front_group = self.argparser.add_argument_group("Kamishibai front cover")
        front_group.add_argument(
            "--FrontCoverStyle",  action="store", type=str, default="two-part lid with hinge eyes (both ends)",
            choices=["slide-on lid", "two-part lid with hinge eyes (both ends)", "three-part lid, hinges not provided"],
            help="style of the front cover")
        front_group.add_argument(
            "--FrontExtraDepth",  action="store", type=int, default=4,
            help="Front extra depth (for attaching hinges for example), in multiples of thickness ; set to 0 to ignore or let the system calculate the smallest one")
        front_group.add_argument(
            "--FrontLockStyle",  action="store", type=str, default="with key",
            choices=["none", "simple", "with key"],
            help="style of the front lock")
        front_group.add_argument(
            "--FrontExtraTopAndBottomLocks",  action="store", type=boolarg, default=True,
            help="Add front extra locks at the top and bottom")
        hinges_3panes_group = self.argparser.add_argument_group("Kamishibai 3 pane cover hinge holes")
        hinges_3panes_group.add_argument(
            "--HingeHolesDiameter",  action="store", type=float, default=2.5,
            help="Hinge hole diameter in mm (set to 0 for no holes)")
        hinges_3panes_group.add_argument(
            "--HingeHolesCoverEdgeDistance",  action="store", type=float, default=5.5,
            help="distance of the cover holes from the edge to the holes centers in mm")
        hinges_3panes_group.add_argument(
            "--HingeHolesBoxEdgeDistance",  action="store", type=float, default=7.0,
            help="distance of the box holes from the edge to the holes centers in mm")
        hinges_3panes_group.add_argument(
            "--HingeHolesCoverSeparation",  action="store", type=argparseSections, default="24.0:12.0",
            help="separation of the cover holes from one another's center in mm (section parameter type) ; the first item is the distance from the border")
        hinges_3panes_group.add_argument(
            "--HingeHolesBoxSeparation",  action="store", type=argparseSections, default="15.0:30.0",
            help="separation of the box holes from one another's center in mm (section parameter type) ; the first item is the distance from the border")
        ScrewsLocking_group = self.argparser.add_argument_group("Screws parameters for attaching the pieces together")
        ScrewsLocking_group.add_argument(
            "--LockScrewDiameter",  action="store", type=float, default=0.0,
            help="Diameter of the screw holes in mm (set to 0 for no screws)")
        ScrewsLocking_group.add_argument(
            "--TopLockScrewLength",  action="store", type=float, default=16.0,
            help="Length of the top locking screws in mm")
        ScrewsLocking_group.add_argument(
            "--BottomLockScrewLength",  action="store", type=float, default=13.0,
            help="Length of the bottom locking screws in mm")
        ScrewsLocking_group.add_argument(
            "--DoorFeetScrewLength",  action="store", type=float, default=16.0,
            help="Length of the door feet screws in mm (set to 0 for no screws)")
        ScrewsLocking_group.add_argument(
            "--LockNutThickness",  action="store", type=float, default=2.4,
            help="Thickness of the locking nuts in mm")
        ScrewsLocking_group.add_argument(
            "--LockNutWidth",  action="store", type=float, default=5.5,
            help="Width of the locking nuts in mm")
        ScrewsLocking_group.add_argument(
            "--LockScrewDistanceFromBorder",  action="store", type=float, default=11,
            help="Distance of the screw axis from the side border (in multiples of thickness)")
        ScrewsLocking_group.add_argument(
            "--LockScrewExtraFeetScewDiameter",  action="store", type=float, default=3.0,
            help="Diameter of the screw holes for extra feet at the corners, in mm (set to 0 for no screws)")
        ScrewsLocking_group.add_argument(
            "--LockScrewExtraFeetDistanceFromBorder",  action="store", type=float, default=7.0,
            help="Distance from the border for the axis of the extra feet at the corners, in mm (set to 0 for no screws)")


    def screwAttachement (self, LockScrewLength):
        self.polyline(0, 90, self.thickness, 90, self.LockNutWidth/2 - self.LockScrewDiameter/2, -90,
                        self.LockNutThickness, -90, self.LockNutWidth/2 - self.LockScrewDiameter/2, 90,
                        LockScrewLength - self.LockNutThickness - self.thickness, -90, self.LockScrewDiameter, -90,
                        LockScrewLength - self.LockNutThickness - self.thickness, 90, self.LockNutWidth/2 - self.LockScrewDiameter/2, -90,
                        self.LockNutThickness, -90, self.LockNutWidth/2 - self.LockScrewDiameter/2, 90, self.thickness, 90)

    def boxFrontBackCallback (self, wi, hi, isFront):
        # window hole
        self.rectangularHole(self.thickness*2 + self.FrameThickness, self.FrameThickness, wi - self.FrameThickness*2, hi - self.Margin - self.FrameThickness*2 - self.thickness * (2 if self.HandleThickness > 0 else 0), self.FrameCornerRadius, False, False)
        # finger holes for handle ceiling
        if self.HandleThickness > 0 :
            self.fingerHolesAt(self.thickness*2 , hi - self.thickness * 1.5, self.thickness*4,0)
            self.fingerHolesAt(wi - self.thickness*2 , hi - self.thickness * 1.5, self.thickness*4,0)
            self.fingerHolesAt(wi/2 - self.HandleWidth/2 - self.thickness*0, hi - self.thickness * 1.5, self.thickness*4,0)
            self.fingerHolesAt(wi/2 + self.HandleWidth/2 - self.thickness*0, hi - self.thickness * 1.5, self.thickness*4,0)
        # finger holes for extra depth
        if (isFront and self.FrontExtraDepth > 0) or not isFront :
            self.fingerHolesAt(self.thickness*1.5, self.thickness*0, hi)
            self.fingerHolesAt(self.thickness*2.5 + wi, self.thickness*0, hi)
        else :
            # hinge holes for 3 pane panel
            if ((self.HingeHolesDiameter > 0) and (isFront and self.FrontCoverStyle == "three-part lid, higes not provided") or (not isFront and self.BackCoverStyle == "three-part lid, higes not provided")) :
                posx = self.thickness
                for x in self.HingeHolesBoxSeparation:
                    posx += x
                    self.hole(posx, hi + self.thickness - self.HingeHolesBoxEdgeDistance, self.HingeHolesDiameter/2)
                    self.hole(wi + self.thickness*4 - posx, hi + self.thickness - self.HingeHolesBoxEdgeDistance, self.HingeHolesDiameter/2)
                posy=-self.thickness
                for y in self.HingeHolesBoxSeparation:
                    posy += y
                    self.hole(self.HingeHolesBoxEdgeDistance + self.thickness, posy, self.HingeHolesDiameter/2)
                    self.hole(self.HingeHolesBoxEdgeDistance + self.thickness, (hi - self.Margin) * 3/4 - posy, self.HingeHolesDiameter/2)
                    self.hole(wi + self.thickness*3 - self.HingeHolesBoxEdgeDistance, posy, self.HingeHolesDiameter/2)
                    self.hole(wi + self.thickness*3 - self.HingeHolesBoxEdgeDistance, (hi - self.Margin) * 3/4 - posy, self.HingeHolesDiameter/2)

    def boxFrontBack (self, wi, hi, isFront, move=None, label=""):
        if self.LockScrewDiameter > 0 :
            #self.rectangularWall(wi + self.thickness*4, hi, "fNfM", callback=[
            #                lambda:self.boxFrontBackCallback(wi, hi, isFront)
            #                ],move=move, label=label)
            if self.move(wi + self.thickness*6, hi + self.thickness*3, move, True):
                return
            self.boxFrontBackCallback(wi, hi, isFront)
            self.moveTo(-self.thickness*2, 0)
            #bottom
            self.edge(self.thickness*2)
            self.edges["f"](self.thickness*(self.LockScrewDistanceFromBorder - 3) - self.LockScrewDiameter)
            self.edge(self.LockScrewDiameter/2)
            self.screwAttachement(self.BottomLockScrewLength - self.thickness)
            self.edge(self.LockScrewDiameter/2)
            self.edges["f"](wi/2 - self.thickness*(self.LockScrewDistanceFromBorder - 5) - self.LockScrewDiameter*2)
            self.edge(self.LockScrewDiameter/2)
            self.screwAttachement(self.BottomLockScrewLength - self.thickness)
            self.edge(self.LockScrewDiameter/2)
            self.edges["f"](wi/2 - self.thickness*(self.LockScrewDistanceFromBorder - 5) - self.LockScrewDiameter*2)
            self.edge(self.LockScrewDiameter/2)
            self.screwAttachement(self.BottomLockScrewLength - self.thickness)
            self.edge(self.LockScrewDiameter/2)
            self.edges["f"](self.thickness*(self.LockScrewDistanceFromBorder - 3) - self.LockScrewDiameter)
            self.polyline(self.thickness*2, 90)
            #right
            self.edges["N"](hi)
            self.corner(90)
            #top
            self.edges["f"](self.thickness*(self.LockScrewDistanceFromBorder - 3 - edges.SlideOnLidSettings.relative_params["play"]) - self.LockScrewDiameter)
            self.edge(self.LockScrewDiameter/2)
            self.screwAttachement(self.TopLockScrewLength - self.thickness)
            self.edge(self.LockScrewDiameter/2)
            self.edges["f"](wi/2 - self.thickness*(self.LockScrewDistanceFromBorder - 5) - self.LockScrewDiameter*2)
            self.edge(self.LockScrewDiameter/2)
            self.screwAttachement(self.TopLockScrewLength - self.thickness)
            self.edge(self.LockScrewDiameter/2)
            self.edges["f"](wi/2 - self.thickness*(self.LockScrewDistanceFromBorder - 5) - self.LockScrewDiameter*2)
            self.edge(self.LockScrewDiameter/2)
            self.screwAttachement(self.TopLockScrewLength - self.thickness)
            self.edge(self.LockScrewDiameter/2)
            self.edges["f"](self.thickness*(self.LockScrewDistanceFromBorder - 3 - edges.SlideOnLidSettings.relative_params["play"]) - self.LockScrewDiameter)
            self.corner(90)
            #left
            self.edges["M"](hi)
            self.corner(90)
            # move plate
            self.move(wi + self.thickness*6, hi + self.thickness*3, move, label=label)
        else :
            self.rectangularWall(wi + self.thickness*4, hi, "fNfM", callback=[
                            lambda:self.boxFrontBackCallback(wi, hi, isFront)
                            ],move=move, label=label)

    def boxTopBottom (self, wi, di, isTop, move=None, label=""):
        if self.move(wi + self.thickness*8, di + self.thickness * (self.FrontExtraDepth + self.BackExtraDepth + 6) + (self.thickness*3 if self.FrontCoverStyle == "two-part lid with hinge eyes (both ends)" else 0), move, True):
            return
        if self.LockScrewDiameter > 0 :
            # screw holes
            self.hole(self.thickness * (self.LockScrewDistanceFromBorder - 1), self.thickness * (self.BackExtraDepth + 2.5), self.LockScrewDiameter/2)
            self.hole(wi/2 + self.thickness * 4, self.thickness * (self.BackExtraDepth + 2.5), self.LockScrewDiameter/2)
            self.hole(wi - self.thickness * (self.LockScrewDistanceFromBorder - 9), self.thickness * (self.BackExtraDepth + 2.5), self.LockScrewDiameter/2)
            self.hole(self.thickness * (self.LockScrewDistanceFromBorder - 1), di + self.thickness * (self.BackExtraDepth + 3.5), self.LockScrewDiameter/2)
            self.hole(wi/2 + self.thickness * 4, di + self.thickness * (self.BackExtraDepth + 3.5), self.LockScrewDiameter/2)
            self.hole(wi - self.thickness * (self.LockScrewDistanceFromBorder - 9), di + self.thickness * (self.BackExtraDepth + 3.5), self.LockScrewDiameter/2)

            if self.LockScrewExtraFeetScewDiameter > 0 and self.LockScrewExtraFeetDistanceFromBorder > 0 and not isTop :
                self.hole(self.LockScrewExtraFeetDistanceFromBorder, self.LockScrewExtraFeetDistanceFromBorder, self.LockScrewExtraFeetScewDiameter/2)
                self.hole(wi + self.thickness * 8 - self.LockScrewExtraFeetDistanceFromBorder, self.LockScrewExtraFeetDistanceFromBorder, self.LockScrewExtraFeetScewDiameter/2)
                if self.FrontCoverStyle == "two-part lid with hinge eyes (both ends)":
                    self.hole(self.thickness * 6, di + self.thickness * (self.BackExtraDepth + self.FrontExtraDepth + 4) - self.LockScrewExtraFeetDistanceFromBorder, self.LockScrewExtraFeetScewDiameter/2)
                    self.hole(wi + self.thickness * 2, di + self.thickness * (self.BackExtraDepth + self.FrontExtraDepth + 4) - self.LockScrewExtraFeetDistanceFromBorder, self.LockScrewExtraFeetScewDiameter/2)
                elif self.FrontCoverStyle == "three-part lid, higes not provided":
                    self.hole(self.LockScrewExtraFeetDistanceFromBorder, di + self.thickness * (self.BackExtraDepth + self.FrontExtraDepth + 4) - self.LockScrewExtraFeetDistanceFromBorder, self.LockScrewExtraFeetScewDiameter/2)
                    self.hole(wi + self.thickness * 8 - self.LockScrewExtraFeetDistanceFromBorder, di + self.thickness * (self.BackExtraDepth + self.FrontExtraDepth + 4) - self.LockScrewExtraFeetDistanceFromBorder, self.LockScrewExtraFeetScewDiameter/2)
                else:
                    self.hole(self.LockScrewExtraFeetDistanceFromBorder, di + self.thickness * (self.BackExtraDepth + self.FrontExtraDepth + 6) - self.LockScrewExtraFeetDistanceFromBorder, self.LockScrewExtraFeetScewDiameter/2)
                    self.hole(wi + self.thickness * 8 - self.LockScrewExtraFeetDistanceFromBorder, di + self.thickness * (self.BackExtraDepth + self.FrontExtraDepth + 6) - self.LockScrewExtraFeetDistanceFromBorder, self.LockScrewExtraFeetScewDiameter/2)

            #finger holes for top and bottom door locks
            if self.FrontExtraTopAndBottomLocks and (self.FrontCoverStyle == "two-part lid with hinge eyes (both ends)"
                                        or (self.FrontCoverStyle == "three-part lid, higes not provided" and not isTop)):
                self.fingerHolesAt(wi/2 - self.thickness * 4, di + self.thickness * (self.BackExtraDepth + self.FrontExtraDepth + 2.5), self.thickness*16, 0)

            # finger holes for front and back if necessary #TODO update all this section...
            #self.fingerHolesAt(self.thickness*2, self.thickness * (self.BackExtraDepth + 2.5), wi + self.thickness*4,0)
            self.fingerHolesAt(self.thickness*2, self.thickness * (self.BackExtraDepth + 2.5), self.thickness*(self.LockScrewDistanceFromBorder - 3) - self.LockScrewDiameter,0)
            self.fingerHolesAt(self.thickness*(self.LockScrewDistanceFromBorder - 1) +  self.LockScrewDiameter, self.thickness * (self.BackExtraDepth + 2.5), wi/2 - self.thickness*(self.LockScrewDistanceFromBorder - 5) - self.LockScrewDiameter*2,0)
            self.fingerHolesAt(wi/2 + self.thickness*4 + self.LockScrewDiameter, self.thickness * (self.BackExtraDepth + 2.5), wi/2 - self.thickness*(self.LockScrewDistanceFromBorder - 5) - self.LockScrewDiameter*2,0)
            self.fingerHolesAt(wi - self.thickness*(self.LockScrewDistanceFromBorder - 9) + self.LockScrewDiameter, self.thickness * (self.BackExtraDepth + 2.5), self.thickness*(self.LockScrewDistanceFromBorder - 3) - self.LockScrewDiameter,0)
            if self.FrontExtraDepth > 0 :
                #self.fingerHolesAt(self.thickness*2, di + self.thickness * (self.BackExtraDepth + 3.5), wi + self.thickness*4,0)
                self.fingerHolesAt(self.thickness*2, di + self.thickness * (self.BackExtraDepth + 3.5), self.thickness*(self.LockScrewDistanceFromBorder - 3) - self.LockScrewDiameter,0)
                self.fingerHolesAt(self.thickness*(self.LockScrewDistanceFromBorder - 1) + self.LockScrewDiameter, di + self.thickness * (self.BackExtraDepth + 3.5), wi/2 - self.thickness*(self.LockScrewDistanceFromBorder - 5) - self.LockScrewDiameter*2,0)
                self.fingerHolesAt(wi/2 + self.thickness*4 + self.LockScrewDiameter, di + self.thickness * (self.BackExtraDepth + 3.5), wi/2 - self.thickness*(self.LockScrewDistanceFromBorder - 5) - self.LockScrewDiameter*2,0)
                self.fingerHolesAt(wi - self.thickness*(self.LockScrewDistanceFromBorder - 9) + self.LockScrewDiameter, di + self.thickness * (self.BackExtraDepth + 3.5), self.thickness*(self.LockScrewDistanceFromBorder - 3) - self.LockScrewDiameter,0)

        else :
            # finger holes for front and back if necessary
            self.fingerHolesAt(self.thickness*2, self.thickness * (self.BackExtraDepth + 2.5), wi + self.thickness*4,0)
            if self.FrontExtraDepth > 0 :
                self.fingerHolesAt(self.thickness*2, di + self.thickness * (self.BackExtraDepth + 3.5), wi + self.thickness*4,0)
        # finger holes for sides
        # back
        if isTop :
            if self.BackExtraDepth > 2 :
                self.fingerHolesAt(self.thickness*3.5, self.thickness*2, self.thickness * (self.BackExtraDepth - 0), angle=90)
                self.fingerHolesAt(wi + self.thickness*4.5, self.thickness*2, self.thickness * (self.BackExtraDepth - 0), angle=90)
        else :
            self.fingerHolesAt(self.thickness*3.5, self.thickness*2, self.thickness * self.BackExtraDepth, angle=90)
            self.fingerHolesAt(wi + self.thickness*4.5, self.thickness*2, self.thickness * self.BackExtraDepth, angle=90)
        # front
        if self.FrontCoverStyle == "two-part lid with hinge eyes (both ends)" :
            self.fingerHolesAt(self.thickness*3.5, di + self.thickness*(self.BackExtraDepth + 4), self.thickness * (self.FrontExtraDepth  - 2), angle=90)
            self.fingerHolesAt(wi + self.thickness*4.5, di + self.thickness*(self.BackExtraDepth + 4), self.thickness * (self.FrontExtraDepth  - 2), angle=90)
        elif self.FrontExtraDepth > 0 and (self.FrontCoverStyle == "three-part lid, higes not provided" or self.FrontCoverStyle == "none") :
            self.fingerHolesAt(self.thickness*3.5, di + self.thickness*(self.BackExtraDepth + self.FrontExtraDepth + 0), self.FrontExtraDepth * self.thickness, angle=90)
            self.fingerHolesAt(wi + self.thickness*4.5, di + self.thickness*(self.BackExtraDepth  + self.BackExtraDepth + 0), self.FrontExtraDepth * self.thickness, angle=90)
        elif self.FrontExtraDepth > 2 and self.FrontCoverStyle == "slide-on lid" :
            self.fingerHolesAt(self.thickness*3.5, di + self.thickness*(self.BackExtraDepth + 4), self.thickness * (self.FrontExtraDepth), angle=90)
            self.fingerHolesAt(wi + self.thickness*4.5, di + self.thickness*(self.BackExtraDepth + 4), self.thickness * (self.FrontExtraDepth), angle=90)
        elif self.FrontExtraDepth > 0 and not isTop and self.FrontCoverStyle == "slide-on lid" :
            self.fingerHolesAt(self.thickness*3.5, di + self.thickness*(self.BackExtraDepth + 4), self.thickness * (self.FrontExtraDepth), angle=90)
            self.fingerHolesAt(wi + self.thickness*4.5, di + self.thickness*(self.BackExtraDepth + 4), self.thickness * (self.FrontExtraDepth), angle=90)
        elif self.FrontExtraDepth > 0 and not isTop and not self.FrontCoverStyle == "slide-on lid" :
            self.fingerHolesAt(self.thickness*3.5, di + (self.BackExtraDepth + 4.5) * self.thickness, self.thickness * (self.FrontExtraDepth - 1), angle=90)
            self.fingerHolesAt(wi + self.thickness*4.5, di + (self.BackExtraDepth + 4.5) * self.thickness, self.thickness * (self.FrontExtraDepth - 1), angle=90)
        # hole for handle
        if (isTop and self.HandleThickness > 0 and self.HandleWidth > 0) :
            self.rectangularHole(self.thickness*4 + wi/2 - self.HandleWidth/2 - self.HandleMargin/2, self.thickness * (self.BackExtraDepth + 3 - self.HandleThickness/2) + di/2 - self.HandleMargin/2, self.HandleWidth + self.HandleMargin, self.thickness*self.HandleThickness + self.HandleMargin, 0, False, False)
        # hinge holes for 3 pane panel
        if (isTop and (self.HingeHolesDiameter > 0) and (self.FrontCoverStyle == "three-part lid, higes not provided") and (self.HandleThickness > 0)) :
            posx=self.thickness*3
            for x in self.HingeHolesBoxSeparation:
                posx += x
                self.hole(posx, di + self.thickness*(self.FrontExtraDepth + self.BackExtraDepth + 4) - self.HingeHolesBoxEdgeDistance, self.HingeHolesDiameter/2)
                self.hole(wi + self.thickness*8 - posx, di + self.thickness*(self.FrontExtraDepth + self.BackExtraDepth + 4) - self.HingeHolesBoxEdgeDistance, self.HingeHolesDiameter/2)
        # plate
        # back side
        self.moveTo(self.thickness*2, 0)
        if isTop :
            self.polyline(self.thickness - self.Margin/2, 90, self.thickness * 2, -90, wi + self.thickness*2 + self.Margin, -90,
                            self.thickness * 2, 90, self.thickness - self.Margin/2, [90, self.thickness*2])
        else :
            self.edge(self.thickness * 2)
            self.edges["L"](wi)
            self.polyline(self.thickness * 2, [90, self.thickness*2])
        # right side
        if isTop :
            self.polyline(self.thickness * self.BackExtraDepth - self.Margin/2, 90, self.thickness*2, -90, di + self.thickness*2 + self.Margin, 0)
            if self.FrontExtraDepth > 0 :
                self.polyline(0, -90, self.thickness*2, 90)
                self.edge(self.thickness * self.FrontExtraDepth - self.Margin/2)
        else :
            self.edge(self.thickness * (self.BackExtraDepth + 1))
            self.edges["L"](di)
            if self.FrontCoverStyle == "slide-on lid" :
                self.edge(self.thickness * (1 + self.FrontExtraDepth))
            else :
                self.edge(self.thickness * (1 + self.FrontExtraDepth))
        if self.FrontCoverStyle == "slide-on lid" :
            self.corner(90, radius = self.thickness*2)
        else :
            self.corner(90)
        # front side
        if self.FrontExtraDepth > 0 :
            if self.FrontCoverStyle == "two-part lid with hinge eyes (both ends)" :
                self.edges["k"].settings.style = "flush_inset"
                self.edges["k"](wi + self.thickness*8)
                self.corner(90)
            elif self.FrontCoverStyle == "slide-on lid" :
                if isTop :
                    self.polyline(self.thickness - self.Margin/2, 90, self.thickness * 2, -90, wi + self.thickness*2 + self.Margin, -90,
                                    self.thickness * 2, 90, self.thickness - self.Margin/2, [90, self.thickness*2])
                else :
                    self.edge(self.thickness * 2)
                    self.edges["L"](wi)
                    self.polyline(self.thickness * 2, [90, self.thickness*2])
            else :
                self.polyline(wi + self.thickness*8, 90)
        else :
            if not isTop :
                self.edge(self.thickness*2)
            self.edges["F"](wi + self.thickness*4)
            if not isTop :
                self.edge(self.thickness*2)
            self.corner(90)
        # left side
        if isTop :
            if self.FrontExtraDepth > 0 :
                if self.FrontCoverStyle == "slide-on lid" :
                    self.polyline(self.thickness * (self.FrontExtraDepth - 0) - self.Margin/2, 90)
                else :
                    self.polyline(self.thickness * self.FrontExtraDepth - self.Margin/2, 90)
                self.polyline(self.thickness*2, -90)
            self.polyline(di + self.thickness*2 + self.Margin, -90, self.thickness*2, 90, self.thickness * self.BackExtraDepth - self.Margin/2, 0)
        else :
            if self.FrontCoverStyle == "slide-on lid" :
                self.edge(self.thickness * (1 + self.FrontExtraDepth))
            else :
                self.edge(self.thickness * (1 + self.FrontExtraDepth))
            self.edges["L"](di)
            self.edge(self.thickness * (self.BackExtraDepth + 1))
        self.corner(90, radius=self.thickness*2)
        # move plate
        self.move(wi + self.thickness*8, di + self.thickness * (self.FrontExtraDepth + self.BackExtraDepth + 6) + (self.thickness*3 if self.FrontCoverStyle == "two-part lid with hinge eyes (both ends)" else 0), move, label=label)

    def boxFrontSideCallback (self, hi) :
        # hinge holes for 3 pane panel
        if ((self.HingeHolesDiameter > 0) and (self.FrontCoverStyle == "three-part lid, higes not provided")) :
            posy=0
            for y in self.HingeHolesBoxSeparation:
                posy += y
                self.hole(posy - self.thickness, self.HingeHolesBoxEdgeDistance, self.HingeHolesDiameter/2)
                self.hole(hi * 3/4 + self.Margin/2 - posy, self.HingeHolesBoxEdgeDistance, self.HingeHolesDiameter/2)

    def boxOpenSide (self, hi, move=None):
        #back
        if self.BackExtraDepth > 2 :
            self.rectangularWall(hi, self.thickness*self.BackExtraDepth, "Nfff", move=move, label="back side")
        else :
            self.rectangularWall(hi, self.thickness*self.BackExtraDepth, "Neff", move=move, label="back side")

        # front
        if self.FrontExtraDepth > 0 :
            if self.FrontCoverStyle == "slide-on lid" :
                if self.FrontExtraDepth > 0 :
                    self.rectangularWall(hi, self.thickness*(self.FrontExtraDepth), "Nfff", move=move, label="front side")
                else :
                    self.rectangularWall(hi, self.thickness*(self.FrontExtraDepth), "Neff", move=move, label="front side")
            elif self.FrontCoverStyle == "two-part lid with hinge eyes (both ends)" :
                self.rectangularWall(hi, self.thickness*(self.FrontExtraDepth - 2), "efff", move=move, label="front side")
            elif self.FrontCoverStyle == "three-part lid, higes not provided" :
                self.rectangularWall(hi, self.FrontExtraDepth * self.thickness, "efff", callback=[lambda:self.boxFrontSideCallback(hi)], move=move, label="front side")
            else :
                self.rectangularWall(hi, self.thickness*self.FrontExtraDepth, "efff", move=move, label="front side")

    def topHandle (self, wi, di, move=None, label=""):
        # handle plates
        for i in range(self.HandleThickness):
            if self.move(wi, 30 + self.thickness*(self.HandleThickness * 2 + 2), move, True):
                return
            # holes for holders
            self.rectangularHole(wi/2 - self.HandleWidth/2 + self.thickness, self.thickness, self.thickness*3, self.thickness,0, False, False)
            self.rectangularHole(wi/2 + self.HandleWidth/2 - self.thickness*4, self.thickness, self.thickness*3, self.thickness,0, False, False)
            #hole for screw
            if self.LockScrewDiameter > 0 :
                self.hole(wi/2, self.thickness*1.5, self.LockScrewDiameter/2)
            #hole for handle
            self.rectangularHole((wi - self.HandleWidth)/2 + self.thickness * self.HandleThickness, self.thickness*2 + self.thickness * self.HandleThickness, self.HandleWidth - self.thickness * self.HandleThickness * 2, 30, 15, False, False)
            # main plate
            # bottom
            self.polyline(self.thickness*5, 90, self.thickness, -90, wi/2 - self.HandleWidth/2 - self.thickness*5, -90,
                        self.thickness, 90, self.thickness*5, 90, self.thickness, -90)
            if (self.LockScrewDiameter > 0) :
                self.polyline(self.HandleWidth/2 - self.thickness*5 - self.LockNutWidth, -90, self.thickness, 90,
                            self.LockNutWidth*2, 90, self.thickness, -90)
                self.edge(self.HandleWidth/2 - self.thickness*5 - self.LockNutWidth)
            else :
                self.edge(self.HandleWidth - self.thickness*10)
            self.polyline(0, -90, self.thickness, 90, self.thickness*5, 90, self.thickness, -90,
                        wi/2 - self.HandleWidth/2 - self.thickness*5, -90, self.thickness, 90, self.thickness*5, 90)
            # right
            self.polyline(self.thickness*2, 90)
            # plate holder
            self.polyline(self.thickness, 90, self.thickness, -90, self.thickness*3, -90,
                        self.thickness, 90, wi/2 - self.HandleWidth/2 - self.thickness * (self.HandleThickness+2), -90)
            # handle
            self.polyline(30 - 15 + self.thickness*(self.HandleThickness * 2), [90,15], self.HandleWidth - 30, [90,15],
                        30 - 15 + self.thickness*(self.HandleThickness * 2), -90, wi/2 - self.HandleWidth/2 - self.thickness * (self.HandleThickness+2), 90)
            #plate holder
            self.polyline(self.thickness, -90, self.thickness*3, -90, self.thickness, 90, self.thickness, 90)
            # left
            self.polyline(self.thickness*2, 90)
            # move plate
            self.move(wi, 30 + self.thickness*(self.HandleThickness * 2 + 2), move, label=label)
        # plate holders
        self.rectangularWall(di, self.thickness*3, move=move)
        self.rectangularWall(di, self.thickness*3, move=move)
        self.rectangularWall(di, self.thickness*3, move=move)
        self.rectangularWall(di, self.thickness*3, move=move)
        #ceiling
        if self.move(wi+ self.thickness, di+ self.thickness*4, move, True):
            return
        self.moveTo(0, self.thickness*2)
        self.rectangularHole(wi/2 - self.HandleWidth/2, di/2 - self.thickness*self.HandleThickness/2, self.thickness*5, self.thickness*self.HandleThickness, 0, False, False)
        self.rectangularHole(wi/2 + self.HandleWidth/2 - self.thickness*5, di/2 - self.thickness*self.HandleThickness/2, self.thickness*5, self.thickness*self.HandleThickness, 0, False, False)
        if (self.LockScrewDiameter > 0) :
            self.rectangularHole(wi/2 - self.LockNutWidth, self.thickness, self.LockNutWidth*2, di - self.thickness*2, 0, False, False)
        #bottom
        self.edges["f"](self.thickness*4)
        self.edge(wi/2 - self.HandleWidth/2 - self.thickness*6)
        self.edges["f"](self.thickness*4)
        self.edge(self.HandleWidth - self.thickness*4)
        self.edges["f"](self.thickness*4)
        self.edge(wi/2 - self.HandleWidth/2 - self.thickness*6)
        self.edges["f"](self.thickness*4)
        self.corner(90)
        #right
        self.polyline(di/2 - self.HandleThickness* self.thickness/2, 90, self.thickness*5, -90,
                    self.thickness * self.HandleThickness, -90, self.thickness*5, 90,
                    di/2 - self.HandleThickness* self.thickness/2, 90)
        #top
        self.edges["f"](self.thickness*4)
        self.edge(wi/2 - self.HandleWidth/2 - self.thickness*6)
        self.edges["f"](self.thickness*4)
        self.edge(self.HandleWidth - self.thickness*4)
        self.edges["f"](self.thickness*4)
        self.edge(wi/2 - self.HandleWidth/2 - self.thickness*6)
        self.edges["f"](self.thickness*4)
        self.corner(90)
        #left
        self.polyline(di/2 - self.HandleThickness* self.thickness/2, 90, self.thickness*5, -90,
                    self.thickness * self.HandleThickness, -90, self.thickness*5, 90,
                    di/2 - self.HandleThickness* self.thickness/2, 90)
        # move plate
        self.move(wi+ self.thickness, di+ self.thickness*4, move, label="handle ceiling")

    def coverPanel1Lid (self, wi, hi, hasSubLayer = False, move=None, label=""):
        # sides
        if hasSubLayer :
            self.rectangularWall(wi, hi, "lmen", callback = [lambda:self.rectangularHole(wi/2, self.thickness*3.5, self.thickness, self.thickness),
                                            lambda:self.rectangularHole(hi - self.thickness*5.5, wi/2, self.thickness, self.thickness)],move=move, label=label)
            self.rectangularWall(wi - self.Margin, hi - self.thickness*6, "eeee", callback = [lambda:self.rectangularHole(wi/2 - self.Margin/2, self.thickness*1.5, self.thickness, self.thickness),
                                            lambda:self.rectangularHole(hi - self.thickness*7.5, wi/2 - self.Margin/2, self.thickness, self.thickness)],move=move, label="side panel inner")
            self.rectangularWall(wi - self.Margin, hi - self.thickness*6, "eeee", callback = [lambda:self.rectangularHole(wi/2 - self.Margin/2, self.thickness*1.5, self.thickness, self.thickness),
                                            lambda:self.rectangularHole(hi - self.thickness*7.5, wi/2 - self.Margin/2, self.thickness, self.thickness)],move=move, label="side panel inner")
            self.rectangularWall (self.thickness + self.PegsWidthMargin, self.thickness * 3, "eeee", move=move, label="")
            self.rectangularWall (self.thickness + self.PegsWidthMargin, self.thickness * 3, "eeee", move=move, label="")
        # back or front (with key holder if necessary)
        else :
            if (self.FrontCoverStyle == "two-part lid with hinge eyes (both ends)" or self.FrontCoverStyle == "three-part lid, higes not provided") and self.FrontLockStyle == "with key" :
                self.rectangularWall(wi, hi, "lmen", callback=[lambda:self.hole(wi/2, hi - self.thickness*4, d=self.thickness*4),
                                                                lambda:self.rectangularHole(self.thickness*2, self.thickness*2, self.thickness, self.thickness)],move=move, label=label)
                self.rectangularWall (self.thickness*2, self.thickness + self.PegsWidthMargin, "eeee", move=move)
            else :
                self.rectangularWall(wi, hi, "lmen", callback=[lambda:self.hole(wi/2, hi - self.thickness*4, d=self.thickness*4)],move=move, label=label)

    def coverPanel2SideCallback(self, wi, hi, lockStyle):
        if "with key" in lockStyle :
            self.hole((wi - self.Margin)/2 - self.thickness*1.5, hi/2, self.thickness*3.5)
            self.rectangularHole((wi - self.Margin)/2 - self.thickness*1.5, hi/2, self.thickness + self.Margin, self.thickness + self.Margin, 0, color=Color.MAGENTA)
            self.rectangularHole((wi - self.Margin)/2 - self.thickness*3.5, hi/2, self.thickness, self.thickness, 0, color=Color.MAGENTA)
            self.rectangularHole((wi - self.Margin)/2 + self.thickness*0.5, hi/2, self.thickness, self.thickness, 0, color=Color.MAGENTA)
        elif "simple" in lockStyle :
            self.hole((wi - self.Margin)/2, hi/2, self.thickness*2)
            self.rectangularHole((wi - self.Margin)/2, hi/2, self.thickness, self.thickness, 0, color=Color.MAGENTA)
        if "top" in lockStyle :
            self.hole((wi - self.Margin)/2 - self.thickness, hi - self.thickness*4, self.thickness*2)
            self.rectangularHole((wi - self.Margin)/2 - self.thickness, hi - self.thickness*4, self.thickness, self.thickness, 0, color=Color.MAGENTA)
        if "bottom" in lockStyle :
            self.hole((wi - self.Margin)/2 - self.thickness, self.thickness*4, self.thickness*2)
            self.rectangularHole((wi - self.Margin)/2 - self.thickness, self.thickness*4, self.thickness, self.thickness, 0, color=Color.MAGENTA)

    def coverPanel2Side(self, wi, hi, lockStyle, move=None, label=""):
        if self.DoorFeetScrewLength > 0 and self.LockScrewDiameter > 0 :
            if self.move((wi + self.thickness*6 - self.Margin)/2, hi + self.thickness*2, move, True):
                return
            self.coverPanel2SideCallback(wi, hi, lockStyle)
            # plate
            self.edges["I"](wi/2 + self.thickness * 1.5 - self.LockScrewDiameter/2  - self.Margin/2)
            self.screwAttachement(self.DoorFeetScrewLength)
            self.polyline(self.thickness * 1.5 - self.LockScrewDiameter/2, 90, hi + self.thickness*2, 90, self.thickness * 1.5, 0)
            self.edges["J"](wi/2 + self.thickness * 1.5 - self.Margin/2)
            self.polyline(0, 90, hi, 90)
            # move plate
            self.move((wi + self.thickness*6 - self.Margin)/2, hi + self.thickness*2, move, label=label)
        else :
            self.rectangularWall((wi + self.thickness*6 - self.Margin)/2, hi, "IeJe", callback=[lambda:self.coverPanel2SideCallback(wi, hi, lockStyle)], move=move, label=label)

    def coverPanel3Side (self, wi, hi, lockStyle, move=None, label=""):
        if self.move(wi/2 + self.thickness*2, hi *3/4 + self.thickness*2, move, True):
            return
        # hinge holes for 3 pane panel
        if (self.HingeHolesDiameter > 0) :
            posy=0
            for y in self.HingeHolesCoverSeparation:
                posy += y
                self.hole(self.HingeHolesCoverEdgeDistance, posy, self.HingeHolesDiameter/2)
                self.hole(self.HingeHolesCoverEdgeDistance, hi * 3/4 + self.Margin/2 + self.thickness - posy, self.HingeHolesDiameter/2)
        # small extra lock t the bottom
        if "bottom" in lockStyle :
            self.hole((wi - self.Margin)/2 - self.thickness*3, self.thickness*4, self.thickness*2)
            self.rectangularHole((wi - self.Margin)/2 - self.thickness*3, self.thickness*4, self.thickness, self.thickness, 0, color=Color.MAGENTA)
        # plate
        if self.DoorFeetScrewLength > 0 and self.LockScrewDiameter > 0 :
            self.edge((wi - self.thickness - self.LockScrewDiameter - self.Margin)/2)
            self.screwAttachement(self.DoorFeetScrewLength)
            self.edge(self.thickness*1.5 - self.LockScrewDiameter/2)
        else :
            self.edge((wi + self.thickness*2 - self.Margin)/2)
        self.polyline(0, 90, (hi + self.thickness*2 - self.Margin)/2, 90,
                    (wi + self.thickness*2 - self.Margin)/4, -math.atan(2*(hi + self.thickness*2-self.Margin)/(wi + self.thickness*2-self.Margin))*180/math.pi,
                    math.sqrt(pow((hi + self.thickness*2 - self.Margin)/4, 2) + pow((wi + self.thickness*2 - self.Margin)/8, 2)), math.atan(2*(hi + self.thickness*2-self.Margin)/(wi + self.thickness*2-self.Margin))*180/math.pi,
                    (wi + self.thickness*2 - self.Margin)/8, 90, (hi + self.thickness*2 - self.Margin)*3/4, 90)
        # move plate
        self.move(wi/2 + self.thickness*2, hi *3/4 + self.thickness*2, move, label=label)

    def coverPanel3Top (self, wi, hi, lockStyle, move=None, label=""):
        if self.move(wi + self.thickness*2, hi/2 + self.thickness*2, move, True):
            return
        # lock hole
        if lockStyle == "with key" :
            self.hole((wi + self.thickness*2)/2, hi/2 - self.thickness*4, self.thickness*3.5)
            self.rectangularHole((wi + self.thickness*2)/2, hi/2 - self.thickness*4, self.thickness + self.Margin, self.thickness + self.Margin, 0, color=Color.MAGENTA)
            self.rectangularHole((wi + self.thickness*2)/2 - self.thickness*2, hi/2 - self.thickness*4, self.thickness, self.thickness, 0, color=Color.MAGENTA)
            self.rectangularHole((wi + self.thickness*2)/2 + self.thickness*2, hi/2 - self.thickness*4, self.thickness, self.thickness, 0, color=Color.MAGENTA)
        elif lockStyle == "simple" :
            self.hole((wi + self.thickness*2)/2, hi/2 - self.thickness*2.5, self.thickness*2)
            self.rectangularHole((wi + self.thickness*2)/2, hi/2 - self.thickness*2.5, self.thickness, self.thickness, 0, color=Color.MAGENTA)
        # hinge holes for 3 pane panel
        if (self.HingeHolesDiameter > 0)  :
            posx=0
            for x in self.HingeHolesCoverSeparation:
                posx += x
                self.hole(posx, self.HingeHolesCoverEdgeDistance, self.HingeHolesDiameter/2)
                self.hole(wi + self.thickness*2 - posx, self.HingeHolesCoverEdgeDistance, self.HingeHolesDiameter/2)
        # plate
        self.polyline(wi + self.thickness*2, 90, (hi + self.thickness*2 - self.Margin)/4, 90,
                    (wi + self.thickness*2)/8 + self.Margin/2, -math.atan(2*(hi + self.thickness*2-self.Margin)/(wi + self.thickness*2))*180/math.pi,
                    math.sqrt(pow((hi + self.thickness*2 - self.Margin)/4, 2) + pow((wi + self.thickness*2)/8, 2)), math.atan(2*(hi + self.thickness*2-self.Margin)/(wi + self.thickness*2))*180/math.pi,
                    (wi + self.thickness*2)/2 -  + self.Margin, math.atan(2*(hi + self.thickness*2-self.Margin)/(wi + self.thickness*2))*180/math.pi,
                    math.sqrt(pow((hi + self.thickness*2 - self.Margin)/4, 2) + pow((wi + self.thickness*2)/8, 2)), -math.atan(2*(hi + self.thickness*2-self.Margin)/(wi + self.thickness*2))*180/math.pi,
                    (wi + self.thickness*2)/8 + self.Margin/2, 90, (hi + self.thickness*2 - self.Margin)/4, 90)
        # move plate
        self.move(wi + self.thickness*2, hi/2 + self.thickness*2, move, label=label)

    def lockSimple (self, move=None):
        # external locking wheel
        if self.move(self.thickness*10, self.thickness*10, move, True):
            return
        self.parts.disc(self.thickness*10, callback=lambda:self.rectangularHole(0, 0, self.thickness, self.thickness))
        self.move(self.thickness*10, self.thickness*10, move, label="lock external")
        # grip wheel
        if self.move(self.thickness*6, self.thickness*6, move, True):
            return
        self.parts.wavyKnob(self.thickness*5, callback=lambda:self.rectangularHole(0, 0, self.thickness, self.thickness))
        self.move(self.thickness*6, self.thickness*6, move, label="lock grip")
        # pivot wheel
        #not needed, it is cut from the part directly
        # internal locking wheel
        if self.move(self.thickness*11, self.thickness*11, move, True):
            return
        self.parts.disc(self.thickness*10, dwidth=0.8, callback=lambda:self.rectangularHole(0, 0, self.thickness, self.thickness))
        self.move(self.thickness*11, self.thickness*11, move, label="lock internal")
        # discs attachment
        self.rectangularWall(self.thickness*4, self.thickness + self.PegsWidthMargin, "eeee", move=move)

    def lockExtra (self, move=None):
        # grip wheel
        if self.move(self.thickness*7, self.thickness*7, move, True):
            return
        self.parts.wavyKnob(self.thickness*5, callback=lambda:self.rectangularHole(0, 0, self.thickness, self.thickness))
        self.move(self.thickness*6, self.thickness*6, move, label="lock grip")
        # internal plate wheel
        if self.move(self.thickness*6 - self.Margin, self.thickness*6 - self.Margin, move, True):
            return
        self.parts.disc(self.thickness*6 - self.Margin, callback=lambda:self.rectangularHole(0, 0, self.thickness, self.thickness))
        self.move(self.thickness*6 - self.Margin, self.thickness*6, move, label="lock internal")
        # internal spacing wheel
        if self.move(self.thickness*6 - self.Margin, self.thickness*6 - self.Margin, move, True):
            return
        self.parts.disc(self.thickness*6 - self.Margin, callback=lambda:self.rectangularHole(0, 0, self.thickness, self.thickness))
        self.move(self.thickness*6 - self.Margin, self.thickness*6 - self.Margin, move, label="lock spacer")
        # internal locking wheel
        if self.move(self.thickness*8 - self.Margin, self.thickness*8 - self.Margin, move, True):
            return
        self.parts.disc(self.thickness*8 - self.Margin, dwidth=0.8, callback=lambda:self.rectangularHole(0, 0, self.thickness, self.thickness))
        self.move(self.thickness*8 - self.Margin, self.thickness*8 - self.Margin, move, label="lock locker")
        # discs attachment
        self.rectangularWall(self.thickness*5, self.thickness + self.PegsWidthMargin, "eeee", move=move)

    def keyHoles(self, centerHoleLength, isRotated=False):
        # center key hole
        if centerHoleLength == 2 :
            self.rectangularHole(-(self.thickness)/2, 0, self.thickness*2 + self.Margin, self.thickness+ self.Margin)
        elif centerHoleLength == 3 :
            self.rectangularHole(0, 0, self.thickness*3+ self.Margin, self.thickness + self.Margin)
        elif centerHoleLength == 1 :
            self.rectangularHole(0, 0, self.thickness+ self.Margin, self.thickness + self.Margin)
        # side holes
        if isRotated :
            self.rectangularHole(self.thickness*2, 0, self.thickness, self.thickness)
            self.rectangularHole(-self.thickness*2, 0, self.thickness, self.thickness)
        else :
            self.rectangularHole(0, self.thickness*2, self.thickness, self.thickness)
            self.rectangularHole(0, -self.thickness*2, self.thickness, self.thickness)

    def lockWithKey (self, isInnerLockRorated = False, move=None):
        # external locking wheel
        if self.move(self.thickness*15, self.thickness*15, move, True):
            return
        self.parts.disc(self.thickness*15, callback=lambda:self.keyHoles(2))
        self.move(self.thickness*15, self.thickness*15, move, label="lock external")
        # front wheel
        if self.move(self.thickness*8, self.thickness*8, move, True):
            return
        self.parts.wavyKnob(self.thickness*7, callback=lambda:self.keyHoles(3))
        self.move(self.thickness*8, self.thickness*8, move, label="lock front")
        # pivot wheel
        #not needed, it is cut from the part directly
        # internal locking wheel
        if self.move(self.thickness*15, self.thickness*15, move, True):
            return
        self.parts.disc(self.thickness*15, dwidth=12/15, callback=lambda:self.keyHoles(0, isInnerLockRorated))
        self.move(self.thickness*15, self.thickness*15, move, label="lock internal")
        # discs attachment
        self.rectangularWall(self.thickness*4, self.thickness + self.PegsWidthMargin, "eeee", move=move)
        self.rectangularWall(self.thickness*4, self.thickness + self.PegsWidthMargin, "eeee", move=move)
        # key
        if self.move(self.thickness*10, self.thickness*4, move, True):
            return
        self.rectangularHole(self.thickness, self.thickness, self.thickness, self.thickness, 0, False, False)
        self.polyline(self.thickness*3, 90, self.thickness, -90, self.thickness*3, -90, self.thickness, 90,
                    self.thickness*2, 90, self.thickness, -90, self.thickness, 90, self.thickness, 90,
                    self.thickness*2, -90, self.thickness, 90, self.thickness, 90, self.thickness, -90,
                    self.thickness*3, -90, self.thickness, 90, self.thickness*3, 90, self.thickness*3, 90)
        self.move(self.thickness*10, self.thickness*4, move, label="key")

    def render(self):
       hi = self.SheetHeight + self.Margin * 2 + ((self.thickness*2) if self.HandleThickness > 0 else 0)
       wi = self.SheetWidth + self.Margin
       di = self.SheetsStackDepth + self.Margin

       if self.FrontCoverStyle == "two-part lid with hinge eyes (both ends)" and self.FrontExtraDepth < 2 * HingeSettings.relative_params["hingestrength"] + HingeSettings.relative_params["axle"]/2 :
           self.FrontExtraDepth = 2 * HingeSettings.relative_params["hingestrength"] + HingeSettings.relative_params["axle"]/2
       if self.FrontCoverStyle == "slide-on lid" and self.FrontExtraDepth < 3 :
           self.FrontExtraDepth = 3
       if self.BackExtraDepth < 1 :
           self.BackExtraDepth = 1
       self.ctx.save()

       # front
       self.boxFrontBack (wi, hi, True, move="up", label="front")
       # back
       self.boxFrontBack (wi, hi, False, move="mirror up", label="back")

       # top
       self.boxTopBottom (wi, di, True, move="up", label="top")
       # bottom
       self.boxTopBottom (wi, di, False, move="up", label="bottom")

       # open sides
       self.boxOpenSide(hi, move="up")
       self.boxOpenSide(hi, move="mirror up")

       # side covers
       self.coverPanel1Lid (di, hi, True, move="rotated up", label="side panel")
       self.coverPanel1Lid (di, hi, True, move="rotated up", label="side panel")

       # top handle
       if self.HandleThickness > 0 and self.HandleWidth > 0 :
           self.topHandle (wi, di, move="up", label="top handle")

       # front panel cover
       # two-part lid hinge eyes (both ends)
       if self.FrontCoverStyle=="two-part lid with hinge eyes (both ends)":
           # front panel sides
           self.coverPanel2Side(wi, hi, "top bottom" if self.FrontExtraTopAndBottomLocks else "none", move="mirror up", label="front panel right")
           self.coverPanel2Side(wi, hi, self.FrontLockStyle, move="up", label="front panel left")
           # lock
           if  self.FrontLockStyle=="simple":
               self.lockSimple (move="up")
           elif self.FrontLockStyle=="with key":
               self.lockWithKey (True, move="up")
           #extra locks
           if self.FrontExtraTopAndBottomLocks:
               self.lockExtra(move="up")
               self.lockExtra(move="up")
               self.rectangularWall(self.thickness*16, self.thickness, "feee", move="up")
               self.rectangularWall(self.thickness*16, self.thickness, "feee", move="up")

       # three-part lid, higes not provided
       elif self.FrontCoverStyle=="three-part lid, higes not provided":
           # front panel sides
           self.coverPanel3Side(wi, hi, "bottom" if self.FrontExtraTopAndBottomLocks else "none", move="mirror up", label="front panel right")
           self.coverPanel3Side(wi, hi, "bottom" if self.FrontExtraTopAndBottomLocks else "none", move="up", label="front panel left")
           # front panel top
           self.coverPanel3Top(wi, hi, self.FrontLockStyle, move="up", label="front panel top")
           # lock
           if  self.FrontLockStyle=="simple":
               self.lockSimple (move="up")
           elif self.FrontLockStyle=="with key":
               self.lockWithKey (False, move="up")
           #extra locks
           if self.FrontExtraTopAndBottomLocks:
               self.lockExtra(move="up")
               self.lockExtra(move="up")
               self.rectangularWall(self.thickness*16, self.thickness, "feee", move="up")
               self.rectangularWall(self.thickness*16, self.thickness, "feee", move="up")
       # slide-on lid
       elif self.FrontCoverStyle=="slide-on lid":
           self.coverPanel1Lid (wi, hi, False, move="up", label="front panel")

       # back panel cover
       self.coverPanel1Lid (wi, hi, False, move="up", label="back panel")
