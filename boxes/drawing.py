from __future__ import annotations

import codecs
import io
import math
import re
from typing import Any
from xml.etree import ElementTree as ET

from affine import Affine

from boxes.Color import RGB, ColorPalette
from boxes.extents import Extents

EPS = 1e-4
PADDING = 10

# Dog bones are drawn this much (in mm) larger than the radius of the router
# bit. A notch exactly the size of the bit may be dropped by CAM software when
# offsetting the tool path.
DOGBONE_CLEARANCE = 0.1

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
            m = Affine.scale(self.scale, -self.scale) @ m
            m = Affine.translation(0, self.scale*extents.height) @ m
        else:
            m = Affine.scale(self.scale, self.scale) @ m

        self.transform(self.scale, m, self.invert_y)

        return Extents(0, 0, extents.width * self.scale, extents.height * self.scale)

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
                        x_, y_ = m @ (x, y)
                        e.add(x_, y_)
        return e

    def transform(self, f, m, invert_y=False):
        self.params["lw"] *= f
        for c in self.path:
            C = c[0]
            c[1], c[2] = m @ (c[1], c[2])
            if C == 'C':
                c[3], c[4] = m @ (c[3], c[4])
                c[5], c[6] = m @ (c[5], c[6])
            if C == "T":
                c[3] = m @ c[3]
                if invert_y:
                    c[3] @= Affine.scale(1, -1)
            if C == "D":
                c[3] *= f

    def faster_edges(self, inner_corners):
        if inner_corners == "dogbone":
            self.path = apply_dogbones(self.path)
            # clean up remaining inverted arcs (e.g. of small rounded corners)
            inner_corners = "corner"
        if inner_corners == "backarc":
            return

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
        self._mxy = self._m @ self._xy
        self._lw = 0
        self._rgb: RGB = ColorPalette.BLACK
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
        self._m @= Affine.translation(x, y)
        self._xy = (0, 0)

    def scale(self, sx, sy):
        self._m @= Affine.scale(sx, sy)

    def rotate(self, r):
        self._m @= Affine.rotation(180 * r / math.pi)

    def set_line_width(self, lw):
        self._lw = lw

    def set_source_rgb(self, r: int, g: int, b: int):
        if not (0 <= r <= 255):
            raise ValueError("red must be 0–255")
        if not (0 <= g <= 255):
            raise ValueError("green must be 0–255")
        if not (0 <= b <= 255):
            raise ValueError("blue must be 0–255")
        self._rgb = RGB(r, g, b)

    ## path methods

    def _line_to(self, x, y):
        self._add_move()
        x1, y1 = self._mxy
        self._xy = x, y
        x2, y2 = self._mxy = self._m @ self._xy
        if not points_equal(x1, y1, x2, y2):
            self._dwg.append("L", x2, y2)

    def _add_move(self):
        self._dwg.move_to(*self._mxy)

    def move_to(self, x, y):
        self._xy = (x, y)
        self._mxy = self._m @ self._xy

    def mark_inner_corner(self, radius, backarc):
        """Mark a sharp inner corner at the current point for dog bones

        :param radius: radius of the dog bone (bit radius plus clearance)
        :param backarc: whether the burn correction adds an inverted arc
        """
        self._add_move()
        r = radius * abs(self._m.determinant) ** 0.5
        self._dwg.append("D", *self._mxy, r, backarc)

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

        mx1, my1 = self._m @ (x1, y1)
        mx2, my2 = self._m @ (x2, y2)
        mx3, my3 = self._m @ (x3, y3)
        mx4, my4 = self._m @ (x4, y4)
        mxc, myc = self._m @ (xc, yc)

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
        mx1, my1 = self._m @ (x1, y1)
        mx2, my2 = self._m @ (x2, y2)
        mx3, my3 = self._m @ (x3, y3)
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
        raise NotImplementedError

    def set_font(self, style, bold=False, italic=False):
        if style not in ("serif", "sans-serif", "monospaced"):
            raise ValueError("Unknown font style")
        self._ff = (style, bold, italic)

    def set_font_size(self, fs):
        self._fs = fs

    def show_text(self, text, **args):
        params = {"ff": self._ff, "fs": self._fs, "lw": self._lw, "rgb": self._rgb}
        params.update(args)
        mx0, my0 = self._m @ self._xy
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

        url_desc: str = ""
        if md.get("url"):
            self._addTag(w, 'dc:source', md["url"])
            self._addTag(w, 'dc:source', md["url_short"])
            remove_render = re.compile(r'&render=\d+')
            settings_url = remove_render.sub('', md["url"])
            settings_url_short = remove_render.sub('', md["url_short"])
            url_desc = f"Url: {md['url']}\n"
            url_desc += f"Url short: {md['url_short']}\n"
            url_desc += f"SettingsUrl: {settings_url}\n"
            url_desc += f"SettingsUrl short: {settings_url_short}\n"
        else:
            self._addTag(w, 'dc:source', md["cli"])

        desc = md["short_description"] or ""
        if md.get("description"):
            desc += f"\n\n{md['description']}"
        desc += "\n\nCreated with Boxes.py (https://boxes.hackerspace-bamberg.de/)\n"
        desc += f"Command line: {md['cli']}\n"
        desc += f"Command line short: {md['cli_short']}\n"
        desc += url_desc
        self._addTag(w, 'dc:description', desc)

        # title
        self._addTag(root, "title", md["name"], True)

        # Add XML comment
        txt = f"\n{md['name']} - {md['short_description']}\n"
        if md.get("description"):
            txt += f"\n\n{md['description']}\n\n"
        txt += """\nCreated with Boxes.py (https://boxes.hackerspace-bamberg.de/)\n"""
        if not md["reproducible"]:
            txt += f"""Creation date: {creation_date}\n"""

        txt += f"Command line (remove spaces between dashes): {md['cli_short']}\n"
        txt += url_desc

        m = ET.Comment(txt.replace("--", "- -").replace("--", "- -")) # ----
        m.tail = '\n'
        root.insert(0, m)

    def finish(self, inner_corners="loop"):
        extents = self._adjust_coordinates()
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
                path.faster_edges(inner_corners)
                for c in path.path:
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
                        m = m @ Affine.translation(0, -params['fs'])
                        tm = " ".join(f"{m[i]:.3f}" for i in (0, 3, 1, 4, 2, 5))
                        font, bold, italic = params['ff']
                        fontweight = ("normal", "bold")[bool(bold)]
                        fontstyle = ("normal", "italic")[bool(italic)]

                        style = f"font-family: {font} ; font-weight: {fontweight}; font-style: {fontstyle}; fill: {params['rgb'].as_css()}"
                        t = ET.SubElement(g, "text",
                                          #x=f"{x:.3f}", y=f"{y:.3f}",
                                          transform=f"matrix( {tm} )",
                                          style=style)
                        t.text = text
                        t.set("font-size", f"{params['fs']}px")
                        t.set("text-anchor", params.get('align', 'left'))
                        t.set("dominant-baseline", 'hanging')
                        t.tail = "\n  "
                    else:
                        print("Unknown", c)

                    last = c

                if start and start is not last and \
                   points_equal(start[1], start[2], last[1], last[2]):
                    p.append("Z")
                color = (
                    RGB.random().as_css()
                    if RANDOMIZE_COLORS
                    else path.params["rgb"].as_css()
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
            desc += f"%% {line}\n"
        desc += "%\n"
        if md.get("description"):
            desc += "%\n"
            for line in md["description"].split("\n"):
                desc += f"%% {line}\n"
            desc += "%\n"

        desc += f"%% Command line: {md['cli']}\n"
        desc += f"%% Command line short: {md['cli_short']}\n"
        if md.get("url"):
            remove_render = re.compile(r'&render=\d+')
            settings_url = remove_render.sub('', md["url"])
            settings_url_short = remove_render.sub('', md["url_short"])
            desc += f'%%Url: {md["url"]}\n'
            desc += f'%%Url short: {md["url_short"]}\n'
            desc += f'%%SettingsUrl: {settings_url}\n'
            desc += f'%%SettingsUrl short: {settings_url_short}\n'
        return desc

    def finish(self, inner_corners="loop"):

        extents = self._adjust_coordinates()
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
                path.faster_edges(inner_corners)

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
                        m, text, params = c[3:]
                        tm = " ".join(f"{m[i]:.3f}" for i in (0, 3, 1, 4, 2, 5))
                        text = text.replace("(", r"\(").replace(")", r"\)")
                        color = " ".join(f"{c:.2f}" for c in params["rgb"].as_float_tuple())
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

                if p:  # todo: might be empty since text is not implemented yet
                    color = " ".join(f"{c:.2f}" for c in path.params["rgb"].as_float_tuple())
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

    def finish(self, inner_corners="loop"):
        if self.dbg: print("LBRN2 save")
        extents = self._adjust_coordinates()
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
                myColor = self.lbrn2_colors[4*int(path.params["rgb"].as_float_tuple()[0])+2*int(path.params["rgb"].as_float_tuple()[1])+int(path.params["rgb"].as_float_tuple()[2])]

                p = []
                x, y = 0, 0
                C = ""
                start = None
                last = None
                path.faster_edges(inner_corners)
                num = 0
                cnt = 1
                end = len(path.path) - 1
                if self.dbg:
                    for c in path.path:
                        print ("6",num, c)
                        num += 1
                    num = 0

                c = path.path[num]
                C, x, y = c[0:3]
                if self.dbg:
                    print("end:", end)
                while num < end or (C == "T" and num <= end):  # len(path.path):
                    if self.dbg:
                        print("0", num)
                    c = path.path[num]
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
                        while done == False and num < end:  # len(path.path):
                            num += 1
                            c = path.path[num]
                            if self.dbg: print ("next: ",num, c)
                            C, x, y = c[0:3]
                            if C == "M":
                                if start and points_equal(start[1], start[2], x0, y0):
                                    pl.text += f"L{cnt-1} 0"
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
                                else:
                                    pl.text += f"L{cnt-1} 0"
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
                        fontColor = self.lbrn2_colors[4*int(params["rgb"].as_float_tuple()[0])+2*int(params["rgb"].as_float_tuple()[1])+int(params["rgb"].as_float_tuple()[2])]

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


### Dog bones

def _unit(v):
    l = math.hypot(*v)
    if l < EPS:
        return None
    return (v[0] / l, v[1] / l)


def _sweep(a_from, a_to, direction):
    """Angle from a_from to a_to going in direction (+1 ccw, -1 cw)"""
    d = (a_to - a_from) % (2 * math.pi)
    if direction > 0:
        return d
    return d - 2 * math.pi if d > EPS else 0.0


def _arc_to_beziers(center, radius, start, end, direction):
    """Bezier curves ("C" commands) for a circular arc from start to end"""
    cx, cy = center
    a0 = math.atan2(start[1] - cy, start[0] - cx)
    a_end = math.atan2(end[1] - cy, end[0] - cx)
    sweep = _sweep(a0, a_end, direction)
    n = max(1, math.ceil(abs(sweep) / (0.5 * math.pi) - 1e-9))
    phi = sweep / n
    k = 4 / 3 * math.tan(phi / 4) * radius
    result = []
    for i in range(n):
        a1 = a0 + phi
        x0, y0 = cx + radius * math.cos(a0), cy + radius * math.sin(a0)
        x3, y3 = cx + radius * math.cos(a1), cy + radius * math.sin(a1)
        c1 = (x0 - k * math.sin(a0), y0 + k * math.cos(a0))
        c2 = (x3 + k * math.sin(a1), y3 - k * math.cos(a1))
        if i == n - 1:
            x3, y3 = end
        result.append(["C", x3, y3, *c1, *c2])
        a0 = a1
    return result


def _circle_intersection(c1, c2, r):
    """Both intersections of two circles with the same radius"""
    d = math.dist(c1, c2)
    if d < EPS or d >= 2 * r:
        return None
    mx, my = (c1[0] + c2[0]) / 2, (c1[1] + c2[1]) / 2
    h = math.sqrt(r * r - (d / 2) ** 2)
    nx, ny = -(c2[1] - c1[1]) / d, (c2[0] - c1[0]) / d
    return (mx + h * nx, my + h * ny), (mx - h * nx, my - h * ny)


def _segment_circle(p, q, center, r):
    """Parameters t in [0, 1] where the segment p->q crosses the circle"""
    dx, dy = q[0] - p[0], q[1] - p[1]
    fx, fy = p[0] - center[0], p[1] - center[1]
    a = dx * dx + dy * dy
    b = 2 * (fx * dx + fy * dy)
    c = fx * fx + fy * fy - r * r
    disc = b * b - 4 * a * c
    if a < EPS * EPS or disc < 0:
        return []
    s = math.sqrt(disc)
    return [t for t in ((-b - s) / (2 * a), (-b + s) / (2 * a))
            if -EPS <= t <= 1 + EPS]


def _find_dogbones(cmds, closed):
    """Find the corners marked with "D" that can get a dog bone"""
    corners = []
    for i, c in enumerate(cmds):
        if c[0] != "D":
            continue
        radius, backarc = c[3], c[4]
        if i < 2 or cmds[i - 1][0] != "L":
            continue
        li = i - 1
        j = i + 1
        backarc_idx = None
        if backarc:
            if j >= len(cmds) or cmds[j][0] != "C":
                continue
            backarc_idx = j
            j += 1
        wrap = False
        if j < len(cmds):
            out_start = cmds[j - 1][1:3]
            lo = j
        elif closed:
            out_start = cmds[0][1:3]
            lo = 1
            wrap = True
        else:
            continue
        if cmds[lo][0] != "L":
            continue
        a, b = cmds[li - 1][1:3], cmds[li][1:3]
        d = cmds[lo][1:3]
        d1, d2 = _unit(pdiff(b, a)), _unit(pdiff(d, out_start))
        if d1 is None or d2 is None:
            continue
        if backarc:
            _, x, y = line_intersection((a, b), (out_start, d))
            if x is None:
                continue
            v = (x, y)
        else:
            v = b
        # angle of the empty space in the corner
        theta = math.acos(max(-1.0, min(1.0, -d1[0] * d2[0] - d1[1] * d2[1])))
        if theta < math.radians(5) or theta > math.radians(175):
            continue
        bisector = _unit((d2[0] - d1[0], d2[1] - d1[1]))
        if bisector is None:
            continue
        # The circle goes through the corner with its center on the bisector
        chord = 2 * radius * math.cos(theta / 2)
        center = (v[0] + radius * bisector[0], v[1] + radius * bisector[1])
        p1 = (v[0] - chord * d1[0], v[1] - chord * d1[1])
        p2 = (v[0] + chord * d2[0], v[1] + chord * d2[1])
        cross = ((p1[0] - center[0]) * (v[1] - center[1]) -
                 (p1[1] - center[1]) * (v[0] - center[0]))
        corners.append({
            "i": i, "li": li, "lo": lo, "backarc_idx": backarc_idx,
            "wrap": wrap, "v": v, "d1": d1, "d2": d2, "chord": chord,
            "center": center, "radius": radius, "p1": p1, "p2": p2,
            "dir": 1 if cross > 0 else -1,
            "in_start": a, "out_end": d,
        })
    return corners


def _dogbone_subpath(cmds):
    if not any(c[0] == "D" for c in cmds):
        return cmds
    if cmds[0][0] != "M":
        return [c for c in cmds if c[0] != "D"]

    last = cmds[-1]
    closed = len(cmds) > 2 and points_equal(*cmds[0][1:3], *last[1:3])
    corners = _find_dogbones(cmds, closed)

    # Find where each dog bone starts and ends. If a line next to the corner
    # is too short the dog bone continues to the line before/after it. Lines
    # between two dog bones are handled below by intersecting the dog bones.
    by_in = {c["li"]: c for c in corners}
    by_out = {c["lo"]: c for c in corners}
    valid = {id(c) for c in corners}

    def used(k):
        return any(id(c) in valid for c in (by_in.get(k), by_out.get(k)) if c)

    def plan_in(c):
        prev = by_out.get(c["li"])
        if (prev is not None and id(prev) in valid) or \
           c["chord"] <= math.dist(c["v"], c["in_start"]) + EPS:
            return c["li"], c["p1"], None
        k = c["li"] - 1
        if k < 1 or cmds[k][0] != "L" or used(k):
            return None
        s, a = cmds[k - 1][1:3], cmds[k][1:3]
        ts = _segment_circle(s, a, c["center"], c["radius"])
        if not ts or math.dist(a, c["center"]) > c["radius"]:
            return None
        t = min(ts)
        return k, (s[0] + t * (a[0] - s[0]), s[1] + t * (a[1] - s[1])), c["li"]

    def plan_out(c):
        nxt = by_in.get(c["lo"])
        if (nxt is not None and id(nxt) in valid) or \
           c["chord"] <= math.dist(c["v"], c["out_end"]) + EPS:
            return c["p2"], None
        k = c["lo"] + 1
        if k >= len(cmds) or cmds[k][0] != "L" or used(k):
            return None
        e, f = cmds[c["lo"]][1:3], cmds[k][1:3]
        ts = _segment_circle(e, f, c["center"], c["radius"])
        if not ts or math.dist(e, c["center"]) > c["radius"]:
            return None
        t = max(ts)
        return (e[0] + t * (f[0] - e[0]), e[1] + t * (f[1] - e[1])), c["lo"]

    changed = True
    while changed:
        changed = False
        for c in corners:
            if id(c) in valid and (plan_in(c) is None or plan_out(c) is None):
                valid.discard(id(c))
                changed = True

    out: list[Any] = list(cmds)
    for c in corners:
        if id(c) not in valid:
            continue
        in_idx, start, drop_in = plan_in(c)
        end, drop_out = plan_out(c)
        out[in_idx] = ["L", *start]
        out[c["i"]] = ["A", *end, c]
        for k in (drop_in, drop_out, c["backarc_idx"]):
            if k is not None:
                out[k] = None
        if c["wrap"]:
            out[0] = ["M", *end]
    out = [c for c in out if c is not None and c[0] != "D"]

    # Intersect dog bones that overlap because the line between them is too short
    i = 0
    while i < len(out) - 2:
        a1, line, a2 = out[i], out[i + 1], out[i + 2]
        if a1[0] == "A" and line[0] == "L" and a2[0] == "A":
            info1, info2 = a1[3], a2[3]
            d2 = info1["d2"]
            if ((line[1] - a1[1]) * d2[0] + (line[2] - a1[2]) * d2[1]) < EPS:
                points = _circle_intersection(info1["center"], info2["center"],
                                              info1["radius"])
                if points:
                    # use the intersection away from the cut out area
                    v = info1["v"]
                    n = (info1["center"][0] - v[0], info1["center"][1] - v[1])
                    x = min(points, key=lambda p: (p[0] - v[0]) * n[0] +
                            (p[1] - v[1]) * n[1])
                    out[i] = ["A", *x, info1]
                    del out[i + 1]
                    continue
        i += 1

    result = []
    for c in out:
        if c[0] == "A":
            info = c[3]
            result.extend(_arc_to_beziers(info["center"], info["radius"],
                                          result[-1][1:3], c[1:3], info["dir"]))
        else:
            result.append(c)
    return result


def apply_dogbones(path):
    """Replace inner corners marked with "D" by dog bones

    The dog bones are circles going through the corner with their center on
    the bisector of the corner. That way the corner is cut out completely
    while removing as little extra material as possible.
    """
    merged = []
    for c in path:
        # corners > 100° are drawn in steps
        if (c[0] == "D" and merged and merged[-1][0] == "D" and
                points_equal(*merged[-1][1:3], *c[1:3])):
            continue
        merged.append(c)

    result = []
    sub = []
    for c in merged:
        if c[0] == "M" and sub:
            result.extend(_dogbone_subpath(sub))
            sub = []
        sub.append(c)
    if sub:
        result.extend(_dogbone_subpath(sub))
    return result
