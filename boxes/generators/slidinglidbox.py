from boxes import *


class SlidingLidBox(Boxes):
    """Box with rails for a sliding lid"""

    description = """* The sliding lid rests on the lower rails and is kept in place by the upper rails.
* When using inner measurements, the height goes from bottom to lid, the lower rail is inside of the inner height.
* The width of the rail can be adjusted, wider rails are more stable but make the opening smaller.
* The horizontal margin makes the lid slightly narrower to prevent the lid from jamming.
* The vertical margin makes the gap between the rails larger to let the lid slide more easily.
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

    def hHoles(self):
        pos_h = self.h - 0.5 * self.thickness
        self.fingerHolesAt(pos_h, 0, self.y)

    def backHoles(self):
        pos_h = self.h - 0.5 * self.thickness
        self.fingerHolesAt(0, pos_h, self.rail_mm, 0)
        self.fingerHolesAt(self.x, pos_h, self.rail_mm, 180)

    def render(self):
        # top edge, set fix to finger jonts opposing
        self.top_edge = "F"

        # the size of the gap for the lid
        gap = (1 + self.margin_t) * self.thickness

        # correct for outside size
        if self.outside:
            self.x = self.adjustSize(self.x)
            self.y = self.adjustSize(self.y)
            # correct for the top and bottom edge, then also subtract the gap for the lid
            self.h = self.adjustSize(
                self.h, e1=self.top_edge, e2=self.bottom_edge) - gap

        # rail width is a multiple of thickness -> calculate rail width in mm
        self.rail_mm = self.rail * self.thickness

        # the height of the side and back walls is bigger by the size of the gap
        h_plus = self.h + gap

        # start render
        self.ctx.save()

        # side walls
        # compound edge: f on bottom to match with F of front, E to span the gap for the lid
        sides_compound_edge = edges.CompoundEdge(self, "fE", [self.h, gap])
        self.rectangularWall(self.y, h_plus, [self.bottom_edge, sides_compound_edge, self.top_edge, "f"], callback=[
                             None, self.hHoles, ], move="up mirror", label="right side")
        self.rectangularWall(self.y, h_plus, [self.bottom_edge, sides_compound_edge, self.top_edge, "f"], callback=[
                             None, self.hHoles, ], move="up", label="left side")

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
        x_lid = self.x - 2 * self.margin_s * self.thickness
        self.rectangularWall(self.y, x_lid, "eEee", move="up", label="lid")

        # move to the right for the rest of the pieces
        self.ctx.restore()
        self.rectangularWall(self.y, h_plus, "ffff", move="right only")

        # back
        # the margin of the back top edge, that is already taken up by the side rail, corrected fur burn
        rail_margin = self.rail_mm - self.burn
        # compound edge: top edge in the middle, long edges to cover the ends of the side rails
        back_compound_edge = edges.CompoundEdge(
            self, ["E", self.top_edge, "E"], [rail_margin, self.x - 2 * rail_margin, rail_margin])
        self.rectangularWall(self.x, h_plus, [self.bottom_edge, "F", back_compound_edge, "F"],  callback=[
                             self.backHoles], move="up", label="back")

        # front
        # smaller height than the other walls to make space for the sliding lid
        self.rectangularWall(self.x, self.h, [self.bottom_edge, "F", "e", "F"],
                             move="up", label="front")

        # back rail
        # shorter back rail to make space for the side rails
        self.rectangularWall(self.x - 2 * rail_margin, self.rail_mm, "feee",
                             move="up", label="back rail")
