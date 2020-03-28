import math
from affine import Affine
from boxes.extents import Extents

try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

EPS = 1e-4
PADDING = 10

RANDOMIZE_COLORS = False  # enable to ease check for continuity of pathes


def points_equal(x1, y1, x2, y2):
    return abs(x1 - x2) < EPS and abs(y1 - y2) < EPS


def pdiff(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return (x1 - x2, y1 - y2)


class Surface:
    def __init__(self, fname, width, height):
        self._fname = fname
        self.parts = []
        self._p = self.new_part("default")

    def flush(self):
        pass

    def finish(self):
        pass

    def render(self, renderer):
        renderer.init(**self.args)
        for p in self.parts:
            p.render(renderer)
        renderer.finish()

    def move_offset(self, dx, dy):
        for p in self.parts:
            p.move_offset(dx, dy)

    def new_part(self, name="part"):
        if self.parts and len(self.parts[-1].pathes) == 0:
            return self._p
        p = Part(name)
        self.parts.append(p)
        self._p = p
        return p

    def append(self, *path):
        self._p.append(*path)

    def stroke(self, **params):
        return self._p.stroke(**params)

    def move_to(self, *xy):
        self._p.move_to(*xy)

    def extents(self):
        if not self.parts:
            return Extents()
        return sum([p.extents() for p in self.parts])


class Part:
    def __init__(self, name):
        self.pathes = []
        self.path = []

    def extents(self):
        if not self.pathes:
            return Extents()
        return sum([p.extents() for p in self.pathes])

    def move_offset(self, dx, dy):
        assert(not self.path)
        for p in self.pathes:
            p.move_offset(dx, dy)

    def append(self, *path):
        self.path.append(list(path))

    def stroke(self, **params):
        if len(self.path) == 0:
            return
        # search for path ending at new start coordinates to append this path to
        xy0 = self.path[0][1:3]
        for p in reversed(self.pathes):
            if self.path[0][0] == "T":
                break
            xy1 = p.path[-1][1:3]
            if points_equal(*xy0, *xy1):
                # todo: check for same color and linewidth
                p.path.extend(self.path[1:])
                self.path = []
                return p
        p = Path(self.path, params)
        self.pathes.append(p)
        self.path = []
        return p

    def move_to(self, *xy):
        if len(self.path) == 0:
            self.path.append(["M", *xy])
        elif self.path[-1][0] == "M":
            self.path[-1] = ["M", *xy]
        else:
            xy0 = self.path[-1][1:3]
            if not points_equal(*xy0, *xy):
                self.path.append(["M", *xy])


class Path:
    def __init__(self, path, params):
        self.path = path
        self.params = params
        # self._extents = None

    def __repr__(self):
        l = len(self.path)
        # x1,y1 = self.path[0][1:3]
        x2, y2 = self.path[-1][1:3]
        return f"Path[{l}] to ({x2:.2f},{y2:.2f})"

    def extents(self):
        # if self._extents is not None: return self._extents
        e = Extents()
        for p in self.path:
            e.add(*p[1:3])
        return e

    def move_offset(self, dx, dy):
        for c in self.path:
            C = c[0]
            c[1] += dx
            c[2] += dy
            if C == 'C':
                c[3] += dx
                c[4] += dy
                c[5] += dx
                c[6] += dy

    def faster_edges(self):
        for (i, p) in enumerate(self.path):
            if p[0] == "C" and i > 1 and i < len(self.path) - 1:
                if self.path[i - 1][0] == "L" and self.path[i + 1][0] == "L":
                    p11 = self.path[i - 2][1:3]
                    p12 = self.path[i - 1][1:3]
                    p21 = p[1:3]
                    p22 = self.path[i + 1][1:3]
                    if (((p12[0]-p21[0])**2 + (p12[1]-p21[1])**2) >
                        self.params["lw"]**2):
                        continue
                    lines_intersect, x, y = line_intersection((p11, p12), (p21, p22))
                    if lines_intersect:
                        self.path[i - 1] = ("L", x, y)
                        self.path[i] = ("C", x, y, *p12, *p21)


class Context:
    def __init__(self, surface, *al, **ad):
        self._renderer = self._dwg = surface

        self._bounds = Extents()
        self._padding = PADDING

        self._stack = []
        self._m = Affine.translation(0, 0)
        self._xy = (0, 0)
        self._mxy = self._m * self._xy
        self._lw = 0
        self._rgb = (0, 0, 0)
        self._ff = "sans-serif"
        self._last_path = None

    def _update_bounds_(self, mx, my):
        self._bounds.update(mx, my)

    def save(self):
        self._stack.append(
            (self._m, self._xy, self._lw, self._rgb, self._mxy, self._last_path)
        )
        self._xy = (0, 0)

    def restore(self):
        (
            self._m,
            self._xy,
            self._lw,
            self._rgb,
            self._mxy,
            self._last_path,
        ) = self._stack.pop()

    ## transformations

    def translate(self, x, y):
        self._m *= Affine.translation(x, y)
        self._xy = (0, 0)

    def scale(self, sx, sy):
        self._m *= Affine.scale(sx, sy)

    def rotate(self, r):
        self._m *= Affine.rotation(180 * r / math.pi)

    def set_line_width(self, lw):
        self._lw = lw

    def set_source_rgb(self, r, g, b):
        self._rgb = (r, g, b)

    ## path methods

    def _line_to(self, x, y):
        self._add_move()
        x1, y1 = self._mxy
        self._xy = x, y
        x2, y2 = self._mxy = self._m * self._xy
        if not points_equal(x1, y1, x2, y2):
            self._dwg.append("L", x2, y2)

    def _add_move(self):
        self._dwg.move_to(*self._mxy)

    def move_to(self, x, y):
        self._xy = (x, y)
        self._mxy = self._m * self._xy

    def line_to(self, x, y):
        self._line_to(x, y)

    def _arc(self, xc, yc, radius, angle1, angle2, direction):
        x1, y1 = radius * math.cos(angle1) + xc, radius * math.sin(angle1) + yc
        x4, y4 = radius * math.cos(angle2) + xc, radius * math.sin(angle2) + yc

        # XXX direction seems not needed for small arcs
        ax = x1 - xc
        ay = y1 - yc
        bx = x4 - xc
        by = y4 - yc
        q1 = ax * ax + ay * ay
        q2 = q1 + ax * bx + ay * by
        k2 = 4/3 * ((2 * q1 * q2)**0.5 - q2) / (ax * by - ay * bx)

        x2 = xc + ax - k2 * ay
        y2 = yc + ay + k2 * ax
        x3 = xc + bx + k2 * by
        y3 = yc + by - k2 * bx

        mx1, my1 = self._m * (x1, y1)
        mx2, my2 = self._m * (x2, y2)
        mx3, my3 = self._m * (x3, y3)
        mx4, my4 = self._m * (x4, y4)
        mxc, myc = self._m * (xc, yc)

        self._add_move()
        self._dwg.append("C", mx4, my4, mx2, my2, mx3, my3)
        self._xy = (x4, y4)
        self._mxy = (mx4, my4)

    def arc(self, xc, yc, radius, angle1, angle2):
        self._arc(xc, yc, radius, angle1, angle2, 1)

    def arc_negative(self, xc, yc, radius, angle1, angle2):
        self._arc(xc, yc, radius, angle1, angle2, -1)

    def curve_to(self, x1, y1, x2, y2, x3, y3):
        # mx0,my0 = self._m*self._xy
        mx1, my1 = self._m * (x1, y1)
        mx2, my2 = self._m * (x2, y2)
        mx3, my3 = self._m * (x3, y3)
        self._add_move()
        self._dwg.append("C", mx3, my3, mx1, my1, mx2, my2)  # destination first!
        self._xy = (x3, y3)

    def stroke(self):
        # print('stroke stack-level=',len(self._stack),'lastpath=',self._last_path,)
        self._last_path = self._dwg.stroke(rgb=self._rgb, lw=self._lw)
        self._xy = (0, 0)

    def fill(self):
        self._xy = (0, 0)
        raise NotImplementedError()

    def select_font_face(self, ff):
        self._ff = ff

    def set_font_size(self, fs):
        self._fs = fs

    def show_text(self, text, **args):
        params = {"ff": self._ff, "fs": self._fs, "lw": self._lw, "rgb": self._rgb}
        params.update(args)
        mx0, my0 = self._m * self._xy
        self._dwg.append("T", mx0, my0, text, params)

    def text_extents(self, text):
        fs = self._fs
        # XXX ugly hack! Fix Boxes.text() !
        return (0, 0, 0.6 * fs * len(text), 0.65 * fs, fs * 0.1, 0)

    def rectangle(self, x, y, width, height):

        # todo: better check for empty path?
        self.stroke()

        self.move_to(x, y)
        self.line_to(x + width, y)
        self.line_to(x + width, y + height)
        self.line_to(x, y + height)
        self.line_to(x, y)
        self.stroke()

    def get_current_point(self):
        return self._xy

    def flush(self):
        pass
        # todo: check, if needed
        # self.stroke()

    ## additional methods
    def new_part(self):
        self._dwg.new_part()


class SVGSurface(Surface):
    def finish(self):

        extents = self.extents()

        self.move_offset(-extents.xmin + PADDING,
                         -extents.ymin + PADDING)
        w = extents.width + 2 * PADDING
        h = extents.height + 2 * PADDING


        nsmap = {
                "dc": "http://purl.org/dc/elements/1.1/",
                "cc": "http://creativecommons.org/ns#",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "svg": "http://www.w3.org/2000/svg",
                "xlink": "http://www.w3.org/1999/xlink",
                "inkscape": "http://www.inkscape.org/namespaces/inkscape",
            }
        ET.register_namespace("", "http://www.w3.org/2000/svg")
        ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
        svg = ET.Element('svg', width=f"{w:.2f}mm", height=f"{h:.2f}mm",
                         viewBox=f"0.0 0.0 {w:.2f} {h:.2f}",
                         xmlns="http://www.w3.org/2000/svg")
        for name, value in nsmap.items():
            svg.set(f"xmlns:{name}", value)
        svg.text = "\n"
        tree = ET.ElementTree(svg)
        
        for i, part in enumerate(self.parts):
            if not part.pathes:
                continue
            g = ET.SubElement(svg, "g", id=f"p-{i}",
                              style="fill:none;stroke-linecap:round;stroke-linejoin:round;")
            g.text = "\n  "
            g.tail = "\n"
            for j, path in enumerate(part.pathes):
                p = []
                x, y = 0, 0
                path.faster_edges()
                for c in path.path:
                    x0, y0 = x, y
                    C, x, y = c[0:3]
                    if C == "M":
                        p.append(f"M {x:.3f} {y:.3f}")
                    elif C == "L":
                        p.append(f"L {x:.3f} {y:.3f}")
                    elif C == "C":
                        x1, y1, x2, y2 = c[3:]
                        p.append(
                            f"C {x1:.3f} {y1:.3f} {x2:.3f} {y2:.3f} {x:.3f} {y:.3f}"
                        )
                    elif C == "T":
                        text, params = c[3:]
                        style = f"font: {params['ff']}  ; fill: {rgb_to_svg_color(*params['rgb'])}"
                        t = ET.SubElement(g, "text",
                                          x=f"{x:.3f}", y=f"{y:.3f}",
                                          style=style)
                        t.text = text
                        t.set("font-size", f"{params['fs']}px")
                    else:
                        print("Unknown", c)
                color = (
                    random_svg_color()
                    if RANDOMIZE_COLORS
                    else rgb_to_svg_color(*path.params["rgb"])
                )
                if p:  # might be empty if only contains text
                    t = ET.SubElement(g, "path", d=" ".join(p), stroke=color)
                    t.set("stroke-width", f'{path.params["lw"]:.2f}')
                    t.tail = "\n  "
            t.tail = "\n"
        tree.write(open(self._fname, "wb"), xml_declaration=True, method="xml")

class PSSurface(Surface):

    def finish(self):

        extents = self.extents()

        self.move_offset(-extents.xmin + PADDING,
                         -extents.ymin + PADDING)

        w = extents.width + 2 * PADDING
        h = extents.height + 2 * PADDING

        f = open(self._fname, "w")

        f.write("%!PS-Adobe-2.0\n")
        f.write(
            f"%%BoundingBox: 0 0 {w:.0f} {h:.0f}\n\n"
        )
        # f.write(f"%%DocumentMedia: \d+x\d+mm ((\d+) (\d+)) 0 \("
        # dwg['width']=f'{w:.2f}mm'
        # dwg['height']=f'{h:.2f}mm'

        for i, part in enumerate(self.parts):
            if not part.pathes:
                continue
            # g = dwg.add( dwg.g(id=f'p-{i}',style='fill:none;stroke-linecap:round;stroke-linejoin:round;') )
            for j, path in enumerate(part.pathes):
                p = []
                x, y = 0, 0
                path.faster_edges()

                for c in path.path:
                    x0, y0 = x, y
                    C, x, y = c[0:3]
                    if C == "M":
                        p.append(f"{x:.3f} {y:.3f} moveto")
                    elif C == "L":
                        p.append(f"{x:.3f} {y:.3f} lineto")
                    elif C == "C":
                        x1, y1, x2, y2 = c[3:]
                        p.append(
                            f"{x1:.3f} {y1:.3f} {x2:.3f} {y2:.3f} {x:.3f} {y:.3f} curveto"
                        )
                    elif C == "T":
                        text, params = c[3:]
                        text = text.replace("(", "r\(").replace(")", r"\)")
                        color = " ".join((f"{c:.2f}"
                                          for c in params["rgb"]))
                        f.write(f"/{params['ff']} findfont\n")
                        f.write(f"{params['fs']*72 / 25.4} scalefont\n")
                        f.write("setfont\n")
                        f.write(f"{color} setrgbcolor\n")
                        f.write(f"{x:.3f} {y:.3f} moveto\n")
                        f.write(f"({text}) show\n\n")
                    else:
                        print("Unknown", c)
                color = (
                    random_svg_color()
                    if RANDOMIZE_COLORS
                    else rgb_to_svg_color(*path.params["rgb"])
                )
                if p:  # todo: might be empty since text is not implemented yet
                    color = " ".join((f"{c:.2f}"
                                      for c in path.params["rgb"]))
                    f.write("newpath\n")
                    f.write("\n".join(p))
                    f.write("\n")
                    f.write(f"{path.params['lw']} setlinewidth\n")
                    f.write(f"{color} setrgbcolor\n")
                    f.write("stroke\n\n")
        f.write(
            """
showpage
%%Trailer
%%EOF
"""
        )
        f.close()


from random import random


def random_svg_color():
    r, g, b = random(), random(), random()
    return f"rgb({r*255:.0f},{g*255:.0f},{b*255:.0f})"


def rgb_to_svg_color(r, g, b):
    return f"rgb({r*255:.0f},{g*255:.0f},{b*255:.0f})"


def line_intersection(line1, line2):

    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        # todo: deal with paralel line intersection / overlay
        return False, None, None

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div

    on_segments = (
        (x + EPS >= min(line1[0][0], line1[1][0])),
        (x + EPS >= min(line2[0][0], line2[1][0])),
        (x - EPS <= max(line1[0][0], line1[1][0])),
        (x - EPS <= max(line2[0][0], line2[1][0])),
        (y + EPS >= min(line1[0][1], line1[1][1])),
        (y + EPS >= min(line2[0][1], line2[1][1])),
        (y - EPS <= max(line1[0][1], line1[1][1])),
        (y - EPS <= max(line2[0][1], line2[1][1])),
    )

    return min(on_segments), x, y
