from boxes import *
import math


class PenHolderBox(Boxes):
    """PenHolderBox: Open pen holder box with two internal grid plates."""

    ui_group = "My"

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser("x", "y", "h", "outside", "bottom_edge")

        # plate_gap et plate1_offset dans le groupe "PenHolderBox Settings" (= _action_groups[1], celui de x/y/h)
        self.argparser._action_groups[1].add_argument(
            "--plate_gap", type=float, default=80.0,
            help="Distance (mm) between Plate 1 and Plate 2.")
        self.argparser._action_groups[1].add_argument(
            "--plate1_offset", type=float, default=3.0,
            help="Distance (mm) from the top of the box to Plate 1 (default = thickness).")

        group2 = self.argparser.add_argument_group(
            "PenHolderBox Hole Plate Settings",
            description="Settings for the hole grid plates.")
        group2.add_argument(
            "--nx", type=int, default=5,
            help="Number of holes in width (X).")
        group2.add_argument(
            "--ny", type=int, default=4,
            help="Number of holes in depth (Y).")
        group2.add_argument(
            "--pen_diam", type=float, default=12.0,
            help="Diameter (mm) of the pen hole.")
        group2.add_argument(
            "--cap_diam", type=float, default=16.0,
            help="Diameter (mm) of the cap (reserved area, drawn in green).")

    def _check_grille(self, plaque_w, plaque_h):
        cd = self.cap_diam
        utile_w = plaque_w - cd
        utile_h = plaque_h - cd
        grille_w = self.nx * cd
        grille_h = self.ny * cd
        ok = True
        if grille_w > utile_w:
            print(f"WARNING: grid too wide ! {grille_w:.1f}mm > zone utile {utile_w:.1f}mm. Reduce nx or cap_diam.")
            ok = False
        if grille_h > utile_h:
            print(f"WARNING: grid too tall ! {grille_h:.1f}mm > zone utile {utile_h:.1f}mm. Reduce ny or cap_diam.")
            ok = False
        if ok:
            print(f"Grid OK: {grille_w:.1f}x{grille_h:.1f}mm within usable area {utile_w:.1f}x{utile_h:.1f}mm")
        return ok

    def _trous_plaque(self, plaque_w, plaque_h):
        r_trou = self.pen_diam / 2.0
        r_cap  = self.cap_diam / 2.0
        cd = self.cap_diam
        step = cd  # centre a centre = 1 diametre capuchon

        grille_w = (self.nx - 1) * step
        grille_h = (self.ny - 1) * step

        x0 = (plaque_w - grille_w) / 2.0
        y0 = (plaque_h - grille_h) / 2.0

        for row in range(self.ny):
            for col in range(self.nx):
                cx = x0 + col * step
                cy = y0 + row * step
                # trou de decoupe (couleur normale)
                self.hole(cx, cy, r=r_trou)
                # cercle capuchon en vert (annotation, non decoupe)
                import math as _math
                self.ctx.save()
                self.ctx.set_source_rgb(0, 0.6, 0)
                steps = 60
                for i in range(steps + 1):
                    angle = 2 * _math.pi * i / steps
                    px = cx + r_cap * _math.cos(angle)
                    py = cy + r_cap * _math.sin(angle)
                    if i == 0:
                        self.ctx.move_to(px, py)
                    else:
                        self.ctx.line_to(px, py)
                self.ctx.stroke()
                self.ctx.restore()

    def _mortaises(self, wall_width, wall_height, y_p1, y_p2):
        self.fingerHolesAt(0, y_p1, wall_width, 0)
        self.fingerHolesAt(0, y_p2, wall_width, 0)

    def render(self):
        x, y, h = self.x, self.y, self.h
        t = self.thickness
        t1, t2, t3, t4 = "eeee"
        b = self.edges.get(self.bottom_edge, self.edges["F"])
        sideedge = "F"

        if self.outside:
            self.x = x = self.adjustSize(x, sideedge, sideedge)
            self.y = y = self.adjustSize(y)
            self.h = h = self.adjustSize(h, b, t1)

        y_p1 = h - self.plate1_offset - t / 2.0
        y_p2 = y_p1 - self.plate_gap

        self._check_grille(x, y)

        with self.saved_context():
            self.rectangularWall(x, h, [b, sideedge, t1, sideedge],
                ignore_widths=[1, 6], move="up", label="front_face",
                callback=[lambda: self._mortaises(x, h, y_p1, y_p2)])
            self.rectangularWall(x, h, [b, sideedge, t3, sideedge],
                ignore_widths=[1, 6], move="up", label="back_face",
                callback=[lambda: self._mortaises(x, h, y_p1, y_p2)])
            if self.bottom_edge != "e":
                self.rectangularWall(x, y, "ffff", move="up", label="bottom")

        self.rectangularWall(x, h, [b, sideedge, t3, sideedge],
            ignore_widths=[1, 6], move="right only")

        with self.saved_context():
            self.rectangularWall(y, h, [b, "f", t2, "f"],
                ignore_widths=[1, 6], move="up", label="left_side",
                callback=[lambda: self._mortaises(y, h, y_p1, y_p2)])
            self.rectangularWall(y, h, [b, "f", t4, "f"],
                ignore_widths=[1, 6], move="up", label="right_side",
                callback=[lambda: self._mortaises(y, h, y_p1, y_p2)])

        self.rectangularWall(y, h, [b, "f", t4, "f"],
            ignore_widths=[1, 6], move="right only")

        with self.saved_context():
            self.rectangularWall(x, y, "ffff", move="up", label="plate_1",
                callback=[lambda: self._trous_plaque(x, y)])
            self.rectangularWall(x, y, "ffff", move="up", label="plate_2",
                callback=[lambda: self._trous_plaque(x, y)])


def main():
    b = PenHolderBox()
    b.parseArgs()
    b.render()


if __name__ == "__main__":
    main()
