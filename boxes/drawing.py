from __future__ import annotations

import codecs
import io
import math
from typing import Any
from xml.etree import ElementTree as ET

from affine import Affine

from boxes.extents import Extents
from boxes.dogbone import apply_dogbone

EPS = 1e-4


def normalize_arc_angles(start_angle: float, end_angle: float, orientation: int) -> tuple[float, float]:
    if orientation > 0:
        while end_angle <= start_angle + EPS:
            end_angle += 2 * math.pi
    else:
        while end_angle >= start_angle - EPS:
            end_angle -= 2 * math.pi
    return start_angle, end_angle


def arc_to_cubic_segments(cx: float, cy: float, radius: float, start_angle: float, end_angle: float) -> list[list[float]]:
    delta = end_angle - start_angle
    if abs(delta) < 1e-12:
        return []
    segments = max(1, int(math.ceil(abs(delta) / (math.pi / 2.0))))
    result: list[list[float]] = []
    for seg_idx in range(segments):
        t0 = start_angle + delta * (seg_idx / segments)
        t1 = start_angle + delta * ((seg_idx + 1) / segments)
        k = 4.0 / 3.0 * math.tan((t1 - t0) / 4.0)

        cos0, sin0 = math.cos(t0), math.sin(t0)
        cos1, sin1 = math.cos(t1), math.sin(t1)

        p0x = cx + radius * cos0
        p0y = cy + radius * sin0
        p3x = cx + radius * cos1
        p3y = cy + radius * sin1

        c1x = p0x - k * radius * sin0
        c1y = p0y + k * radius * cos0
        c2x = p3x + k * radius * sin1
        c2y = p3y - k * radius * cos1

        result.append(['C', p3x, p3y, c1x, c1y, c2x, c2y])
    return result


def angle_on_arc(angle: float, start: float, end: float, orientation: int) -> float | None:
    full_turn = 2 * math.pi
    if orientation > 0:
        k = math.ceil((start - angle) / full_turn)
        candidate = angle + full_turn * k
        if start - EPS <= candidate <= end + EPS:
            return candidate
    else:
        k = math.floor((start - angle) / full_turn)
        candidate = angle + full_turn * k
        if end - EPS <= candidate <= start + EPS:
            return candidate
    return None


def expand_path_arcs(commands):
    expanded = []
    current = None
    for cmd in commands:
        letter = cmd[0]
        if letter == 'A':
            _, ex, ey, cx, cy, radius, start_angle, end_angle, orientation = cmd
            segments = arc_to_cubic_segments(cx, cy, radius, start_angle, end_angle)
            for seg in segments:
                expanded.append(seg)
            current = (ex, ey)
        else:
            expanded.append(cmd)
            if letter != 'T':
                current = (cmd[1], cmd[2])
    return expanded
PADDING = 10

RANDOMIZE_COLORS = False  # enable to ease check for continuity of paths


def reorder_attributes(root) -> None:
    """
    Source: https://docs.python.org/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.Element.remove
    """
    for el in root.iter():
        attrib = el.attrib
        if len(attrib) > 1:
            # adjust attribute order, e.g. by sorting
            attribs = sorted(attrib.items())
            attrib.clear()
            attrib.update(attribs)


def points_equal(x1, y1, x2, y2):
    return abs(x1 - x2) < EPS and abs(y1 - y2) < EPS


