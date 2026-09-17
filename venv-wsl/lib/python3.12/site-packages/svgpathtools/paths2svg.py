"""This submodule: basic tools for creating svg files from path data.

See also the document.py submodule.
"""

# External dependencies:
from __future__ import division, absolute_import, print_function
from math import ceil
from os import path as os_path, makedirs
from tempfile import gettempdir
from xml.dom.minidom import parse as md_xml_parse
from svgwrite import Drawing, text as txt
from time import time
from warnings import warn
import re

# Internal dependencies
from .path import Path, Line, is_path_segment
from .misctools import open_in_browser

# color shorthand for inputting color list as string of chars.
color_dict = {'a': 'aqua',
              'b': 'blue',
              'c': 'cyan',
              'd': 'darkblue',
              'e': '',
              'f': '',
              'g': 'green',
              'h': '',
              'i': '',
              'j': '',
              'k': 'black',
              'l': 'lime',
              'm': 'magenta',
              'n': 'brown',
              'o': 'orange',
              'p': 'pink',
              'q': 'turquoise',
              'r': 'red',
              's': 'salmon',
              't': 'tan',
              'u': 'purple',
              'v': 'violet',
              'w': 'white',
              'x': '',
              'y': 'yellow',
              'z': 'azure'}


def str2colorlist(s, default_color=None):
    color_list = [color_dict[ch] for ch in s]
    if default_color:
        for idx, c in enumerate(color_list):
            if not c:
                color_list[idx] = default_color
    return color_list


def is3tuple(c):
    return isinstance(c, tuple) and len(c) == 3


def big_bounding_box(paths_n_stuff):
    """returns minimal upright bounding box.

    Args:
        paths_n_stuff: iterable of Paths, Bezier path segments, and
            points (given as complex numbers).

    Returns:
        extrema of bounding box, (xmin, xmax, ymin, ymax)

    """
    bbs = []
    for thing in paths_n_stuff:
        if is_path_segment(thing) or isinstance(thing, Path):
            bbs.append(thing.bbox())
        elif isinstance(thing, complex):
            bbs.append((thing.real, thing.real, thing.imag, thing.imag))
        else:
            try:
                complexthing = complex(thing)
                bbs.append((complexthing.real, complexthing.real,
                            complexthing.imag, complexthing.imag))
            except ValueError:
                raise TypeError("paths_n_stuff can only contains Path, "
                                "CubicBezier, QuadraticBezier, Line, "
                                "and complex objects.")
    xmins, xmaxs, ymins, ymaxs = list(zip(*bbs))
    xmin = min(xmins)
    xmax = max(xmaxs)
    ymin = min(ymins)
    ymax = max(ymaxs)
    return xmin, xmax, ymin, ymax


