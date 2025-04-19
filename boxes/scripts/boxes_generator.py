#!/usr/bin/env python3
# Copyright (C) 2025 Michael Ihde
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This application is designed to support automation of cataloging of boxes
by allowing a user to define one our more yaml files that list the boxes
they want cut.

This will then generate all of the boxes and merge them into a single SVG
with the pieces of the box being packed into one or more panels
(set panel_width and panel_height to zero to disable merging).

The merged output is very useful when cutting many different boxes and using
standard 12" x 12" (i.e. ~305mm x 305mm) panels.  The merged output makes
heavy use of SVG transforms, so some tools may not render them correctly.  This
tool has been tested with LightBurn.

The YAML input looks like this:

```
Defaults:
    reference: 0

Boxes:
    -   box_type: GridfinityTrayLayout # required
        name: "1x3x6u_tray" # optional
        count: 2 # optional, 1 is default
        generate: false # optional, true is default
        args: # the args for the box generator
            h: 6u
            nx: 1
            ny: 3
            countx: 1
            county:  1
            gen_pads: 0

    -   box_type: GridfinityTrayLayout # required
        name: "2x3x6u_tray" # optional
        count: 2 # optional, 1 is default
        args: # the args for the box generator
            h: 6u
            nx: 2
            ny: 3
            countx: 1
            county:  1
            gen_pads: 0
```

Boxes the require a layout can use the following choices:

```
layout: GENERATE # auto generate a layout

layout: path/to/file.txt

layout: |
        ,> 125.25mm
    +-+
    | |  83.25mm
    +-+
```

