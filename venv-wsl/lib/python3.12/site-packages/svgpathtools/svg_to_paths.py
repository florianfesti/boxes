"""This submodule contains tools for creating path objects from SVG files.
The main tool being the svg2paths() function."""

# External dependencies
from __future__ import division, absolute_import, print_function
from xml.dom.minidom import parse
import os
from io import StringIO
import re
try:
    from os import PathLike as FilePathLike
except ImportError:
    FilePathLike = str

# Internal dependencies
from .parser import parse_path


COORD_PAIR_TMPLT = re.compile(
    r'([\+-]?\d*[\.\d]\d*[eE][\+-]?\d+|[\+-]?\d*[\.\d]\d*)' +
    r'(?:\s*,\s*|\s+|(?=-))' +
    r'([\+-]?\d*[\.\d]\d*[eE][\+-]?\d+|[\+-]?\d*[\.\d]\d*)'
)


def path2pathd(path):
    return path.get('d', '')


def ellipse2pathd(ellipse, use_cubics=False):
    """converts the parameters from an ellipse or a circle to a string for a 
    Path object d-attribute"""

    cx = ellipse.get('cx', 0)
    cy = ellipse.get('cy', 0)
    rx = ellipse.get('rx', None)
    ry = ellipse.get('ry', None)
    r = ellipse.get('r', None)

    if r is not None:
        rx = ry = float(r)
    else:
        rx = float(rx)
        ry = float(ry)

    cx = float(cx)
    cy = float(cy)

    if use_cubics:
        # Modified by NXP 2024, 2025
        PATH_KAPPA = 0.552284
        rxKappa = rx * PATH_KAPPA;
        ryKappa = ry * PATH_KAPPA;

        #According to the SVG specification (https://lists.w3.org/Archives/Public/www-archive/2005May/att-0005/SVGT12_Main.pdf),
        #Section 9.4, "The 'ellipse' element": "The arc of an 'ellipse' element begins at the "3 o'clock" point on
        #the radius and progresses towards the "9 o'clock". Therefore, the ellipse begins at the rightmost point
        #and progresses clockwise.
        d = ''
        # Move to the rightmost point
        d += 'M' + str(cx + rx) + ' ' + str(cy)
        # Draw bottom-right quadrant
        d += 'C' + str(cx + rx) + ' ' + str(cy + ryKappa) + ' ' + str(cx + rxKappa) + ' ' + str(cy + ry) + ' ' + str(cx) + ' ' + str(cy + ry)
        # Draw bottom-left quadrant
        d += 'C' + str(cx - rxKappa) + ' ' + str(cy + ry) + ' ' + str(cx - rx) + ' ' + str(cy + ryKappa) + ' ' + str(cx - rx) + ' ' + str(cy)
        # Draw top-left quadrant
        d += 'C' + str(cx - rx) + ' ' + str(cy - ryKappa) + ' ' + str(cx - rxKappa) + ' ' + str(cy - ry) + ' ' + str(cx) + ' ' + str(cy - ry)
        # Draw top-right quadrant
        d += 'C' + str(cx + rxKappa) + ' ' + str(cy - ry) + ' ' + str(cx + rx) + ' ' + str(cy - ryKappa) + ' ' + str(cx + rx) + ' ' + str(cy)
    else:
        d = ''
        d += 'M' + str(cx - rx) + ',' + str(cy)
        d += 'a' + str(rx) + ',' + str(ry) + ' 0 1,0 ' + str(2 * rx) + ',0'
        d += 'a' + str(rx) + ',' + str(ry) + ' 0 1,0 ' + str(-2 * rx) + ',0'

    return d + 'z'


def polyline2pathd(polyline, is_polygon=False):
    """converts the string from a polyline points-attribute to a string for a
    Path object d-attribute"""
    if isinstance(polyline, str):
        points = polyline
    else:
        points = COORD_PAIR_TMPLT.findall(polyline.get('points', ''))

    if len(points) == 0:
        return ''

    closed = (float(points[0][0]) == float(points[-1][0]) and
              float(points[0][1]) == float(points[-1][1]))

    # The `parse_path` call ignores redundant 'z' (closure) commands
    # e.g. `parse_path('M0 0L100 100Z') == parse_path('M0 0L100 100L0 0Z')`
    # This check ensures that an n-point polygon is converted to an n-Line path.
    if is_polygon and closed:
        points.append(points[0])

    d = 'M' + 'L'.join('{0} {1}'.format(x,y) for x,y in points)
    if is_polygon or closed:
        d += 'z'
    return d