def disvg(paths=None, colors=None, filename=None, stroke_widths=None,
          nodes=None, node_colors=None, node_radii=None,
          openinbrowser=True, timestamp=None, margin_size=0.1,
          mindim=600, dimensions=None, viewbox=None, text=None,
          text_path=None, font_size=None, attributes=None,
          svg_attributes=None, svgwrite_debug=False,
          paths2Drawing=False, baseunit='px'):
    """Creates (and optionally displays) an SVG file.

    REQUIRED INPUTS:
        :param paths - a list of paths

    OPTIONAL INPUT:
        :param colors - specifies the path stroke color.  By default all paths
        will be black (#000000).  This paramater can be input in a few ways
        1) a list of strings that will be input into the path elements stroke
            attribute (so anything that is understood by the svg viewer).
        2) a string of single character colors -- e.g. setting colors='rrr' is
            equivalent to setting colors=['red', 'red', 'red'] (see the
            'color_dict' dictionary above for a list of possibilities).
        3) a list of rgb 3-tuples -- e.g. colors = [(255, 0, 0), ...].

        :param filename - the desired location/filename of the SVG file
        created (by default the SVG will be named 'disvg_output.svg' or
        'disvg_output_<timestamp>.svg' and stored in the temporary
        directory returned by `tempfile.gettempdir()`.  See `timestamp`
        for information on the timestamp.

        :param stroke_widths - a list of stroke_widths to use for paths
        (default is 0.5% of the SVG's width or length)

        :param nodes - a list of points to draw as filled-in circles

        :param node_colors - a list of colors to use for the nodes (by default
        nodes will be red)

        :param node_radii - a list of radii to use for the nodes (by default
        nodes will be radius will be 1 percent of the svg's width/length)

        :param text - string or list of strings to be displayed

        :param text_path - if text is a list, then this should be a list of
        path (or path segments of the same length.  Note: the path must be
        long enough to display the text or the text will be cropped by the svg
        viewer.

        :param font_size - a single float of list of floats.

        :param openinbrowser -  Set to True to automatically open the created
        SVG in the user's default web browser.

        :param timestamp - if true, then the a timestamp will be
        appended to the output SVG's filename.  This is meant as a
        workaround for issues related to rapidly opening multiple
        SVGs in your browser using `disvg`. This defaults to true if
        `filename is None` and false otherwise.

        :param margin_size - The min margin (empty area framing the collection
        of paths) size used for creating the canvas and background of the SVG.

        :param mindim - The minimum dimension (height or width) of the output
        SVG (default is 600).

        :param dimensions - The (x,y) display dimensions of the output SVG.
        I.e. this specifies the `width` and `height` SVG attributes. Note that 
        these also can be used to specify units other than pixels. Using this 
        will override the `mindim` parameter.

        :param viewbox - This specifies the coordinated system used in the svg.
        The SVG `viewBox` attribute works together with the the `height` and 
        `width` attrinutes.  Using these three attributes allows for shifting 
        and scaling of the SVG canvas without changing the any values other 
        than those in `viewBox`, `height`, and `width`.  `viewbox` should be 
        input as a 4-tuple, (min_x, min_y, width, height), or a string 
        "min_x min_y width height".  Using this will override the `mindim` 
        parameter.

        :param attributes - a list of dictionaries of attributes for the input
        paths.  Note: This will override any other conflicting settings.

        :param svg_attributes - a dictionary of attributes for output svg.
        
        :param svgwrite_debug - This parameter turns on/off `svgwrite`'s 
        debugging mode.  By default svgwrite_debug=False.  This increases 
        speed and also prevents `svgwrite` from raising of an error when not 
        all `svg_attributes` key-value pairs are understood.
        
        :param paths2Drawing - If true, an `svgwrite.Drawing` object is 
        returned and no file is written.  This `Drawing` can later be saved 
        using the `svgwrite.Drawing.save()` method.

    NOTES:
        * The `svg_attributes` parameter will override any other conflicting 
        settings.

        * Any `extra` parameters that `svgwrite.Drawing()` accepts can be 
        controlled by passing them in through `svg_attributes`.

        * The unit of length here is assumed to be pixels in all variables.

        * If this function is used multiple times in quick succession to
        display multiple SVGs (all using the default filename), the
        svgviewer/browser will likely fail to load some of the SVGs in time.
        To fix this, use the timestamp attribute, or give the files unique
        names, or use a pause command (e.g. time.sleep(1)) between uses.

    SEE ALSO:
        * document.py
    """

    _default_relative_node_radius = 5e-3
    _default_relative_stroke_width = 1e-3
    _default_path_color = '#000000'  # black
    _default_node_color = '#ff0000'  # red
    _default_font_size = 12

    if filename is None:
        timestamp = True if timestamp is None else timestamp
        filename = os_path.join(gettempdir(), 'disvg_output.svg')

    dirname = os_path.abspath(os_path.dirname(filename))
    if not os_path.exists(dirname):
        makedirs(dirname)

    # append time stamp to filename
    if timestamp:
        fbname, fext = os_path.splitext(filename)
        tstamp = str(time()).replace('.', '')
        stfilename = os_path.split(fbname)[1] + '_' + tstamp + fext
        filename = os_path.join(dirname, stfilename)

    # check paths and colors are set
    if isinstance(paths, Path) or is_path_segment(paths):
        paths = [paths]
    if paths:
        if not colors:
            colors = [_default_path_color] * len(paths)
        else:
            assert len(colors) == len(paths)
            if isinstance(colors, str):
                colors = str2colorlist(colors,
                                       default_color=_default_path_color)
            elif isinstance(colors, list):
                for idx, c in enumerate(colors):
                    if is3tuple(c):
                        colors[idx] = "rgb" + str(c)

    # check nodes and nodes_colors are set (node_radii are set later)
    if nodes:
        if not node_colors:
            node_colors = [_default_node_color] * len(nodes)
        else:
            assert len(node_colors) == len(nodes)
            if isinstance(node_colors, str):
                node_colors = str2colorlist(node_colors,
                                            default_color=_default_node_color)
            elif isinstance(node_colors, list):
                for idx, c in enumerate(node_colors):
                    if is3tuple(c):
                        node_colors[idx] = "rgb" + str(c)

    # set up the viewBox and display dimensions of the output SVG
    # along the way, set stroke_widths and node_radii if not provided
    assert paths or nodes
    stuff2bound = []
    if viewbox:
        if not isinstance(viewbox, str):
            viewbox = '%s %s %s %s' % viewbox
        if dimensions is None:
            dimensions = viewbox.split(' ')[2:4]
    elif dimensions:
        dimensions = tuple(map(str, dimensions))
        def strip_units(s):
            return re.search(r'\d*\.?\d*', s.strip()).group()
        viewbox = '0 0 %s %s' % tuple(map(strip_units, dimensions))
    else:
        if paths:
            stuff2bound += paths
        if nodes:
            stuff2bound += nodes
        if text_path:
            stuff2bound += text_path
        xmin, xmax, ymin, ymax = big_bounding_box(stuff2bound)
        dx = xmax - xmin
        dy = ymax - ymin

        if dx == 0:
            dx = 1
        if dy == 0:
            dy = 1

        # determine stroke_widths to use (if not provided) and max_stroke_width
        if paths:
            if not stroke_widths:
                sw = max(dx, dy) * _default_relative_stroke_width
                stroke_widths = [sw]*len(paths)
                max_stroke_width = sw
            else:
                assert len(paths) == len(stroke_widths)
                max_stroke_width = max(stroke_widths)
        else:
            max_stroke_width = 0

        # determine node_radii to use (if not provided) and max_node_diameter
        if nodes:
            if not node_radii:
                r = max(dx, dy) * _default_relative_node_radius
                node_radii = [r]*len(nodes)
                max_node_diameter = 2*r
            else:
                assert len(nodes) == len(node_radii)
                max_node_diameter = 2*max(node_radii)
        else:
            max_node_diameter = 0

        extra_space_for_style = max(max_stroke_width, max_node_diameter)
        xmin -= margin_size*dx + extra_space_for_style/2
        ymin -= margin_size*dy + extra_space_for_style/2
        dx += 2*margin_size*dx + extra_space_for_style
        dy += 2*margin_size*dy + extra_space_for_style
        viewbox = "%s %s %s %s" % (xmin, ymin, dx, dy)

        if mindim is None:
            szx = "{}{}".format(dx, baseunit)
            szy = "{}{}".format(dy, baseunit)
        else:
            if dx > dy:
                szx = str(mindim) + baseunit
                szy = str(int(ceil(mindim * dy / dx))) + baseunit
            else:
                szx = str(int(ceil(mindim * dx / dy))) + baseunit
                szy = str(mindim) + baseunit 
        dimensions = szx, szy

    # Create an SVG file
    if svg_attributes is not None:
        dimensions = (svg_attributes.get("width", dimensions[0]),
                      svg_attributes.get("height", dimensions[1]))
        debug = svg_attributes.get("debug", svgwrite_debug)
        dwg = Drawing(filename=filename, size=dimensions, debug=debug,
                      **svg_attributes)
    else:
        dwg = Drawing(filename=filename, size=dimensions, debug=svgwrite_debug,
                      viewBox=viewbox)

    # add paths
    if paths:
        for i, p in enumerate(paths):
            if isinstance(p, Path):
                ps = p.d()
            elif is_path_segment(p):
                ps = Path(p).d()
            else:  # assume this path, p, was input as a Path d-string
                ps = p

            if attributes:
                good_attribs = {'d': ps}
                for key in attributes[i]:
                    val = attributes[i][key]
                    if key != 'd':
                        try:
                            dwg.path(ps, **{key: val})
                            good_attribs.update({key: val})
                        except Exception as e:
                            warn(str(e))

                dwg.add(dwg.path(**good_attribs))
            else:
                dwg.add(dwg.path(ps, stroke=colors[i],
                                 stroke_width=str(stroke_widths[i]),
                                 fill='none'))

    # add nodes (filled in circles)
    if nodes:
        for i_pt, pt in enumerate([(z.real, z.imag) for z in nodes]):
            dwg.add(dwg.circle(pt, node_radii[i_pt], fill=node_colors[i_pt]))

    # add texts
    if text:
        assert isinstance(text, str) or (isinstance(text, list) and
                                         isinstance(text_path, list) and
                                         len(text_path) == len(text))
        if isinstance(text, str):
            text = [text]
            if not font_size:
                font_size = [_default_font_size]
            if not text_path:
                pos = complex(xmin + margin_size*dx, ymin + margin_size*dy)
                text_path = [Line(pos, pos + 1).d()]
        else:
            if font_size:
                if isinstance(font_size, list):
                    assert len(font_size) == len(text)
                else:
                    font_size = [font_size] * len(text)
            else:
                font_size = [_default_font_size] * len(text)
        for idx, s in enumerate(text):
            p = text_path[idx]
            if isinstance(p, Path):
                ps = p.d()
            elif is_path_segment(p):
                ps = Path(p).d()
            else:  # assume this path, p, was input as a Path d-string
                ps = p

            # paragraph = dwg.add(dwg.g(font_size=font_size[idx]))
            # paragraph.add(dwg.textPath(ps, s))
            pathid = 'tp' + str(idx)
            dwg.defs.add(dwg.path(d=ps, id=pathid))
            txter = dwg.add(dwg.text('', font_size=font_size[idx]))
            txter.add(txt.TextPath('#'+pathid, s))

    if paths2Drawing:
        return dwg
      
    dwg.save()

    # re-open the svg, make the xml pretty, and save it again
    xmlstring = md_xml_parse(filename).toprettyxml()
    with open(filename, 'w') as f:
        f.write(xmlstring)

    # try to open in web browser
    if openinbrowser:
        try:
            open_in_browser(filename)
        except:
            print("Failed to open output SVG in browser.  SVG saved to:")
            print(filename)


