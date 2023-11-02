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


class FrontEdge(edges.BaseEdge):
    char = "a"

    def __call__(self, length, **kw):
        x = math.ceil( ((self.canDiameter * 0.5 + 2 * self.thickness) * math.sin(math.radians(self.chuteAngle))) / self.thickness)
        if self.top_edge != "e":
            self.corner(90, self.thickness)
            self.edge(0.5 * self.canDiameter)            
            self.corner(-90, 0.25 * self.canDiameter)
        else:
            self.moveTo(-self.burn, self.canDiameter + self.thickness, -90)
            self.corner(90, 0.25 * self.canDiameter)
            self.edge(self.thickness)

        self.edge(0.5 * self.canDiameter - self.thickness)
        self.corner(-90, 0.25 * self.canDiameter)
        self.edge(0.5 * self.canDiameter)
        self.corner(90, self.thickness)
        self.edge(x * self.thickness )
        self.corner(90, self.thickness)
        self.edge(0.5 * self.canDiameter)
        self.corner(-90, 0.25 * self.canDiameter)
        self.edge(0.5 * self.canDiameter - (1 + x) * self.thickness + self.top_chute_height + self.bottom_chute_height - self.barrier_height)
        self.corner(-90, 0.25 * self.canDiameter)
        self.edge(0.5 * self.canDiameter)
        self.corner(90, self.thickness)
        self.edge(self.barrier_height)
        self.edge(self.thickness)

class TopChuteEdge(edges.BaseEdge):
    char = "b"

    def __call__(self, length, **kw):
        self.edge(0.2 * length - self.thickness)
        self.corner(90, self.thickness)
        self.edge(1.5*self.canDiameter - 2 * self.thickness)
        self.corner(-90, self.thickness)
        self.edge(0.6 * length - 2 * self.thickness)
        self.corner(-90, self.thickness)
        self.edge(1.5*self.canDiameter - 2 * self.thickness)
        self.corner(90, self.thickness)
        self.edge(0.2 * length - self.thickness)

class BarrierEdge(edges.BaseEdge):
    char = "A"

    def __call__(self, length, **kw):
        self.edge(0.2*length)
        self.corner(90,self.thickness/2)
        self.corner(-90,self.thickness/2)
        self.edge(0.6*length-2*self.thickness)
        self.corner(-90,self.thickness/2)
        self.corner(90,self.thickness/2)
        self.edge(0.2*length)

    def startwidth(self) -> float:
        return self.boxes.thickness