def pdiff(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return (x1 - x2, y1 - y2)


class Surface:

    scale = 1.0
    invert_y = False

    def __init__(self) -> None:
        self.parts: list[Any] = []
        self._p = self.new_part("default")
        self.count = 0

    def set_metadata(self, metadata):
        self.metadata = metadata

    def flush(self):
        pass

    def finish(self):
        pass

    def _adjust_coordinates(self):
        extents = self.extents()
        extents.xmin -= PADDING
        extents.ymin -= PADDING
        extents.xmax += PADDING
        extents.ymax += PADDING

        m = Affine.translation(-extents.xmin, -extents.ymin)
        if self.invert_y:
            m = Affine.scale(self.scale, -self.scale) * m
            m = Affine.translation(0, self.scale*extents.height) * m
        else:
            m = Affine.scale(self.scale, self.scale) * m

        self.transform(self.scale, m, self.invert_y)

        return Extents(0, 0, extents.width * self.scale, extents.height * self.scale)

    def prepare_paths(self, inner_corners, dogbone_radius=None):
        for part in self.parts:
            for path in part.pathes:
                path.faster_edges(inner_corners, dogbone_radius)
        return self._adjust_coordinates()

    def render(self, renderer):
        renderer.init(**self.args)
        for p in self.parts:
            p.render(renderer)
        renderer.finish()

    def transform(self, f, m, invert_y=False):
        for p in self.parts:
            p.transform(f, m, invert_y)

    def new_part(self, name="part"):
        if self.parts and len(self.parts[-1].pathes) == 0:
            return self._p
        p = Part(name)
        self.parts.append(p)
        self._p = p
        return p

    def append(self, *path):
        self.count += 1
        if self.count > 100000:
            raise ValueError("Too many lines")
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
    def __init__(self, name) -> None:
        self.pathes: list[Any] = []
        self.path: list[Any] = []

    def extents(self):
        if not self.pathes:
            return Extents()
        return sum([p.extents() for p in self.pathes])

    def transform(self, f, m, invert_y=False):
        assert(not self.path)
        for p in self.pathes:
            p.transform(f, m, invert_y)

    def append(self, *path):
        self.path.append(list(path))

    def stroke(self, **params):
        if len(self.path) == 0:
            return
        # search for path ending at new start coordinates to append this path to
        xy0 = self.path[0][1:3]
        if (not points_equal(*xy0, *self.path[-1][1:3]) and
            not self.path[0][0] == "T"):
            for p in reversed(self.pathes):
                xy1 = p.path[-1][1:3]
                if points_equal(*xy0, *xy1) and p.params == params:
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
    def __init__(self, path, params) -> None:
        self.path = path
        self.params = params

    def __repr__(self) -> str:
        l = len(self.path)
        # x1,y1 = self.path[0][1:3]
        if l>0:
            x2, y2 = self.path[-1][1:3]
            return f"Path[{l}] to ({x2:.2f},{y2:.2f})"
        return f"empty Path"

    def extents(self):
        e = Extents()
        for p in self.path:
            e.add(*p[1:3])
            if p[0] == 'T':
                m, text, params = p[3:]
                h = params['fs']
                l = len(text) * h * 0.7
                align = params.get('align', 'left')
                start, end = {
                    'left' : (0, 1),
                    'middle' : (-0.5, 0.5),
                    'end' : (-1, 0),
                    }[align]
                for x in (start*l, end*l):
                    for y in (0, h):
                        x_, y_ = m * (x, y)
                        e.add(x_, y_)
            elif p[0] == 'A':
                _, _, _, cx, cy, radius, ang_start, ang_end, orientation = p
                radius = abs(radius)
                angles = {ang_start, ang_end}
                for base in (0.0, math.pi / 2.0, math.pi, 3.0 * math.pi / 2.0):
                    candidate = angle_on_arc(base, ang_start, ang_end, orientation)
                    if candidate is not None:
                        angles.add(candidate)
                for angle in angles:
                    px = cx + radius * math.cos(angle)
                    py = cy + radius * math.sin(angle)
                    e.add(px, py)
        return e

    def transform(self, f, m, invert_y=False):
        self.params["lw"] *= f
        current = None
        for idx, c in enumerate(self.path):
            if isinstance(c, tuple):
                c = list(c)
                self.path[idx] = c
            C = c[0]
            if C == "M":
                c[1], c[2] = m * (c[1], c[2])
                current = (c[1], c[2])
                continue
            c[1], c[2] = m * (c[1], c[2])
            if C == 'L':
                current = (c[1], c[2])
            elif C == 'C':
                c[3], c[4] = m * (c[3], c[4])
                c[5], c[6] = m * (c[5], c[6])
                current = (c[1], c[2])
            elif C == 'A':
                cx0, cy0 = c[3], c[4]
                r0 = c[5]
                start0 = c[6]
                end0 = c[7]
                orient0 = c[8]
                c[3], c[4] = m * (cx0, cy0)
                c[5] = abs(r0) * f
                cx, cy = c[3], c[4]
                radius = c[5]
                if current is None:
                    sx0 = cx0 + abs(r0) * math.cos(start0)
                    sy0 = cy0 + abs(r0) * math.sin(start0)
                    current = m * (sx0, sy0)
                start_vec = (current[0] - cx, current[1] - cy)
                end_vec = (c[1] - cx, c[2] - cy)
                start_angle = math.atan2(start_vec[1], start_vec[0])
                end_angle = math.atan2(end_vec[1], end_vec[0])
                cross = start_vec[0] * end_vec[1] - start_vec[1] * end_vec[0]
                if abs(cross) < EPS:
                    orientation = 1 if orient0 >= 0 else -1
                else:
                    orientation = 1 if cross > 0 else -1
                start_angle, end_angle = normalize_arc_angles(start_angle, end_angle, orientation)
                c[6], c[7], c[8] = start_angle, end_angle, orientation
                current = (c[1], c[2])
            elif C == "T":
                c[3] = m * c[3]
                if invert_y:
                    c[3] *= Affine.scale(1, -1)
            else:
                current = (c[1], c[2])

    def faster_edges(self, inner_corners, dogbone_radius=None):
        if inner_corners == "backarc":
            return

        if inner_corners == "dogbone":
            if not apply_dogbone(self.path, dogbone_radius, EPS, line_intersection):
                return

        else:
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
                            if inner_corners == "loop":
                                self.path[i] = ("C", x, y, *p12, *p21)
                            else:
                                self.path[i] =  ("L", x, y)
        # filter duplicates
        if len(self.path) > 1: # no need to find duplicates if only one element in path
            self.path = [p for n, p in enumerate(self.path) if p != self.path[n-1]]

class Context:
    def __init__(self, surface, *al, **ad) -> None:
        self._renderer = self._dwg = surface

        self._bounds = Extents()
        self._padding = PADDING

        self._stack: list[Any] = []
        self._m = Affine.translation(0, 0)
        self._xy = (0, 0)
        self._mxy = self._m * self._xy
        self._lw = 0
        self._rgb = (0, 0, 0)
        self._ff = "sans-serif"
        self._fs = 10
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
        if abs(angle1 - angle2) < EPS or radius < EPS:
            return
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
        self._mxy = (mx3, my3)

    def stroke(self):
        # print('stroke stack-level=',len(self._stack),'lastpath=',self._last_path,)
        self._last_path = self._dwg.stroke(rgb=self._rgb, lw=self._lw)
        self._xy = (0, 0)

    def fill(self):
        self._xy = (0, 0)
        raise NotImplementedError()

    def set_font(self, style, bold=False, italic=False):
        if style not in ("serif", "sans-serif", "monospaced"):
            raise ValueError("Unknown font style")
        self._ff = (style, bold, italic)

    def set_font_size(self, fs):
        self._fs = fs

    def show_text(self, text, **args):
        params = {"ff": self._ff, "fs": self._fs, "lw": self._lw, "rgb": self._rgb}
        params.update(args)
        mx0, my0 = self._m * self._xy
        m = self._m
        self._dwg.append("T", mx0, my0, m, text, params)

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

    invert_y = True

    fonts = {
        'serif' : 'TimesNewRoman, "Times New Roman", Times, Baskerville, Georgia, serif',
        'sans-serif' : '"Helvetica Neue", Helvetica, Arial, sans-serif',
        'monospaced' : '"Courier New", Courier, "Lucida Sans Typewriter"'
    }

    def _addTag(self, parent, tag, text, first=False):
        if first:
            t = ET.Element(tag)
        else:
            t = ET.SubElement(parent, tag)
        t.text = text
        t.tail = '\n'
        if first:
            parent.insert(0, t)
        return t

    def _add_metadata(self, root) -> None:
        md = self.metadata

        title = "{group} - {name}".format(**md)
        creation_date: str = md["creation_date"].strftime("%Y-%m-%d %H:%M:%S")

        # Add Inkscape style rdf meta data
        root.set("xmlns:dc", "http://purl.org/dc/elements/1.1/")
        root.set("xmlns:cc", "http://creativecommons.org/ns#")
        root.set("xmlns:rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")

        m = self._addTag(root, "metadata", '\n', True)
        r = ET.SubElement(m, 'rdf:RDF')
        w = ET.SubElement(r, 'cc:Work')
        w.text = '\n'

        self._addTag(w, 'dc:title', title)
        if not md["reproducible"]:
            self._addTag(w, 'dc:date', creation_date)

        if "url" in md and md["url"]:
            self._addTag(w, 'dc:source', md["url"])
            self._addTag(w, 'dc:source', md["url_short"])
        else:
            self._addTag(w, 'dc:source', md["cli"])

        desc = md["short_description"] or ""
        if "description" in md and md["description"]:
            desc += "\n\n" + md["description"]
        desc += "\n\nCreated with Boxes.py (https://boxes.hackerspace-bamberg.de/)\n"
        desc += "Command line: %s\n" % md["cli"]
        desc += "Command line short: %s\n" % md["cli_short"]
        if md["url"]:
            desc += "Url: %s\n" % md["url"]
            desc += "Url short: %s\n" % md["url_short"]
            desc += "SettingsUrl: %s\n" % md["url"].replace("&render=1", "")
            desc += "SettingsUrl short: %s\n" % md["url_short"].replace("&render=1", "")
        self._addTag(w, 'dc:description', desc)

        # title
        self._addTag(root, "title", md["name"], True)

        # Add XML comment
        txt = """\n{name} - {short_description}\n""".format(**md)
        if md["description"]:
            txt += """\n\n{description}\n\n""".format(**md)
        txt += """\nCreated with Boxes.py (https://boxes.hackerspace-bamberg.de/)\n"""
        if not md["reproducible"]:
            txt += f"""Creation date: {creation_date}\n"""

        txt += "Command line (remove spaces between dashes): %s\n" % md["cli_short"]

        if md["url"]:
            txt += "Url: %s\n" % md["url"]
            txt += "Url short: %s\n" % md["url_short"]
            txt += "SettingsUrl: %s\n" % md["url"].replace("&render=1", "")
            txt += "SettingsUrl short: %s\n" % md["url_short"].replace("&render=1", "")
        m = ET.Comment(txt.replace("--", "- -").replace("--", "- -")) # ----
        m.tail = '\n'
        root.insert(0, m)

    def finish(self, inner_corners="loop", dogbone_radius=None):
        extents = self.prepare_paths(inner_corners, dogbone_radius)
        w = extents.width * self.scale
        h = extents.height * self.scale


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

        self._add_metadata(svg)

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
                start = None
                last = None
                commands = expand_path_arcs(path.path)
                for c in commands:
                    x0, y0 = x, y
                    C, x, y = c[0:3]
                    if C == "M":
                        if start and points_equal(start[1], start[2],
                                                  last[1], last[2]):
                            p.append("Z")
                        start = c
                        p.append(f"M {x:.3f} {y:.3f}")
                    elif C == "L":
                        if abs(x - x0) < EPS:
                            p.append(f"V {y:.3f}")
                        elif abs(y - y0) < EPS:
                            p.append(f"H {x:.3f}")
                        else:
                            p.append(f"L {x:.3f} {y:.3f}")
                    elif C == "C":
                        x1, y1, x2, y2 = c[3:]
                        p.append(
                            f"C {x1:.3f} {y1:.3f} {x2:.3f} {y2:.3f} {x:.3f} {y:.3f}"
                        )
                    elif C == "T":
                        m, text, params = c[3:]
                        m = m * Affine.translation(0, -params['fs'])
                        tm = " ".join(f"{m[i]:.3f}" for i in (0, 3, 1, 4, 2, 5))
                        font, bold, italic = params['ff']
                        fontweight = ("normal", "bold")[bool(bold)]
                        fontstyle = ("normal", "italic")[bool(italic)]

                        style = f"font-family: {font} ; font-weight: {fontweight}; font-style: {fontstyle}; fill: {rgb_to_svg_color(*params['rgb'])}"
                        t = ET.SubElement(g, "text",
                                          #x=f"{x:.3f}", y=f"{y:.3f}",
                                          transform=f"matrix( {tm} )",
                                          style=style)
                        t.text = text
                        t.set("font-size", f"{params['fs']}px")
                        t.set("text-anchor", params.get('align', 'left'))
                        t.set("dominant-baseline", 'hanging')
                    else:
                        print("Unknown", c)

                    last = c

                if start and start is not last and \
                   points_equal(start[1], start[2], last[1], last[2]):
                    p.append("Z")
                color = (
                    random_svg_color()
                    if RANDOMIZE_COLORS
                    else rgb_to_svg_color(*path.params["rgb"])
                )
                if p and p[-1][0] == "M":
                    p.pop()
                if p:  # might be empty if only contains text
                    t = ET.SubElement(g, "path", d=" ".join(p), stroke=color)
                    t.set("stroke-width", f'{path.params["lw"]:.2f}')
                    t.tail = "\n  "
            t.tail = "\n"
        reorder_attributes(tree)
        f = io.BytesIO()
        tree.write(f, encoding="utf-8", xml_declaration=True, method="xml")
        f.seek(0)
        return f

class PSSurface(Surface):

    scale = 72 / 25.4 # 72 dpi

    fonts = {
        ('serif', False, False) : 'Times-Roman',
        ('serif', False, True) : 'Times-Italic',
        ('serif', True, False) : 'Times-Bold',
        ('serif', True, True) : 'Times-BoldItalic',
        ('sans-serif', False, False) : 'Helvetica',
        ('sans-serif', False, True) : 'Helvetica-Oblique',
        ('sans-serif', True, False) : 'Helvetica-Bold',
        ('sans-serif', True, True) : 'Helvetica-BoldOblique',
        ('monospaced', False, False) : 'Courier',
        ('monospaced', False, True) : 'Courier-Oblique',
        ('monospaced', True, False) : 'Courier-Bold',
        ('monospaced', True, True) : 'Courier-BoldOblique',
        }

    def _metadata(self) -> str:
        md = self.metadata

        desc = ""
        desc += "%%Title: Boxes.py - {group} - {name}\n".format(**md)
        if not md["reproducible"]:
            desc += f'%%CreationDate: {md["creation_date"].strftime("%Y-%m-%d %H:%M:%S")}\n'
        desc += f'%%Keywords: boxes.py, laser, laser cutter\n'
        desc += f'%%Creator: {md.get("url") or md["cli"]}\n'
        desc += "%%CreatedBy: Boxes.py (https://boxes.hackerspace-bamberg.de/)\n"
        for line in (md["short_description"] or "").split("\n"):
            desc += "%% %s\n" % line
        desc += "%\n"
        if "description" in md and md["description"]:
            desc += "%\n"
            for line in md["description"].split("\n"):
                desc += "%% %s\n" % line
            desc += "%\n"

        desc += "%% Command line: %s\n" % md["cli"]
        desc += "%% Command line short: %s\n" % md["cli_short"]
        if md["url"]:
            desc += f'%%Url: {md["url"]}\n'
            desc += f'%%Url short: {md["url_short"]}\n'
            desc += f'%%SettingsUrl: {md["url"].replace("&render=1", "")}\n'
            desc += f'%%SettingsUrl short: {md["url_short"].replace("&render=1", "")}\n'
        return desc

    def finish(self, inner_corners="loop", dogbone_radius=None):

        extents = self.prepare_paths(inner_corners, dogbone_radius)
        w = extents.width
        h = extents.height

        data = io.BytesIO()
        f = codecs.getwriter('utf-8')(data)

        f.write(f"""%!PS-Adobe-2.0 EPSF-2.0
%%BoundingBox: 0 0 {w:.0f} {h:.0f}
{self._metadata()}
%%EndComments

1 setlinecap
1 setlinejoin
0.0 0.0 0.0 setrgbcolor
""")
        f.write("""
/ReEncode { % inFont outFont encoding | -
   /MyEncoding exch def
   exch findfont
   dup length dict
   begin
      {def} forall
      /Encoding MyEncoding def
      currentdict
   end
   definefont
} def

""")
        for font in self.fonts.values():
            f.write(f"/{font} /{font}-Latin1 ISOLatin1Encoding ReEncode\n")
        # f.write(f"%%DocumentMedia: \d+x\d+mm ((\d+) (\d+)) 0 \("
        # dwg['width']=f'{w:.2f}mm'
        # dwg['height']=f'{h:.2f}mm'

        for i, part in enumerate(self.parts):
            if not part.pathes:
                continue
            for j, path in enumerate(part.pathes):
                p = []
                x, y = 0, 0
                commands = path.path

                for c in commands:
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
                    elif C == "A":
                        cx, cy, radius, start_angle, end_angle, orientation = c[3], c[4], c[5], c[6], c[7], c[8]
                        start_deg = math.degrees(start_angle)
                        end_deg = math.degrees(end_angle)
                        cmd = "arc" if orientation > 0 else "arcn"
                        p.append(
                            f"{cx:.3f} {cy:.3f} {radius:.3f} {start_deg:.6f} {end_deg:.6f} {cmd}"
                        )
                    elif C == "T":
                        m, text, params = c[3:]
                        tm = " ".join(f"{m[i]:.3f}" for i in (0, 3, 1, 4, 2, 5))
                        text = text.replace("(", r"\(").replace(")", r"\)")
                        color = " ".join(f"{c:.2f}" for c in params["rgb"])
                        align = params.get('align', 'left')
                        f.write(f"/{self.fonts[params['ff']]}-Latin1 findfont\n")
                        f.write(f"{params['fs']} scalefont\n")
                        f.write("setfont\n")
                        #f.write(f"currentfont /Encoding  ISOLatin1Encoding put\n")
                        f.write(f"{color} setrgbcolor\n")
                        f.write("matrix currentmatrix") # save current matrix
                        f.write(f"[ {tm} ] concat\n")
                        if align == "left":
                            f.write(f"0.0\n")
                        else:
                            f.write(f"({text}) stringwidth pop ")
                            if align == "middle":
                                f.write(f"-0.5 mul\n")
                            else: # end
                                f.write(f"neg\n")
                        # offset y by descender
                        f.write("currentfont dup /FontBBox get 1 get \n")
                        f.write("exch /FontMatrix get 3 get mul neg moveto \n")

                        f.write(f"({text}) show\n") # text created by dup above
                        f.write("setmatrix\n\n") # restore matrix
                    else:
                        print("Unknown", c)
                color = (
                    random_svg_color()
                    if RANDOMIZE_COLORS
                    else rgb_to_svg_color(*path.params["rgb"])
                )
                if p:  # todo: might be empty since text is not implemented yet
                    color = " ".join(f"{c:.2f}" for c in path.params["rgb"])
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
        data.seek(0)
        return data

class DXFSurface(Surface):

    scale = 1.0
    invert_y = False

    def finish(self, inner_corners="loop", dogbone_radius=None):
        extents = self.prepare_paths(inner_corners, dogbone_radius)
        entities: list[str] = []
        for part in self.parts:
            if not part.pathes:
                continue
            for path in part.pathes:
                entities.extend(self._entities_from_path(path.path))

        return self._build_dxf(extents, entities)

    @staticmethod
    def _pair(container: list[str], code: int, value: Any) -> None:
        container.append(f"{code:>3}")
        container.append(str(value))

    @staticmethod
    def _format_angle(angle_deg: float) -> float:
        angle = angle_deg % 360.0
        if math.isclose(angle, 360.0, abs_tol=1e-9):
            angle = 0.0
        return angle

    def _entities_from_path(self, commands):
        entities: list[str] = []
        current: tuple[float, float] | None = None
        for cmd in commands:
            letter = cmd[0]
            if letter == "M":
                current = (cmd[1], cmd[2])
            elif letter == "L":
                target = (cmd[1], cmd[2])
                if current and not points_equal(current[0], current[1], target[0], target[1]):
                    entities.extend(self._line_entity(current, target))
                current = target
            elif letter == "C":
                if current is None:
                    current = (cmd[1], cmd[2])
                    continue
                control1 = (cmd[3], cmd[4])
                control2 = (cmd[5], cmd[6])
                end_point = (cmd[1], cmd[2])
                prev = current
                for point in self._approximate_cubic(current, control1, control2, end_point):
                    if not points_equal(prev[0], prev[1], point[0], point[1]):
                        entities.extend(self._line_entity(prev, point))
                    prev = point
                current = end_point
            elif letter == "A":
                if current is None:
                    current = (cmd[1], cmd[2])
                end_point = (cmd[1], cmd[2])
                center = (cmd[3], cmd[4])
                radius = cmd[5]
                start_angle = math.degrees(cmd[6])
                end_angle = math.degrees(cmd[7])
                orientation = cmd[8]
                if radius > EPS:
                    if orientation < 0:
                        start_angle, end_angle = end_angle, start_angle
                    start_angle = self._format_angle(start_angle)
                    end_angle = self._format_angle(end_angle)
                    entities.extend(self._arc_entity(center, radius, start_angle, end_angle))
                current = end_point
            elif letter == "T":
                text_entities = self._text_entity(cmd)
                if text_entities:
                    entities.extend(text_entities)
        return entities

    def _line_entity(self, start, end):
        if points_equal(start[0], start[1], end[0], end[1]):
            return []
        items: list[str] = []
        self._pair(items, 0, "LINE")
        self._pair(items, 8, "0")
        self._pair(items, 10, f"{start[0]:.6f}")
        self._pair(items, 20, f"{start[1]:.6f}")
        self._pair(items, 30, "0.0")
        self._pair(items, 11, f"{end[0]:.6f}")
        self._pair(items, 21, f"{end[1]:.6f}")
        self._pair(items, 31, "0.0")
        return items

    def _arc_entity(self, center, radius, start_angle, end_angle):
        items: list[str] = []
        self._pair(items, 0, "ARC")
        self._pair(items, 8, "0")
        self._pair(items, 10, f"{center[0]:.6f}")
        self._pair(items, 20, f"{center[1]:.6f}")
        self._pair(items, 30, "0.0")
        self._pair(items, 40, f"{abs(radius):.6f}")
        self._pair(items, 50, f"{start_angle:.6f}")
        self._pair(items, 51, f"{end_angle:.6f}")
        return items

    def _text_entity(self, cmd):
        _, x, y, _m, text, params = cmd
        if not text:
            return []
        height = params.get("fs", 10.0)
        items: list[str] = []
        self._pair(items, 0, "TEXT")
        self._pair(items, 8, "0")
        self._pair(items, 10, f"{x:.6f}")
        self._pair(items, 20, f"{y:.6f}")
        self._pair(items, 30, "0.0")
        self._pair(items, 40, f"{height:.6f}")
        self._pair(items, 1, text)
        return items

    def _approximate_cubic(self, p0, p1, p2, p3, steps=12):
        result: list[tuple[float, float]] = []
        for step in range(1, steps + 1):
            t = step / steps
            mt = 1.0 - t
            x = (
                mt * mt * mt * p0[0]
                + 3 * mt * mt * t * p1[0]
                + 3 * mt * t * t * p2[0]
                + t * t * t * p3[0]
            )
            y = (
                mt * mt * mt * p0[1]
                + 3 * mt * mt * t * p1[1]
                + 3 * mt * t * t * p2[1]
                + t * t * t * p3[1]
            )
            result.append((x, y))
        return result

    def _build_dxf(self, extents, entities):
        lines: list[str] = []
        add = lambda code, value: self._pair(lines, code, value)

        add(0, "SECTION")
        add(2, "HEADER")
        add(9, "$ACADVER")
        add(1, "AC1009")
        add(9, "$INSUNITS")
        add(70, 4)
        add(9, "$MEASUREMENT")
        add(70, 1)
        add(9, "$EXTMIN")
        add(10, f"{extents.xmin:.6f}")
        add(20, f"{extents.ymin:.6f}")
        add(30, "0.0")
        add(9, "$EXTMAX")
        add(10, f"{extents.xmax:.6f}")
        add(20, f"{extents.ymax:.6f}")
        add(30, "0.0")
        add(0, "ENDSEC")

        add(0, "SECTION")
        add(2, "TABLES")
        add(0, "TABLE")
        add(2, "LAYER")
        add(70, 1)
        add(0, "LAYER")
        add(2, "0")
        add(70, 0)
        add(62, 7)
        add(6, "CONTINUOUS")
        add(0, "ENDTAB")
        add(0, "ENDSEC")

        add(0, "SECTION")
        add(2, "ENTITIES")
        lines.extend(entities)
        add(0, "ENDSEC")

        add(0, "SECTION")
        add(2, "BLOCKS")
        add(0, "ENDSEC")

        add(0, "SECTION")
        add(2, "OBJECTS")
        add(0, "ENDSEC")
        add(0, "EOF")
        data = ("\r\n".join(lines) + "\r\n").encode("ascii", "ignore")
        buffer = io.BytesIO(data)
        buffer.seek(0)
        return buffer

class LBRN2Surface(Surface):


    invert_y = False
    dbg = False

    fonts = {
        'serif' : 'Times New Roman',
        'sans-serif' : 'Arial',
        'monospaced' : 'Courier New'
    }

    lbrn2_colors=[
        0,  # Colors.OUTER_CUT    (BLACK)   --> Lightburn C00 (black)
        1,  # Colors.INNER_CUT    (BLUE)    --> Lightburn C01 (blue)
        3,  # Colors.ETCHING      (GREEN)   --> Lightburn C02 (green)
        6,  # Colors.ETCHING_DEEP (CYAN)    --> Lightburn C06 (cyan)
        30, # Colors.ANNOTATIONS  (RED)     --> Lightburn T1
        7,  # Colors.OUTER_CUT    (MAGENTA) --> Lightburn C07 (magenta)
        4,  # Colors.OUTER_CUT    (YELLOW)  --> Lightburn C04 (yellow)
        8,  # Colors.OUTER_CUT    (WHITE)   --> Lightburn C08 (grey)
        ]

    def finish(self, inner_corners="loop", dogbone_radius=None):
        if self.dbg: print("LBRN2 save")
        extents = self.prepare_paths(inner_corners, dogbone_radius)
        w = extents.width * self.scale
        h = extents.height * self.scale

        svg = ET.Element('LightBurnProject', AppVersion="1.0.06", FormatVersion="1", MaterialHeight="0", MirrorX="False", MirrorY="False")
        svg.text = "\n"
        num = 0
        txtOffset = {}

        tree = ET.ElementTree(svg)
        if self.dbg: print ("8", num)

        cs = ET.SubElement(svg, "CutSetting", Type="Cut")
        index    = ET.SubElement(cs, "index",    Value="3")         # green layer (ETCHING)
        name     = ET.SubElement(cs, "name",     Value="Etch")
        priority = ET.SubElement(cs, "priority", Value="0")         # is cut first

        cs = ET.SubElement(svg, "CutSetting", Type="Cut")
        index    = ET.SubElement(cs, "index",    Value="6")         # cyan layer (ETCHING_DEEP)
        name     = ET.SubElement(cs, "name",     Value="Deep Etch")
        priority = ET.SubElement(cs, "priority", Value="1")         # is cut second

        cs = ET.SubElement(svg, "CutSetting", Type="Cut")
        index    = ET.SubElement(cs, "index",    Value="7")         # magenta layer (MAGENTA)
        name     = ET.SubElement(cs, "name",     Value="C07")
        priority = ET.SubElement(cs, "priority", Value="2")         # is cut third

        cs = ET.SubElement(svg, "CutSetting", Type="Cut")
        index    = ET.SubElement(cs, "index",    Value="4")         # yellow layer (YELLOW)
        name     = ET.SubElement(cs, "name",     Value="C04")
        priority = ET.SubElement(cs, "priority", Value="3")         # is cut third

        cs = ET.SubElement(svg, "CutSetting", Type="Cut")
        index    = ET.SubElement(cs, "index",    Value="8")         # grey layer (WHITE)
        name     = ET.SubElement(cs, "name",     Value="C08")
        priority = ET.SubElement(cs, "priority", Value="4")         # is cut fourth

        cs = ET.SubElement(svg, "CutSetting", Type="Cut")
        index    = ET.SubElement(cs, "index",    Value="1")         # blue layer (INNER_CUT)
        name     = ET.SubElement(cs, "name",     Value="Inner Cut")
        priority = ET.SubElement(cs, "priority", Value="5")         # is cut fifth

        cs = ET.SubElement(svg, "CutSetting", Type="Cut")
        index    = ET.SubElement(cs, "index",    Value="0")         # black layer (OUTER_CUT)
        name     = ET.SubElement(cs, "name",     Value="Outer Cut")
        priority = ET.SubElement(cs, "priority", Value="6")         # is cut sixth

        cs = ET.SubElement(svg, "CutSetting", Type="Tool")
        index    = ET.SubElement(cs, "index",    Value="30")        # T1 layer (ANNOTATIONS)
        name     = ET.SubElement(cs, "name",     Value="T1")        # tool layer do not support names
        priority = ET.SubElement(cs, "priority", Value="7")         # is not cut at all

        for i, part in enumerate(self.parts):
            if self.dbg: print ("7", num)
            if not part.pathes:
                continue
            gp = ET.SubElement(svg, "Shape", Type="Group")
            gp.text = "\n  "
            gp.tail = "\n"
            children = ET.SubElement(gp, "Children")
            children.text = "\n  "
            children.tail = "\n"

            for j, path in enumerate(part.pathes):
                myColor = self.lbrn2_colors[4*int(path.params["rgb"][0])+2*int(path.params["rgb"][1])+int(path.params["rgb"][2])]

                p = []
                x, y = 0, 0
                C = ""
                start = None
                last = None
                commands = expand_path_arcs(path.path)
                num = 0
                cnt = 1
                end = len(commands) - 1
                if self.dbg:
                    for c in commands:
                        print ("6",num, c)
                        num += 1
                    num = 0

                c = commands[num]
                C, x, y = c[0:3]
                if self.dbg:
                    print("end:", end)
                while num < end or (C == "T" and num <= end):  # len(commands):
                    if self.dbg:
                        print("0", num)
                    c = commands[num]
                    if self.dbg: print("first: ", num, c)

                    C, x, y = c[0:3]
                    if C == "M":
                        if self.dbg: print ("1", num)
                        sh = ET.SubElement(children, "Shape", Type="Path", CutIndex=str(myColor))
                        sh.text = "\n  "
                        sh.tail = "\n"
                        vl = ET.SubElement(sh, "VertList")
                        vl.text = f"V{x:.3f} {y:.3f}c0x1c1x1"
                        vl.tail = "\n"
                        pl = ET.SubElement(sh, "PrimList")
                        pl.text = ""#f"L{cnt} {cnt+1}"
                        pl.tail = "\n"
                        start = c
                        x0, y0 = x, y
                        # do something with M
                        done = False
                        bspline = False
                        while done == False and num < end:  # len(commands):
                            num += 1
                            c = commands[num]
                            if self.dbg: print ("next: ",num, c)
                            C, x, y = c[0:3]
                            if C == "M":
                                if start and points_equal(start[1], start[2], x0, y0):
                                    pl.text = "LineClosed"
                                start = c
                                cnt = 1
                                if self.dbg: print ("next, because M")
                                done = True
                            elif C == "T":
                                if self.dbg: print ("next, because T")
                                done = True
                            else:
                                if C == "L":
                                    vl.text+=(f"V{x:.3f} {y:.3f}c0x1c1x1")
                                    pl.text += f"L{cnt-1} {cnt}"
                                    cnt +=1
                                elif C == "C":
                                    x1, y1, x2, y2 = c[3:]
                                    if self.dbg: print ("C: ",x0, y0, x1, y1, x, y, x2, y2)
                                    vl.text+=(f"V{x0:.3f} {y0:.3f}c0x{(x1):.3f}c0y{(y1):.3f}c1x1V{x:.3f} {y:.3f}c0x1c1x{(x2):.3f}c1y{(y2):.3f}")
                                    pl.text += f"L{cnt-1} {cnt}B{cnt} {cnt+1}"
                                    cnt +=2
                                    bspline = True
                                else:
                                    print("unknown", c)
                            if done == False:
                                x0, y0 = x, y

                        if start and points_equal(start[1], start[2], x0, y0):
                                if bspline == False:
                                    pl.text = "LineClosed"
                        start = c
                        if self.dbg: print ("2", num)
                    elif C == "T":
                        cnt = 1
                        #C = ""
                        if self.dbg: print ("3", num)
                        m, text, params = c[3:]
                        m = m * Affine.translation(0, params['fs'])
                        if self.dbg: print ("T: ",x, y, c)
                        num += 1
                        font, bold, italic = params['ff']
                        if params.get('font', 'Arial')=='Arial':
                            f = self.fonts[font]
                        else:
                            f = params.get('font', 'Arial')
                        fontColor = self.lbrn2_colors[4*int(params["rgb"][0])+2*int(params["rgb"][1])+int(params["rgb"][2])]

                        #alignment can be left|middle|end
                        if params.get('align', 'left')=='middle':
                            hor = '1'
                        else:
                            if params.get('align', 'left')=='end':
                                hor = '2'
                            else:
                                hor = '0'
                        ver = 1 # vertical is always bottom, text is shifted in box class

                        pos = text.find('%')
                        offs = 0
                        if pos >- 1:
                            if self.dbg: print ("p: ", pos, text[pos+1:pos+3])
                            texttype = '2'
                            if self.dbg: print("l ", len(text[pos+1:pos+3]))
                            if text[pos+1:pos+2].isnumeric():
                                if self.dbg: print ("t0", text[pos+1:pos+3])
                                if text[pos+1:pos+3].isnumeric() and len(text[pos+1:pos+3]) == 2:
                                    if self.dbg: print ("t1")
                                    if text[pos:pos+3] in txtOffset:
                                        if self.dbg: print ("t2")
                                        offs = txtOffset[text[pos:pos+3]] + 1
                                    else:
                                        if self.dbg: print ("t3")
                                        offs = 0
                                    txtOffset[text[pos:pos+3]] = offs
                                else:
                                    if self.dbg: print ("t4")
                                    if text[pos:pos+2] in txtOffset:
                                        if self.dbg: print ("t5")
                                        offs = txtOffset[text[pos:pos+2]] + 1
                                    else:
                                        offs = 0
                                        if self.dbg: print ("t6")
                                    txtOffset[text[pos:pos+2]] = offs
                            else:
                                if self.dbg: print ("t7")
                                texttype = '0'
                        else:
                            texttype = '0'
                            if self.dbg: print ("t8")
                        if self.dbg: print ("o: ", text, txtOffset, offs)

                        if not text:
                            if self.dbg: print ("T: text with empty string - ",x, y, c)
                        else:
                            sh = ET.SubElement(children, "Shape", Type="Text", CutIndex=str(fontColor), Font=f"{f}", H=f"{(params['fs']*1.75*0.6086434):.3f}", Str=f"{text}", Bold=f"{'1' if bold else '0'}", Italic=f"{'1' if italic else '0'}", Ah=f"{str(hor)}", Av=f"{str(ver)}", Eval=f"{texttype}", VariableOffset=f"{str(offs)}")  # 1mm = 1.75 Lightburn H units
                            sh.text = "\n  "
                            sh.tail = "\n"
                            xf = ET.SubElement(sh, "XForm")
                            xf.text = " ".join(f"{m[i]:.3f}" for i in (0, 3, 1, 4, 2, 5))
                            xf.tail = "\n"
                    else:
                        if self.dbg: print ("4", num)
                        print ("next, because not M")
                        num += 1

        url = self.metadata["url"].replace("&render=1", "") # remove render argument to get web form again

        pl = ET.SubElement(svg, "Notes", ShowOnLoad="1", Notes="File created by Boxes.py script, programmed by Florian Festi.\nLightburn output by Klaus Steinhammer.\n\nURL with settings:\n" + str(url))
        pl.text = ""
        pl.tail = "\n"

        if self.dbg: print ("5", num)
        f = io.BytesIO()
        tree.write(f, encoding="utf-8", xml_declaration=True, method="xml")
        f.seek(0)
        return f

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
        # todo: deal with parallel line intersection / overlay
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