def polygon2pathd(polyline, is_polygon=True):
    """converts the string from a polygon points-attribute to a string 
    for a Path object d-attribute.
    Note:  For a polygon made from n points, the resulting path will be
    composed of n lines (even if some of these lines have length zero).
    """
    return polyline2pathd(polyline, is_polygon)


def rect2pathd(rect):
    """Converts an SVG-rect element to a Path d-string.
    
    The rectangle will start at the (x,y) coordinate specified by the 
    rectangle object and proceed counter-clockwise."""
    x, y = float(rect.get('x', 0)), float(rect.get('y', 0))
    w, h = float(rect.get('width', 0)), float(rect.get('height', 0))

    if 'rx' in rect.keys() or 'ry' in rect.keys():

        # if only one, rx or ry, is present, use that value for both
        # https://developer.mozilla.org/en-US/docs/Web/SVG/Element/rect
        rx = rect.get('rx', None)
        ry = rect.get('ry', None)
        if rx is None:
            rx = ry or 0.
        if ry is None:
            ry = rx or 0.
        rx, ry = float(rx), float(ry)

        d = "M {} {} ".format(x + rx, y)  # right of p0
        d += "L {} {} ".format(x + w - rx, y)  # go to p1
        d += "A {} {} 0 0 1 {} {} ".format(rx, ry, x+w, y+ry)  # arc for p1
        d += "L {} {} ".format(x+w, y+h-ry)  # above p2
        d += "A {} {} 0 0 1 {} {} ".format(rx, ry, x+w-rx, y+h)  # arc for p2
        d += "L {} {} ".format(x+rx, y+h)  # right of p3
        d += "A {} {} 0 0 1 {} {} ".format(rx, ry, x, y+h-ry)  # arc for p3
        d += "L {} {} ".format(x, y+ry)  # below p0
        d += "A {} {} 0 0 1 {} {} z".format(rx, ry, x+rx, y)  # arc for p0
        return d

    x0, y0 = x, y
    x1, y1 = x + w, y
    x2, y2 = x + w, y + h
    x3, y3 = x, y + h

    d = ("M{} {} L {} {} L {} {} L {} {} z"
         "".format(x0, y0, x1, y1, x2, y2, x3, y3))
        
    return d


def line2pathd(l):
    return (
        'M' + l.attrib.get('x1', '0') + ' ' + l.attrib.get('y1', '0')
        + 'L' + l.attrib.get('x2', '0') + ' ' + l.attrib.get('y2', '0')
    )


