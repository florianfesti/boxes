from boxes import *


class SlidingLidBox(Boxes):
    """Box with rails for a sliding lid"""

    description = """* The sliding lid rests on the lower rails and is kept in place by the upper rails.
* When using inner measurements, the height goes from bottom to lid, the lower rail is inside of the inner height.
* The width of the rail can be adjusted, wider rails are more stable but make the opening smaller.
* The horizontal margin makes the lid slightly narrower to prevent the lid from jamming.
* The vertical margin makes the gap between the rails larger to let the lid slide more easily.

![Closed](static/samples/SlidingLidBox-2.jpg)
"""

    ui_group = "Box"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser(x=60.0, y=220.0, h=60.0, outside=False)
        self.argparser.add_argument(
            "--bottom_edge", action="store",
            type=ArgparseEdgeType("Fhs"), choices=list("Fhs"),
            default="F", help="edge type for bottom edge")
        self.argparser.add_argument(
            "--rail",  action="store", type=float, default=1.5,
            help="width of the rail (multiples of thickness)")
        self.argparser.add_argument(
            "--margin_t", action="store", type=float, default=0.1,
            help="vertical margin for sliding lid (multiples of thickness)")
        self.argparser.add_argument(
            "--margin_s", action="store", type=float, default=0.05,
            help="margin to add at both sides of sliding lid (multiples of thickness)")
        self.argparser.add_argument(
            "--lid_type", action="store", type=str, default="hole",
            choices={"hole", "lip", "none"}, help="add an optional grip hole to the lid")
        self.argparser.add_argument(
            "--hole_length", action="store", type=float, default=40,
            help="length of the grip hole in mm")
        self.argparser.add_argument(
            "--hole_width", action="store", type=float, default=20,
            help="width of the grip hole in mm")
        self.argparser.add_argument(
            "--hole_radius", action="store", type=float, default=10,
            help="radius of the grip hole in mm")

    def lowerRailHoles(self):
        # finger holes for bottom rails, subtracting half a thickness so the top sits right at self.h
        pos_h = self.h - 0.5 * self.thickness
        self.fingerHolesAt(pos_h, 0, self.y)

    def backHoles(self):
        # back holes for bottom rails, subtracting half a thickness so the top sits right at self.h
        pos_h = self.h - 0.5 * self.thickness
        self.fingerHolesAt(0, pos_h, self.rail_mm, 0)
        self.fingerHolesAt(self.x, pos_h, self.rail_mm, 180)

    def gripHole(self, lid_y):
        # grip hole x position: half a width from the edge, so subtracting one width to reach the middle
        pos_x = self.y - self.hole_width
        # grip hole y position: centered on the lid
        pos_y = lid_y / 2
        self.rectangularHole(pos_x, pos_y, self.hole_width,
                             self.hole_length, self.hole_radius)

    def render(self):
        # the size of the gap for the lid
        gap = (1 + self.margin_t) * self.thickness

        # correct for outside size
        if self.outside:
            self.x = self.adjustSize(self.x)
            self.y = self.adjustSize(self.y)
            # correct for the top and bottom edge, then also subtract the gap for the lid
            self.h = self.adjustSize(
                self.h, e1="F", e2=self.bottom_edge) - gap

        # rail width is a multiple of thickness -> calculate rail width in mm
        self.rail_mm = self.rail * self.thickness

        # the margin of the top edge, that is already taken up by the side rail, corrected for burn
        rail_margin = self.rail_mm - self.burn

        # the height of the side and back walls is bigger by the size of the gap
        h_plus = self.h + gap

        # start render
        self.ctx.save()

        # side walls
        # compound edge: f on bottom to match with F of front, E to span the gap for the lid
        sides_compound_edge = edges.CompoundEdge(self, "fE", [self.h, gap])
        self.rectangularWall(self.y, h_plus, [self.bottom_edge, sides_compound_edge, "F", "f"], callback=[
                             None, self.lowerRailHoles], move="up mirror", label="right side")
        self.rectangularWall(self.y, h_plus, [self.bottom_edge, sides_compound_edge, "F", "f"], callback=[
                             None, self.lowerRailHoles], move="up", label="left side")

        # bottom
        self.rectangularWall(self.y, self.x, "ffff", move="up", label="bottom")

        # rails
        # top rails: long edge toward the front, short edge toward the back
        self.rectangularWall(self.y, self.rail_mm, "fEee",
                             move="up mirror", label="top right rail")
        self.rectangularWall(self.y, self.rail_mm, "fEee",
                             move="up", label="top left rail")
        # bottom rails: short edge toward the front, finger joint toward the back
        self.rectangularWall(self.y, self.rail_mm, "feef",
                             move="up mirror", label="bottom right rail")
        self.rectangularWall(self.y, self.rail_mm, "feef",
                             move="up", label="bottom left rail")

        # lid
        # modify lid width by horizontal margin, to make the lid slide better
        lid_y = self.x - 2 * self.margin_s * self.thickness
        if self.lid_type == "lip":
            lip_copound_edge = edges.CompoundEdge(
                self, "EfE", [rail_margin, lid_y - 2 * rail_margin, rail_margin])
            # lid
            self.rectangularWall(
                self.y, lid_y, ["e", lip_copound_edge, "e", "e"], move="up", label="lid")
            # lid lip
            self.rectangularWall(lid_y - 2 * rail_margin, gap, "Feee",
                                 move="up", label="lid lip")
        elif self.lid_type == "hole":
            self.rectangularWall(self.y, lid_y, "eEee", move="up", label="lid",
                                 callback=[lambda: self.gripHole(lid_y)])
        else:
            self.rectangularWall(self.y, lid_y, "eEee", move="up", label="lid")

        # move to the right for the rest of the pieces
        self.ctx.restore()
        self.rectangularWall(self.y, h_plus, "ffff", move="right only")

        # back
        # compound edge: top edge in the middle, long edges to cover the ends of the side rails
        back_compound_edge = edges.CompoundEdge(
            self, ["E", "f", "E"], [rail_margin, self.x - 2 * rail_margin, rail_margin])
        self.rectangularWall(self.x, h_plus, [self.bottom_edge, "F", back_compound_edge, "F"],  callback=[
                             self.backHoles], move="up", label="back")

        # front
        # smaller height than the other walls to make space for the sliding lid
        self.rectangularWall(self.x, self.h, [self.bottom_edge, "F", "e", "F"],
                             move="up", label="front")

        # back rail
        # shorter back rail to make space for the side rails
        self.rectangularWall(self.x - 2 * rail_margin, self.rail_mm, "Feee",
                             move="up", label="back rail")