def wsvg(paths=None, colors=None, filename=None, stroke_widths=None,
         nodes=None, node_colors=None, node_radii=None,
         openinbrowser=False, timestamp=False, margin_size=0.1,
         mindim=600, dimensions=None, viewbox=None, text=None,
         text_path=None, font_size=None, attributes=None,
         svg_attributes=None, svgwrite_debug=False,
         paths2Drawing=False, baseunit='px'):
    """Create SVG and write to disk.

    Note: This is identical to `disvg()` except that `openinbrowser`
    is false by default and an assertion error is raised if `filename
    is None`.

    See `disvg()` docstring for more info.
    """
    assert filename is not None
    return disvg(paths, colors=colors, filename=filename,
                 stroke_widths=stroke_widths, nodes=nodes,
                 node_colors=node_colors, node_radii=node_radii,
                 openinbrowser=openinbrowser, timestamp=timestamp,
                 margin_size=margin_size, mindim=mindim,
                 dimensions=dimensions, viewbox=viewbox, text=text,
                 text_path=text_path, font_size=font_size,
                 attributes=attributes, svg_attributes=svg_attributes,
                 svgwrite_debug=svgwrite_debug,
                 paths2Drawing=paths2Drawing, baseunit=baseunit)
    
    
def paths2Drawing(paths=None, colors=None, filename=None,
                  stroke_widths=None, nodes=None, node_colors=None,
                  node_radii=None, openinbrowser=False, timestamp=False,
                  margin_size=0.1, mindim=600, dimensions=None,
                  viewbox=None, text=None, text_path=None,
                  font_size=None, attributes=None, svg_attributes=None,
                  svgwrite_debug=False, paths2Drawing=True, baseunit='px'):
    """Create and return `svg.Drawing` object.

    Note: This is identical to `disvg()` except that `paths2Drawing`
    is true by default and an assertion error is raised if `filename
    is None`.

    See `disvg()` docstring for more info.
    """
    return disvg(paths, colors=colors, filename=filename, 
                 stroke_widths=stroke_widths, nodes=nodes,
                 node_colors=node_colors, node_radii=node_radii,
                 openinbrowser=openinbrowser, timestamp=timestamp,
                 margin_size=margin_size, mindim=mindim,
                 dimensions=dimensions, viewbox=viewbox, text=text,
                 text_path=text_path, font_size=font_size,
                 attributes=attributes, svg_attributes=svg_attributes,
                 svgwrite_debug=svgwrite_debug,
                 paths2Drawing=paths2Drawing, baseunit=baseunit)
