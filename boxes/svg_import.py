"""Allow paths to be imported from an SVG file into boxes.py.

This is intended to make it easier to add custom cut-outs and engraving.
Currently, only a single path can be imported. This is generally sufficient
to import shapes drawn in OpenSCAD.
"""

import svg.path
from lxml import etree
from boxes.drawing import Context
import numpy as np

def draw_path_on_ctx(ctx: Context, path: svg.path.Path):
    """Draw an SVG path into the current context.
    
    This transforms the points according to the current context, but otherwise
    should just add the commands from the path into the output.
    """
    for seg in path:
        if isinstance(seg, svg.path.Move):
            ctx.move_to(seg.end.real, seg.end.imag)
        if isinstance(seg, svg.path.Close) or isinstance(seg, svg.path.Line):
            ctx.line_to(seg.end.real, seg.end.imag)
        elif isinstance(seg, svg.path.CubicBezier):
            ctx.curve_to(
                seg.control1.real,
                seg.control1.imag,
                seg.control2.real,
                seg.control2.imag,
                seg.end.real,
                seg.end.imag,
            )

def path_extent(path: svg.path.Path) -> tuple[tuple[float, float], tuple[float, float]]:
    """Determine max/min x,y positions in a path."""
    extent_x = [np.inf, -np.inf]
    extent_y = [np.inf, -np.inf]
    for seg in path:
        x, y = seg.end.real, seg.end.imag
        for extent, point in [(extent_x, x), (extent_y, y)]:
            extent[0] = min(extent[0], point)
            extent[1] = max(extent[1], point)
    return tuple(extent_x), tuple(extent_y)

def path_centre(path: svg.path.Path) -> tuple[float, float]:
    """Determine the middle point of a path."""
    (x0, x1), (y0, y1) = path_extent(path)
    return (x0 + x1)/2, (y0 + y1)/2

def load_path_from_svg(filename: str) -> svg.path.Path:
    """Load a path from an SVG file.
    
    This assumes there is a single path in the file, as is true for OpenSCAD
    exports.
    """
    tree = etree.parse(filename)
    path_nodes = tree.xpath("//svg:path", namespaces={'svg': "http://www.w3.org/2000/svg"})
    if len(path_nodes) > 1:
        raise RuntimeError("I can only cope with one path in an SVG!")
    data = path_nodes[0].get("d")
    return svg.path.parse_path(data)