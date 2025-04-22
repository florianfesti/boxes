from boxes import *
from boxes.edges import FingerJointEdge

# Dependent generators for drawers
from boxes.generators.abox import ABox
from boxes.generators.dividertray import DividerTray

class AlternatingFingerJointEdgeEven(FingerJointEdge):
    """Alternating finger joint edge """
    char = 'a'
    description = "Alternating Finger Joint"
    positive = True

    # Pasted from FingerJointEdge but with added alternate args and rendering
    def __call__(self, length, bedBolts=None, bedBoltSettings=None, alternate=True, altMod=0, **kw):
      positive = self.positive
      t = self.settings.thickness

      s, f = self.settings.space, self.settings.finger
      thickness = self.settings.thickness
      style = self.settings.style
      play = self.settings.play

      fingers, leftover = self.calcFingers(length, bedBolts)

      if (fingers == 0 and f and
              leftover > 0.75 * thickness and leftover > 4 * play):
          fingers = 1
          f = leftover = leftover / 2.0
          bedBolts = None
          style = "rectangular"

      if not positive:
          f += play
          s -= play
          leftover -= play

      self.edge(leftover / 2.0, tabs=1)

      l1, l2 = self.fingerLength(self.settings.angle)
      h = l1 - l2

      d = (bedBoltSettings or self.bedBoltSettings)[0]

      for i in range(fingers):
          if i != 0:
              if not positive and bedBolts and bedBolts.drawBolt(i):
                  self.hole(0.5 * s,
                            0.5 * self.settings.thickness, 0.5 * d)

              if positive and bedBolts and bedBolts.drawBolt(i):
                  self.bedBoltHole(s, bedBoltSettings)
              else:
                  self.edge(s)

          # Skip finger if alternating
          if alternate and i % 2 == altMod:
              self.edge(f)
          else:
              self.draw_finger(f, h, style,
                               positive, i < fingers // 2)

      self.edge(leftover / 2.0, tabs=1)

class AlternatingFingerJointEdgeOdd(AlternatingFingerJointEdgeEven):
    """Alternating finger joint edge """
    char = 'b'
    description = "Alternating Finger Joint"
    positive = True

    def __call__(self, length, bedBolts=None, bedBoltSettings=None, alternate=True, altMod=1, **kw):
        fingers, leftover = self.calcFingers(length, bedBolts)
        # Handles odd number of fingers
        if fingers % 2 == 0:
            altMod = 0

        super().__call__(length, bedBolts, bedBoltSettings, alternate=alternate, altMod=altMod, **kw)

class DrawerSettings(edges.Settings):
    """Settings for the Drawers
Values:
* absolute

    * style : "ABox" : generator to use for drawers
    * notched : False : notches in drawer (DividerTray only)
    * bottom_edge : "F" : bottom edge for drawer (ABox only)

* relative (in multiples of thickness)

    * depth_reduction : 0.0 : drawer depth reduction for adding stop block inside
    * tolerance : 0.5 : tolerance for drawer fit
    * num_dividers : 5 : number of dividers in each drawer (DividerTray only)
    """
    absolute_params = {
        "style": ("none", "ABox", "DividerTray"),
        "notched": False,
        "bottom_edge": ("F", "e"),
    }

    relative_params = {
        "depth_reduction": 0.0,
        "tolerance": 0.5,
        "num_dividers": 5,
    }

class ApothecaryDrawerBox(Boxes):
    """Apothecary style sliding drawer box"""

    ui_group = "Box"
    description = """## Apothecary style sliding drawer box
Apothecary style sliding drawer box that uses alternating finger joints
for inner shelves to save on materials.

It leverages existing generators to create drawers, or you can
generate your own to suit your specific use case.

Default settings fit in a Kallax cube giving you 12 drawers. These drawers
can each fit most popular TCG cards.
"""

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, finger=2.0, space=2.0)

        self.addSettingsArgs(DrawerSettings, style="none", notched=False,
                             depth_reduction=0.0, tolerance=0.5)

        self.buildArgParser(x=334, y=374, h=334, outside=True)

        self.argparser.add_argument(
            "--rows",  action="store", type=int, default=3,
            help="number of rows")

        self.argparser.add_argument(
            "--cols",  action="store", type=int, default=4,
            help="number of columns")

        self.argparser.add_argument(
            "--generate_drawers",  action="store", type=BoolArg(), default=True,
            help="generate drawers using DividerTray")

    def render(self):
        x, y, h = self.x, self.y, self.h
        rows = self.rows
        cols = self.cols
        t = self.thickness

        if self.outside:
            self.x = x = self.adjustSize(x, "f", "f")
            self.y = y = self.adjustSize(y, "e")
            self.h = h = self.adjustSize(h, "f", "f")

        self.unit_w, self.unit_h = unit_w, unit_h = self.unit_dimensions()

        drawer_settings = self.edgesettings['Drawer']
        drawer_style = drawer_settings['style']

        # Add alternating finger joint edges
        altEven = AlternatingFingerJointEdgeEven(self, self.edges["f"].settings)
        self.addPart(altEven)
        altOdd = AlternatingFingerJointEdgeOdd(self, self.edges["f"].settings)
        self.addPart(altOdd)

        # Back panel
        self.rectangularWall(x, h, "ffff", label="back", callback=[self.back_panel_slot_holes_callback], move="up")

        # Top/Bottom
        with self.saved_context():
            for i in range(2):
                self.rectangularWall(x, y, "eFFF", label="top/bottom", callback=[self.vertical_slot_holes_callback], move="right")

        self.rectangularWall(x, y, "ffff", move="up only")

        # Left/Right walls
        with self.saved_context():
            for i in range(2):
                self.rectangularWall(y, h, "fFfe", label="left/right", callback=[self.horizontal_slot_holes_callback], move="right")

        self.rectangularWall(x, h, "ffff", move="up only")

        # Inner walls
        num_inner_walls = cols - 1
        with self.saved_context():
            for i in range(num_inner_walls):
                self.rectangularWall(y, h, "fffe", label="divider", callback=[self.horizontal_slot_holes_callback], move="right")

        self.rectangularWall(x, h, "ffff", move="up only")

        # Shelves
        num_edge_shelves = 0 if cols < 2 else rows -1
        num_inner_shelves = (rows - 1) * (cols - 2)
        num_single_col_shelves = 0 if cols > 1 else rows - 1
        shelf_width = unit_w + (self.thickness * 2)

        with self.saved_context():
            for i in range(num_edge_shelves):
                self.rectangularWall(unit_w, y, "ebff", label="left shelf", move="right")
                self.rectangularWall(unit_w, y, "effa", label="right shelf", move="right")

            for i in range(num_inner_shelves):
                self.rectangularWall(unit_w, y, "ebfa", label="inner shelf", move="right")

            for i in range(num_single_col_shelves):
                self.rectangularWall(unit_w, y, "efff", label="shelf", move="right")

        self.rectangularWall(unit_w, y, "efff", move="up only")

        # Drawers
        if drawer_style != "none":
            num_drawers = rows * cols

            if self.labels:
                self.text(f"{num_drawers} sets of generated drawers using {drawer_style} generator --^", fontsize=6, color=Color.ANNOTATIONS)
                self.moveTo(0, 10)

            # Use existing generators to create drawers
            for i in range(num_drawers):
                with self.saved_context():
                    drawer_gen, render_width = self.drawerGenerator(drawer_style, drawer_settings, labels=self.labels, outside=self.outside)
                    drawer_gen._buildObjects()
                    drawer_gen.render()

                # Reset positioning for rendering next iteration
                self.moveTo(render_width + 5, 0)

    def back_panel_slot_holes_callback(self):
        self.vertical_slot_holes_callback(self.h)

        for col in range(self.cols):
            posx = col * (self.unit_w + self.thickness + (self.burn * 2))
            for row in range(self.rows - 1):
                posy = ((row + 1) * self.unit_h) + (self.thickness / 2) + (self.thickness * row)
                self.fingerHolesAt(posx, posy, self.unit_w, angle=0)

    def vertical_slot_holes_callback(self, length=None):
        length = length or self.y
        for col in range(1, self.cols):
            posx = 0.5 * self.thickness + col * self.unit_w + (col - 1) * self.thickness
            self.fingerHolesAt(posx, 0, length, angle=90)

    def horizontal_slot_holes_callback(self):
        for row in range(1, self.rows):
            posy = 0.5 * self.thickness + row * self.unit_h + (row - 1) * self.thickness
            self.fingerHolesAt(0, posy, self.y, angle=0)

    def unit_dimensions(self):
        total_inner_width = self.x - (self.thickness * (self.cols - 1))
        total_inner_height = self.h - (self.thickness * (self.rows - 1))
        unit_w = total_inner_width / self.cols
        unit_h = total_inner_height / self.rows
        return unit_w, unit_h

    def drawerGenerator(self, drawer_style, drawer_settings, labels, outside):
        """Return a generator object based on the style name"""

        drawer_width = self.unit_w
        drawer_height = self.unit_h
        drawer_depth = self.y

        if drawer_settings['tolerance'] > 0:
            drawer_width -= drawer_settings['tolerance']
            drawer_height -= drawer_settings['tolerance']
            drawer_depth -= drawer_settings['tolerance']

        if drawer_settings['depth_reduction'] > 0:
            drawer_depth -= drawer_settings['depth_reduction']

        if drawer_style == "ABox":
            bottom_edge = drawer_settings['bottom_edge'] or "F"
            args = [
                f"--x={drawer_width}",
                f"--y={drawer_depth}",
                f"--h={drawer_height}",
                f"--bottom_edge={bottom_edge}",
            ]

            gen = ABox()
            gen.parseArgs(args)
            render_width = drawer_width + drawer_depth

        elif drawer_style == "DividerTray":
            num_dividers = drawer_settings['num_dividers'] + 1
            div_depth = drawer_depth / num_dividers

            args = [
                f"--sx={drawer_width}*1",
                f"--sy={div_depth}*{num_dividers}",
                f"--h={drawer_height}",
                f"--bottom=True"
            ]

            if drawer_settings['notched'] == False:
                args.append(f"--Notch_depth=0")
                args.append(f"--Notch_lower_radius=0")
                args.append(f"--Notch_upper_radius=0")

            gen = DividerTray()
            gen.parseArgs(args)
            render_width = max(drawer_width, drawer_depth) + drawer_width

        else:
            raise ValueError(f"Invalid generator: {drawer_style}")

        gen.thickness = self.thickness
        gen.ctx = self.ctx
        gen.outside = outside
        gen.labels = labels
        gen.label_format = self.label_format
        gen.spacing = self.spacing
        gen.edgesettings = self.edgesettings
        gen.bedBoltSettings = self.bedBoltSettings
        gen.hexHolesSettings = self.hexHolesSettings

        return gen, render_width