def svg2paths(svg_file_location,
              return_svg_attributes=False,
              convert_circles_to_paths=True,
              convert_ellipses_to_paths=True,
              convert_lines_to_paths=True,
              convert_polylines_to_paths=True,
              convert_polygons_to_paths=True,
              convert_rectangles_to_paths=True):
    """Converts an SVG into a list of Path objects and attribute dictionaries. 

    Converts an SVG file into a list of Path objects and a list of
    dictionaries containing their attributes.  This currently supports
    SVG Path, Line, Polyline, Polygon, Circle, and Ellipse elements.

    Args:
        svg_file_location (string or file-like object): the location of the
            svg file on disk or a file-like object containing the content of a
            svg file
        return_svg_attributes (bool): Set to True and a dictionary of
            svg-attributes will be extracted and returned.  See also the 
            `svg2paths2()` function.
        convert_circles_to_paths: Set to False to exclude SVG-Circle
            elements (converted to Paths).  By default circles are included as 
            paths of two `Arc` objects.
        convert_ellipses_to_paths (bool): Set to False to exclude SVG-Ellipse
            elements (converted to Paths).  By default ellipses are included as 
            paths of two `Arc` objects.
        convert_lines_to_paths (bool): Set to False to exclude SVG-Line elements
            (converted to Paths)
        convert_polylines_to_paths (bool): Set to False to exclude SVG-Polyline
            elements (converted to Paths)
        convert_polygons_to_paths (bool): Set to False to exclude SVG-Polygon
            elements (converted to Paths)
        convert_rectangles_to_paths (bool): Set to False to exclude SVG-Rect
            elements (converted to Paths).

    Returns: 
        list: The list of Path objects.
        list: The list of corresponding path attribute dictionaries.
        dict (optional): A dictionary of svg-attributes (see `svg2paths2()`).
    """
    # strings are interpreted as file location everything else is treated as
    # file-like object and passed to the xml parser directly
    from_filepath = isinstance(svg_file_location, str) or isinstance(svg_file_location, FilePathLike)
    svg_file_location = os.path.abspath(svg_file_location) if from_filepath else svg_file_location

    doc = parse(svg_file_location)

    def dom2dict(element):
        """Converts DOM elements to dictionaries of attributes."""
        keys = list(element.attributes.keys())
        values = [val.value for val in list(element.attributes.values())]
        return dict(list(zip(keys, values)))

    # Use minidom to extract path strings from input SVG
    paths = [dom2dict(el) for el in doc.getElementsByTagName('path')]
    d_strings = [el['d'] for el in paths]
    attribute_dictionary_list = paths

    # Use minidom to extract polyline strings from input SVG, convert to
    # path strings, add to list
    if convert_polylines_to_paths:
        plins = [dom2dict(el) for el in doc.getElementsByTagName('polyline')]
        d_strings += [polyline2pathd(pl) for pl in plins]
        attribute_dictionary_list += plins

    # Use minidom to extract polygon strings from input SVG, convert to
    # path strings, add to list
    if convert_polygons_to_paths:
        pgons = [dom2dict(el) for el in doc.getElementsByTagName('polygon')]
        d_strings += [polygon2pathd(pg, True) for pg in pgons]
        attribute_dictionary_list += pgons

    if convert_lines_to_paths:
        lines = [dom2dict(el) for el in doc.getElementsByTagName('line')]
        d_strings += [('M' + l['x1'] + ' ' + l['y1'] +
                       'L' + l['x2'] + ' ' + l['y2']) for l in lines]
        attribute_dictionary_list += lines

    if convert_ellipses_to_paths:
        ellipses = [dom2dict(el) for el in doc.getElementsByTagName('ellipse')]
        d_strings += [ellipse2pathd(e) for e in ellipses]
        attribute_dictionary_list += ellipses

    if convert_circles_to_paths:
        circles = [dom2dict(el) for el in doc.getElementsByTagName('circle')]
        d_strings += [ellipse2pathd(c) for c in circles]
        attribute_dictionary_list += circles

    if convert_rectangles_to_paths:
        rectangles = [dom2dict(el) for el in doc.getElementsByTagName('rect')]
        d_strings += [rect2pathd(r) for r in rectangles]
        attribute_dictionary_list += rectangles

    if return_svg_attributes:
        svg_attributes = dom2dict(doc.getElementsByTagName('svg')[0])
        doc.unlink()
        path_list = [parse_path(d) for d in d_strings]
        return path_list, attribute_dictionary_list, svg_attributes
    else:
        doc.unlink()
        path_list = [parse_path(d) for d in d_strings]
        return path_list, attribute_dictionary_list


def svg2paths2(svg_file_location,
               return_svg_attributes=True,
               convert_circles_to_paths=True,
               convert_ellipses_to_paths=True,
               convert_lines_to_paths=True,
               convert_polylines_to_paths=True,
               convert_polygons_to_paths=True,
               convert_rectangles_to_paths=True):
    """Convenience function; identical to svg2paths() except that
    return_svg_attributes=True by default.  See svg2paths() docstring for more
    info."""
    return svg2paths(svg_file_location=svg_file_location,
                     return_svg_attributes=return_svg_attributes,
                     convert_circles_to_paths=convert_circles_to_paths,
                     convert_ellipses_to_paths=convert_ellipses_to_paths,
                     convert_lines_to_paths=convert_lines_to_paths,
                     convert_polylines_to_paths=convert_polylines_to_paths,
                     convert_polygons_to_paths=convert_polygons_to_paths,
                     convert_rectangles_to_paths=convert_rectangles_to_paths)


def svgstr2paths(svg_string,
               return_svg_attributes=False,
               convert_circles_to_paths=True,
               convert_ellipses_to_paths=True,
               convert_lines_to_paths=True,
               convert_polylines_to_paths=True,
               convert_polygons_to_paths=True,
               convert_rectangles_to_paths=True):
    """Convenience function; identical to svg2paths() except that it takes the
    svg object as string.  See svg2paths() docstring for more
    info."""
    # wrap string into StringIO object
    svg_file_obj = StringIO(svg_string)
    return svg2paths(svg_file_location=svg_file_obj,
                     return_svg_attributes=return_svg_attributes,
                     convert_circles_to_paths=convert_circles_to_paths,
                     convert_ellipses_to_paths=convert_ellipses_to_paths,
                     convert_lines_to_paths=convert_lines_to_paths,
                     convert_polylines_to_paths=convert_polylines_to_paths,
                     convert_polygons_to_paths=convert_polygons_to_paths,
                     convert_rectangles_to_paths=convert_rectangles_to_paths)