Currently there is no web front-end for this script.
"""
import yaml
import copy
import os
import sys
import logging
import argparse
import sys
import uuid
import os
import re

import xml.etree.ElementTree as ET
import rectpack
from rectpack import newPacker, PackingBin
from svgpathtools import parse_path

try:
    import boxes.generators
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../.."))
    import boxes.generators
import boxes

class ArgumentParserError(Exception): pass

class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)

# Evil hack
boxes.ArgumentParser = ThrowingArgumentParser  # type: ignore

PACK_ALGO_CHOICES = (
    "MaxRectsBl",
    "MaxRectsBssf",
    "MaxRectsBaf",
    "MaxRectsBlsf",
    "SkylineBl",
    "SkylineBlWm",
    "SkylineMwf",
    "SkylineMwfl",
    "SkylineMwfWm",
    "SkylineMwflWm",
    "GuillotineBssfSas",
    "GuillotineBssfLas",
    "GuillotineBssfSlas",
    "GuillotineBssfLlas",
    "GuillotineBssfMaxas",
    "GuillotineBssfMinas",
    "GuillotineBlsfSas",
    "GuillotineBlsfLas",
    "GuillotineBlsfSlas",
    "GuillotineBlsfLlas",
    "GuillotineBlsfMaxas",
    "GuillotineBlsfMinas",
    "GuillotineBafSas",
    "GuillotineBafLas",
    "GuillotineBafSlas",
    "GuillotineBafLlas",
    "GuillotineBafMaxas",
    "GuillotineBafMinas",
)

GENERATORS = {b.__name__: b for b in boxes.generators.getAllBoxGenerators().values() if b.webinterface}

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

def generate_layout(box):
    """
    Generates a basic layout the evenly divides a box by box.countx and box.county.

    The boxes dimensions are determined by box.x and box.y (if present), or box.pitch,
    box.nx, and box.ny.
    """
    countx = getattr(box, 'countx', 1)
    county = getattr(box, 'county', 1)

    if hasattr(box, 'x') and hasattr(box, 'y'):
        x = box.x - getattr(box, "margin", 0)
        y = box.y - getattr(box, "margin", 0)
    elif hasattr(box, 'pitch') and hasattr(box, 'nx') and hasattr(box, 'ny'):
        x = box.nx * box.pitch - getattr(box, "margin", 0)
        y = box.ny * box.pitch - getattr(box, "margin", 0)
    else:
        raise ValueError

    layout = ''

    stepx = x / countx
    stepy = y / county
    for i in range(countx):
        line = ' |' * i + f" ,> {stepx}mm\n"
        layout += line
    for i in range(county):
        layout += "+-" * countx + f"+\n"
        layout += "| " * countx + f"|{stepy}mm\n"
    layout += "+-" * countx + "+\n"
    return layout

def generate(cut, output_prefix):
    """
    Generate a single box SVG
    """
    generated_files = []
    defaults = cut.get("Defaults", {})
    for ii, box_settings in enumerate(cut.get("Boxes", [])):
        # Allow for skipping generation
        if box_settings.get("generate") == False:
            continue

        # Get the box generator
        box_type = box_settings.pop("box_type", None)
        if box_type is None:
            raise ValueError("box_type must be provided for each cut")
        box_cls = GENERATORS.get(box_type, None)
        if box_cls is None:
            raise ValueError("invalid generator '%s'" % box_type)

        # Instantitate the box object
        box = box_cls()

        # Create the settings for the generator
        settings = copy.deepcopy(defaults)
        settings.update(box_settings.get("args", {}))

        if hasattr(box, "layout") and "layout" in settings:
            if os.path.exists(settings["layout"]):
                with open(settings["layout"]) as ff:
                    settings["layout"] = ff.read()
            else:
                box.layout = settings["layout"]

        box_args = []
        for kk, vv in settings.items():
            # Handle layout separately
            if kk == "layout":
                continue
            box_args.append(f"--{kk}={vv}")

        try:
            # Ignore unknown arguments by pre-parsing. This two stage
            # approach was performed to avoid modifying parseArgs and
            # changing it's behavior.  A long-term better solution
            # might be to allow parseArgs to take a 'strict' argument
            # the can enable/disable strict parsing of arguments
            args, argv = box.argparser.parse_known_args(box_args)
            if len(argv) > 0:
                for unknown_arg in argv:
                    box_args.remove(unknown_arg)
            box.parseArgs(box_args)
        except ArgumentParserError:
            logging.exception("Error parsing box args")
            continue

        # If the box requires a layout, support auto-generation
        if getattr(box, "layout", None) == "GENERATE":
            box.layout = generate_layout(box)

        # Render the box SVG
        box.open()
        box.render()
        data = box.close()

        if box_settings.get("name") is not None:
            output_base = os.path.basename(output_prefix)
            output_dir = os.path.dirname(output_prefix)
            output_file = os.path.join(output_dir, f"{output_base}_{box_settings['name']}_{box_type}_{ii}")
        else:
            output_file = f"{output_prefix}_{box_type}_{ii}"

        # Write the output
        if box_settings.get("count") is not None:
            for jj in range(int(box_settings.get("count"))):
                logging.info("Writing %s_%s.svg", output_file, jj)
                with open(f"{output_file}_{jj}.svg", "wb") as ff:
                    ff.write(data.read())
                    data.seek(0)
                generated_files.append(f"{output_file}_{jj}.svg")

        else:
            logging.info("Writing %s.svg", output_file)
            with open(f"{output_file}.svg", "wb") as ff:
                ff.write(data.read())
            generated_files.append(f"{output_file}.svg")

    return generated_files

def parse_svg_groups(svg_file):
    """
    Parse out all the SVG groups from the given SVG file
    """
    tree = ET.parse(svg_file)
    root = tree.getroot()
    groups = [g for g in root if g.tag.endswith('g')]
    return groups, tree

def get_bbox_of_group(group):
    """
    Get the bounding box of the SVG group
    """
    min_x = float("inf")
    min_y = float("inf")
    max_x = float("-inf")
    max_y = float("-inf")

    def update_bbox(x_vals, y_vals):
        nonlocal min_x, min_y, max_x, max_y
        min_x = min(min_x, *x_vals)
        min_y = min(min_y, *y_vals)
        max_x = max(max_x, *x_vals)
        max_y = max(max_y, *y_vals)

    for elem in group.iter():
        tag = elem.tag.split("}")[-1]  # Remove namespace
        if tag == "rect":
            x = float(elem.attrib.get("x", 0))
            y = float(elem.attrib.get("y", 0))
            w = float(elem.attrib.get("width", 0))
            h = float(elem.attrib.get("height", 0))
            update_bbox([x, x + w], [y, y + h])
        elif tag == "circle":
            cx = float(elem.attrib.get("cx", 0))
            cy = float(elem.attrib.get("cy", 0))
            r = float(elem.attrib.get("r", 0))
            update_bbox([cx - r, cx + r], [cy - r, cy + r])
        elif tag == "ellipse":
            cx = float(elem.attrib.get("cx", 0))
            cy = float(elem.attrib.get("cy", 0))
            rx = float(elem.attrib.get("rx", 0))
            ry = float(elem.attrib.get("ry", 0))
            update_bbox([cx - rx, cx + rx], [cy - ry, cy + ry])
        elif tag == "line":
            x1 = float(elem.attrib.get("x1", 0))
            y1 = float(elem.attrib.get("y1", 0))
            x2 = float(elem.attrib.get("x2", 0))
            y2 = float(elem.attrib.get("y2", 0))
            update_bbox([x1, x2], [y1, y2])
        elif tag in ["polyline", "polygon"]:
            points = elem.attrib.get("points", "")
            point_pairs = re.findall(r"[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?", points)
            coords = list(map(float, point_pairs))
            xs = coords[::2]
            ys = coords[1::2]
            if xs and ys:
                update_bbox(xs, ys)
        elif tag == "path":
            d = elem.attrib.get("d", "")
            try:
                path = parse_path(d)
                box = path.bbox()  # (min_x, max_x, min_y, max_y)
                update_bbox([box[0], box[1]], [box[2], box[3]])
            except Exception as e:
                print(f"Warning: Failed to parse path in group. Error: {e}")

    # Fallback if nothing was found
    if min_x == float("inf"):
        raise ValueError
    return [min_x, min_y, max_x, max_y]

def extract_elements(svg_files):
    """
    Extract all group elements from the SVG
    """
    elements = []
    for file in svg_files:
        groups, tree = parse_svg_groups(file)
        for g in groups:
            bbox = get_bbox_of_group(g)
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            style = g.attrib.get("style", '')
            elements.append({
                'group': g,
                'bbox': bbox,
                'width': width,
                'height': height,
                'style': style,
                'id': str(uuid.uuid4()),
                'source_file': file
            })
    return elements

def pack_elements(elements, box_width, box_height, margin, rotation, bin_algo, pack_algo):
    """
    Pack all the group elements into the minimum number of panels.
    """
    try:
        bin_algo = getattr(PackingBin, bin_algo)
    except AttributeError:
        raise RuntimeError("invalid bin algorithm specified")

    try:
        pack_algo = getattr(rectpack, pack_algo)
    except AttributeError:
        raise RuntimeError("invalid pack algorithm specified")

    packer = newPacker(
        rotation=rotation, # rotating packing is still a WIP
        pack_algo=pack_algo,
        bin_algo=bin_algo
    )
    for elem in elements:
        packer.add_rect(elem['width'] + (margin*2), elem['height'] + (margin*2), elem['id'])
    packer.add_bin(box_width, box_height, float("inf"))  # unlimited bins
    packer.pack()

    packed = []
    for bid, abin in enumerate(packer):
        for rect in abin:
            x, y, packed_w, packed_h, rid = rect.x, rect.y, rect.width, rect.height, rect.rid
            elem = next(e for e in elements if e['id'] == rid)

            original_w = elem['width'] + (margin*2)
            original_h = elem['height']+ (margin*2)
            rotated = (
                round(packed_w) == round(original_h) and round(packed_h) == round(original_w)
            )

            packed.append({
                'element': elem,
                'x': x,
                'y': y,
                'bin': bid,
                'style': elem['style'],
                'rotated': rotated
            })
    return packed

def create_output_svg(packed_elements, box_width, box_height, margin, include_debug_bbox=False):
    """
    Create the merged SVG output.
    """
    svg = ET.Element(f"{{{SVG_NS}}}svg")
    bins = {}
    spacing = 20  # Space between bins in the output SVG

    for item in packed_elements:
        bin_id = item['bin']
        if bin_id not in bins:
            # Create a new bin group
            bin_group = ET.SubElement(svg, "g", attrib={'id': f'bin_{bin_id}'})
            # Place each bin horizontally spaced apart
            bin_group.set("transform", f"translate({bin_id * (box_width + spacing)}, 0)")
            bins[bin_id] = bin_group

            # Add bounding box rectangle to bin
            rect = ET.Element("rect", {
                "x": "0",
                "y": "0",
                "width": str(box_width),
                "height": str(box_height),
                "fill": "none",
                "stroke": "rgb( 208, 208, 0)",
                "stroke-width": "1"
            })
            bin_group.append(rect)

        elem = item['element']
        g = elem['group']
        bbox = elem['bbox']
        original_w = elem['width']
        original_h = elem['height']
        x, y = item['x'], item['y']
        rotated = item['rotated']
        style = item['style']

        # Normalize the group to (0, 0)
        dx = -bbox[0]
        dy = -bbox[1]

        # Create a new group and apply transforms in order:
        # 1. Move to (x, y) in the bin
        # 2. Rotate if needed
        # 3. Offset to normalize original group position

        transform_parts = []

        # Step 1: move to packed (x, y)
        transform_parts.append(f"translate({x+margin},{y+margin})")

        if rotated:
            dy -= original_h
            # Step 2: rotate 90° around the origin
            transform_parts.append("rotate(90)")
            # Step 3: apply offset to align rotated group
            transform_parts.append(f"translate({dx}, {dy})")
        else:
            # Step 3: apply offset without rotation
            transform_parts.append(f"translate({dx},{dy})")

        full_transform = " ".join(transform_parts)

        # Clone the group with transformation
        new_g = ET.Element("g", attrib={"transform": full_transform, "style": style})
        for child in list(g):
            new_g.append(child)

        if include_debug_bbox:
            new_g.append(
                ET.Element(
                    "rect",
                    attrib={
                        "x": str(bbox[0]),
                        "y": str(bbox[1]),
                        "width": str(original_w),
                        "height": str(original_h),
                        "stroke": "rgb(255,128,0)",
                        "fill": "none",
                    }
                )
            )
        bins[bin_id].append(new_g)


    return ET.ElementTree(svg)

def main(args):
    generated_files = set()
    for cut_file in args.cuts:
        output_prefix = args.prefix
        if output_prefix is None:
            output_prefix = os.path.splitext(cut_file)[0]

        with open(cut_file) as ff:
            cut = yaml.safe_load(ff)
            generated_files.update( generate(cut, output_prefix) )

    # convert width/height in mm to pixels
    if args.panel_width > 0 and args.panel_height > 0 and args.merge:
        width_px = int( (args.panel_width / 25.4) * 96)
        height_px = int( (args.panel_height / 25.4) * 96)
        margin_px = int( (args.margin / 25.4) * 96)

        logging.info("Merging %s files", len(generated_files))
        elements = extract_elements(list(generated_files))
        for element in elements:
            if element['width'] > args.panel_width or element['height'] > args.panel_height:
                logging.warning("Element in %s is larger than panel width and will not be included in merged output", element['source_file'])
        packed = pack_elements(
            elements,
            args.panel_width,
            args.panel_height,
            margin_px,
            args.rotation,
            args.bin_algo,
            args.pack_algo
        )
        result_svg = create_output_svg(
            packed,
            args.panel_width,
            args.panel_height,
            margin_px,
            args.debug
        )

        output_file = f"{output_prefix}_{args.output}"
        result_svg.write(output_file, encoding='utf-8', xml_declaration=True)
        logging.info("Merge output %s", output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("cuts", nargs="+", help="Input cut files")
    parser.add_argument("--prefix", type=str, default=None)
    parser.add_argument("--debug", default=False, action="store_true")
    parser.add_argument("--rotation", default=False, action="store_true")
    parser.add_argument("--bin_algo", default="Global", choices=("BNF", "BFF", "BBF", "Global"))
    parser.add_argument("--pack_algo", default="MaxRectsBssf", choices=PACK_ALGO_CHOICES)
    parser.add_argument("--panel_width", type=int, default=300, help="Panel width in mm")
    parser.add_argument("--panel_height", type=int, default=300, help="Panel height in mm")
    parser.add_argument("--dpi", type=int, default=96, help="SVG resolution in dots-per-inch")
    parser.add_argument("--margin", type=int, default=1, help="margin around outside of element in mm")
    parser.add_argument("--output", default="merged_output.svg", help="Merged output SVG file suffix")
    parser.add_argument("--merge", default=False, action="store_true", help="Produce merged output")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    main(args)