class CanStorage(Boxes):
    """Storage box for round containers"""

    description = """
for AA batteries:

![CanStorage for AA batteries](static/samples/CanStorageAA.jpg)

for canned tomatoes:
"""


    ui_group = "Misc"
    
    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, finger=2.0, space=2.0, surroundingspaces=0.0)
        self.addSettingsArgs(edges.StackableSettings)
        self.addSettingsArgs(fillHolesSettings)

        self.argparser.add_argument(
            "--top_edge", action="store",
            type=ArgparseEdgeType("efhŠ"), choices=list("efhŠ"),
            default="Š", help="edge type for top edge")
        self.argparser.add_argument(
            "--bottom_edge", action="store",
            type=ArgparseEdgeType("eEš"), choices=list("eEš"),
            default="š", help="edge type for bottom edge")

        # Add non default cli params if needed (see argparse std lib)
        self.argparser.add_argument(
            "--canDiameter",  action="store", type=float, default=75,
            help="outer diameter of the cans to be stored (in mm)")
        self.argparser.add_argument(
            "--canHeight",  action="store", type=float, default=110,
            help="height of the cans to be stored (in mm)")
        self.argparser.add_argument(
            "--canNum",  action="store", type=int, default=12,
            help="number of cans to be stored")
        self.argparser.add_argument(
            "--chuteAngle",  action="store", type=float, default=5.0,
            help="slope angle of the chutes")
        
    def DrawPusher(self, dbg = False):
        with self.saved_context():
            if dbg == False:
                self.moveTo(0,self.thickness)
            self.edge(0.25*self.pusherA)
            self.corner(-90)
            self.edge(self.thickness)
            self.corner(90)
            self.edge(0.5*self.pusherA)
            self.corner(90)
            self.edge(self.thickness)
            self.corner(-90)
            self.edge(0.25*self.pusherA)
            
            self.corner(90-self.chuteAngle)
            
            self.edge(0.25*self.pusherB)
            self.corner(-90)
            self.edge(self.thickness)
            self.corner(90)
            self.edge(0.5*self.pusherB)
            self.corner(90)
            self.edge(self.thickness)
            self.corner(-90)
            self.edge(0.25*self.pusherB)

            self.corner(90+self.pusherAngle+self.chuteAngle)
            self.edge(self.pusherC)
        
    def cb_top_chute(self, nr):
        if nr == 0:
            # fill with holes
            border = [
                (0, 0), 
                (self.top_chute_depth, 0), 
                (self.top_chute_depth, 0.2 * self.width - self.thickness), 
                (self.top_chute_depth - self.thickness, 0.2 * self.width), 
                (self.top_chute_depth - 1.5*self.canDiameter, 0.2 * self.width), 
                (self.top_chute_depth - 1.5*self.canDiameter, 0.8 * self.width), 
                (self.top_chute_depth - self.thickness, 0.8 * self.width), 
                (self.top_chute_depth, 0.8 * self.width + self.thickness), 
                (self.top_chute_depth, self.width), 
                (0, self.width),                
                ]

            if self.fillHoles_fill_pattern != "no fill":
                self.fillHoles(
                    pattern="hbar", 
                    border=border,
                    max_radius = min(2*self.thickness, self.fillHoles_hole_max_radius) if self.fillHoles_fill_pattern in ["hbar", "vbar"] else min(2*self.thickness, self.width/30),
                    hspace=min(2*self.thickness, self.fillHoles_space_between_holes) if self.fillHoles_fill_pattern in ["hbar", "vbar"] else min(2*self.thickness, self.width/20),
                    bspace=min(2*self.thickness, self.fillHoles_space_to_border)  if self.fillHoles_fill_pattern in ["hbar", "vbar"] else min(2*self.thickness, self.width/20),
                    bar_length=self.fillHoles_bar_length,
                    max_random=self.fillHoles_max_random,
                    )           
        
    def cb_top(self, nr):
        if nr == 0:
            # fill with holes
            border = [
                (0, 0), 
                (self.depth, 0), 
                (self.depth, self.width), 
                (0, self.width),                
                ]

            if self.fillHoles_fill_pattern != "no fill":
                self.fillHoles(
                    pattern="hbar", 
                    border=border,
                    max_radius = min(2*self.thickness, self.fillHoles_hole_max_radius) if self.fillHoles_fill_pattern in ["hbar", "vbar"] else min(2*self.thickness, self.width/30),
                    hspace=min(2*self.thickness, self.fillHoles_space_between_holes) if self.fillHoles_fill_pattern in ["hbar", "vbar"] else min(2*self.thickness, self.width/20),
                    bspace=min(2*self.thickness, self.fillHoles_space_to_border)  if self.fillHoles_fill_pattern in ["hbar", "vbar"] else min(2*self.thickness, self.width/20),
                    bar_length=self.fillHoles_bar_length,
                    max_random=self.fillHoles_max_random,
                    )            

    def cb_bottom_chute(self, nr):
        if nr == 1:
            # holes for pusher
            self.rectangularHole(self.width*0.85-0.5*self.thickness, 0.25*self.pusherA, self.thickness, 0.5*self.pusherA, center_x=False, center_y=False)
            self.rectangularHole(self.width*0.5 -0.5*self.thickness, 0.25*self.pusherA, self.thickness, 0.5*self.pusherA, center_x=False, center_y=False)
            self.rectangularHole(self.width*0.15-0.5*self.thickness, 0.25*self.pusherA, self.thickness, 0.5*self.pusherA, center_x=False, center_y=False)
            

    def cb_back(self, nr):
        if nr == 1:
            # holes for pusher
            self.rectangularHole(self.width*0.85-0.5*self.thickness, self.thickness + self.depth * math.tan(math.radians(self.chuteAngle)) + 0.25*self.pusherB, self.thickness, 0.5*self.pusherB + self.thickness, center_x=False, center_y=False)
            self.rectangularHole(self.width*0.5 -0.5*self.thickness, self.thickness + self.depth * math.tan(math.radians(self.chuteAngle)) + 0.25*self.pusherB, self.thickness, 0.5*self.pusherB + self.thickness, center_x=False, center_y=False)
            self.rectangularHole(self.width*0.15-0.5*self.thickness, self.thickness + self.depth * math.tan(math.radians(self.chuteAngle)) + 0.25*self.pusherB, self.thickness, 0.5*self.pusherB + self.thickness, center_x=False, center_y=False)

            
    def cb_sides(self, nr):
        if nr == 0:
            # for debugging only
            if self.debug:
                # draw orientation points
                self.hole(0, 0, 1, color=Color.ANNOTATIONS)
                self.hole(0, self.thickness, 1, color=Color.ANNOTATIONS)
                self.hole(0, self.thickness + self.canDiameter, 1, color=Color.ANNOTATIONS)
                self.hole(0, self.thickness + self.canDiameter + self.bottom_chute_height, 1, color=Color.ANNOTATIONS)
                self.hole(0, self.thickness + self.canDiameter + self.bottom_chute_height + self.top_chute_height + self.thickness, 1, color=Color.ANNOTATIONS)
                self.hole(0, self.thickness + self.canDiameter + self.bottom_chute_height + self.top_chute_height + self.thickness + self.canDiameter, 1, color=Color.ANNOTATIONS)
                self.hole(0, self.thickness + self.canDiameter + self.bottom_chute_height + self.top_chute_height + self.thickness + self.canDiameter + 1.0 * self.thickness, 1, color=Color.ANNOTATIONS)
                with self.saved_context():
                    # draw cans, bottom row
                    self.moveTo(0, self.thickness, self.chuteAngle)
                    self.rectangularHole(2*self.thickness, 0, math.ceil(self.canNum / 2) * self.canDiameter, self.canDiameter, center_x=False, center_y=False, color=Color.ANNOTATIONS)
                    for i in range(math.ceil(self.canNum / 2)-1):
                        self.hole(2*self.thickness+(0.5 + i) * self.canDiameter, self.canDiameter / 2, self.canDiameter / 2, color=Color.ANNOTATIONS)
                    i+=1
                    self.hole(2*self.thickness+(0.5 + i) * self.canDiameter, self.canDiameter*0.8 , self.canDiameter / 2, color=Color.ANNOTATIONS)

                with self.saved_context():
                    # draw pusher
                    self.moveTo(self.depth-self.pusherA, self.thickness + (self.depth-self.pusherA) * math.tan(math.radians(self.chuteAngle)))
                    self.moveTo(0,0,self.chuteAngle)
                    self.DrawPusher(True)
                    
                with self.saved_context():
                    # draw cans, top row
                    self.moveTo(0, self.thickness + self.canDiameter + self.bottom_chute_height + self.top_chute_height + 0.5 * self.thickness, -self.chuteAngle)
                    self.rectangularHole(0, 0.5 * self.thickness, math.ceil(self.canNum / 2) * self.canDiameter, self.canDiameter, center_x=False, center_y=False, color=Color.ANNOTATIONS)
                    for i in range(math.ceil(self.canNum / 2)):
                        self.hole((0.5 + i) * self.canDiameter, self.canDiameter / 2 + 0.5 * self.thickness, self.canDiameter / 2, color=Color.ANNOTATIONS)
                with self.saved_context():
                    # draw barrier
                    self.moveTo(1.5 * self.thickness, 1.1 * self.thickness + self.burn + math.sin(math.radians(self.chuteAngle)) * 2 * self.thickness, 90)
                    self.rectangularHole(0, 0, self.barrier_height, self.thickness, center_x=False, center_y=True, color=Color.ANNOTATIONS)

            # bottom chute
            with self.saved_context():
                self.moveTo(0, 0.5 * self.thickness, self.chuteAngle)
                self.fingerHolesAt(0, 0, self.depth / math.cos(math.radians(self.chuteAngle)), 0)
            # top chute
            with self.saved_context():
                self.moveTo(0, self.thickness + self.canDiameter + self.bottom_chute_height + self.top_chute_height + 0.5 * self.thickness, -self.chuteAngle)
                self.fingerHolesAt(0, 0, self.top_chute_depth, 0)
            # front barrier
            with self.saved_context():
                self.moveTo(1.5 * self.thickness, 1.1 * self.thickness + self.burn + math.sin(math.radians(self.chuteAngle)) * 2 * self.thickness, 90)
                self.fingerHolesAt(0, 0, self.barrier_height, 0)
            # fill with holes
            border = [
                (2*self.thickness, 0.5*self.thickness + 2*self.thickness * math.tan(math.radians(self.chuteAngle)) + 0.5*self.thickness/math.cos(math.radians(self.chuteAngle))), 
                (self.depth, self.thickness + self.depth * math.tan(math.radians(self.chuteAngle))), 
                (self.depth, self.height), 
                (self.thickness + 0.75 * self.canDiameter, self.height),
                (self.thickness + 0.75 * self.canDiameter,                  0.5*self.thickness + self.canDiameter + self.bottom_chute_height + self.top_chute_height + self.thickness - (self.thickness + 0.75 * self.canDiameter) * math.tan(math.radians(self.chuteAngle)) + 0.5*self.thickness/math.cos(math.radians(self.chuteAngle))),
                (self.top_chute_depth * math.cos(math.radians(self.chuteAngle)), self.thickness + self.canDiameter + self.bottom_chute_height + self.top_chute_height + self.thickness - (self.top_chute_depth) * math.sin(math.radians(self.chuteAngle))),
                (self.top_chute_depth * math.cos(math.radians(self.chuteAngle)), self.thickness + self.canDiameter + self.bottom_chute_height + self.top_chute_height - (self.top_chute_depth) * math.sin(math.radians(self.chuteAngle))),
                (self.thickness + 0.75 * self.canDiameter,                  1.5*self.thickness + self.canDiameter + self.bottom_chute_height + self.top_chute_height - (self.thickness + 0.75 * self.canDiameter) * math.tan(math.radians(self.chuteAngle)) - 0.5*self.thickness/math.cos(math.radians(self.chuteAngle))),
                (self.thickness + 0.75 * self.canDiameter, 2*self.thickness + self.barrier_height ),
                (2*self.thickness, 2*self.thickness + self.barrier_height), 
                ]

            self.fillHoles(
                pattern=self.fillHoles_fill_pattern, 
                border=border, 
                max_radius=self.fillHoles_hole_max_radius, 
                hspace=self.fillHoles_space_between_holes, 
                bspace=self.fillHoles_space_to_border, 
                min_radius=self.fillHoles_hole_min_radius, 
                style=self.fillHoles_hole_style,
                bar_length=self.fillHoles_bar_length,
                max_random=self.fillHoles_max_random,
                )
        
    def render(self):
        self.chuteAngle = self.chuteAngle
        
        self.pusherAngle = 30 # angle of pusher
        self.pusherA = 0.75 * self.canDiameter # length of pusher
        self.pusherB = self.pusherA / math.sin(math.radians(180 - (90+self.chuteAngle) - self.pusherAngle)) * math.sin(math.radians(self.pusherAngle))
        self.pusherC = self.pusherA / math.sin(math.radians(180 - (90+self.chuteAngle) - self.pusherAngle)) * math.sin(math.radians(90+self.chuteAngle))
    
        self.addPart(FrontEdge(self, self))
        self.addPart(TopChuteEdge(self, self))
        self.addPart(BarrierEdge(self, self))
        
        if self.canDiameter < 8 * self.thickness:
            self.edges["f"].settings.setValues(self.thickness, True, finger=1.0)
            self.edges["f"].settings.setValues(self.thickness, True, space=1.0)
        self.edges["f"].settings.setValues(self.thickness, True, surroundingspaces=0.0)
        
        if self.canDiameter < 4 * self.thickness:
            raise ValueError("Can diameter has to be at least 4 times the material thickness!")

        if self.canNum < 4:
            raise ValueError("4 cans is the minimum!")

        self.depth = self.canDiameter * (math.ceil(self.canNum / 2) + 0.1) + self.thickness
        self.top_chute_height = max(self.depth * math.sin(math.radians(self.chuteAngle)), 0.1 * self.canDiameter)
        self.top_chute_depth = (self.depth - 1.1 * self.canDiameter) / math.cos(math.radians(self.chuteAngle))
        self.bottom_chute_height = max((self.depth - 1.1 * self.canDiameter) * math.sin(math.radians(self.chuteAngle)), 0.1 * self.canDiameter)
        self.bottom_chute_depth = self.depth / math.cos(math.radians(self.chuteAngle))
        self.barrier_height = 0.25 * self.canDiameter
        
        if (self.top_chute_depth + self.bottom_chute_height - self.thickness) < (self.barrier_height + self.canDiameter * 0.1):
            self.bottom_chute_height = self.barrier_height + self.canDiameter * 0.1 + self.thickness - self.top_chute_depth
        
        self.height = self.thickness + self.canDiameter + self.bottom_chute_height + self.top_chute_height + 0.5 * self.thickness + self.canDiameter + 1.5 * self.thickness # measurements from bottom to top
        self.width = 0.01 * self.canHeight + self.canHeight + 0.01 * self.canHeight
        edgs = self.bottom_edge + "h" + self.top_edge + "a"
        
        # render your parts here
        self.rectangularWall(self.depth, self.height, edges=edgs, callback=self.cb_sides, move="up", label="right")
        self.rectangularWall(self.depth, self.height, edges=edgs, callback=self.cb_sides, move="up mirror", label="left")
        
        self.rectangularWall(self.bottom_chute_depth, self.width, "fefe", callback=self.cb_bottom_chute, move="up", label="bottom chute")
        self.rectangularWall(self.top_chute_depth, self.width, "fbfe", callback=self.cb_top_chute, move="up", label="top chute")

        self.rectangularWall(self.barrier_height, self.width, "fAfe", move="right", label="barrier")
        self.rectangularWall(self.height, self.width, "fefe", callback=self.cb_back, move="up", label="back")
        self.rectangularWall(self.barrier_height, self.width, "fefe", move="left only", label="invisible")
        
        if self.top_edge != "e":
            self.rectangularWall(self.depth, self.width, "fefe", callback=self.cb_top, move="up", label="top")
            
        pusherH = self.pusherB * math.cos(math.radians(self.chuteAngle)) + self.thickness
        pusherV = self.pusherC * math.cos(math.radians(self.chuteAngle)) + self.thickness

        self.move(pusherV, pusherH, where ="right", before=True, label="Pusher")
        self.DrawPusher()
        self.move(pusherV, pusherH, where ="right", before=False, label="Pusher")
        self.move(pusherV, pusherH, where ="right", before=True, label="Pusher")
        self.DrawPusher()
        self.move(pusherV, pusherH, where ="right", before=False, label="Pusher")
        self.move(pusherV, pusherH, where ="up", before=True, label="Pusher")
        self.DrawPusher()
        self.text("Glue the Pusher pieces into slots on bottom\nand back plates to prevent stuck cans.", pusherV+3,0, fontsize=4, color=Color.ANNOTATIONS)
        self.move(pusherV, pusherH, where ="up", before=False, label="Pusher")

        self.move(pusherV, pusherH, where ="left only", before=True, label="Pusher")
        self.move(pusherV, pusherH, where ="left only", before=True, label="Pusher")

        if self.bottom_edge == "š":
            self.rectangularWall(self.edges["š"].settings.width+3*self.thickness, self.edges["š"].settings.height-4*self.burn, "eeee", move="right", label="Stabilizer 1")
            self.rectangularWall(self.edges["š"].settings.width+3*self.thickness, self.edges["š"].settings.height-4*self.burn, "eeee", move="right", label="Stabilizer 2")
            self.rectangularWall(self.edges["š"].settings.width+5*self.thickness, self.edges["š"].settings.height-4*self.burn, "eeee", move="right", label="Stabilizer 3")
            self.rectangularWall(self.edges["š"].settings.width+5*self.thickness, self.edges["š"].settings.height-4*self.burn, "eeee", move="right", label="Stabilizer 4")
            self.text("Glue a stabilizer on the inside of each bottom\nside stacking foot for lateral stabilization.",3 ,0 , fontsize=4, color=Color.ANNOTATIONS)

