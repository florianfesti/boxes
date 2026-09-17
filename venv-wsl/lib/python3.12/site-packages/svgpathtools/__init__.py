from .bezier import (bezier_point, bezier2polynomial,
                     polynomial2bezier, split_bezier,
                     bezier_bounding_box, bezier_intersections,
                     bezier_by_line_intersections)
from .path import (Path, Line, QuadraticBezier, CubicBezier, Arc,
                   bezier_segment, is_bezier_segment, is_path_segment,
                   is_bezier_path, concatpaths, poly2bez, bpoints2bezier,
                   closest_point_in_path, farthest_point_in_path,
                   path_encloses_pt, bbox2path, polygon, polyline)
from .parser import parse_path
from .paths2svg import disvg, wsvg, paths2Drawing
from .polytools import polyroots, polyroots01, rational_limit, real, imag
from .misctools import hex2rgb, rgb2hex
from .smoothing import smoothed_path, smoothed_joint, is_differentiable, kinks
from .document import (Document, CONVERSIONS, CONVERT_ONLY_PATHS,
                       SVG_GROUP_TAG, SVG_NAMESPACE)
from .svg_io_sax import SaxDocument

try:
    from .svg_to_paths import svg2paths, svg2paths2, svgstr2paths
except ImportError:
    pass
