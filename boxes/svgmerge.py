import logging
import argparse
import uuid
import io
import re

import xml.etree.ElementTree as ET
import rectpack
from rectpack import newPacker, PackingBin
from svgpathtools import parse_path

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

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

class SvgMerge:
    def __init__(self):
        self.args = None
        self.non_default_args = {}
        self.output = None
        self.argparser = argparse.ArgumentParser()
        self.argparser.add_argument("cuts", nargs="+", help="Input cut files")
        self.argparser.add_argument("--rotation", default=False, action="store_true")
        self.argparser.add_argument("--debug-bbox", default=False, action="store_true")
        self.argparser.add_argument("--bin_algo", default="Global", choices=("BNF", "BFF", "BBF", "Global"))
        self.argparser.add_argument("--pack_algo", default="MaxRectsBssf", choices=PACK_ALGO_CHOICES)
        self.argparser.add_argument("--panel_width", type=int, default=300, help="Panel width in mm")
        self.argparser.add_argument("--panel_height", type=int, default=300, help="Panel height in mm")
        self.argparser.add_argument("--dpi", type=int, default=96, help="SVG resolution in dots-per-inch")
        self.argparser.add_argument("--margin", type=int, default=1, help="margin around outside of element in mm")
        self.argparser.add_argument("--output", type=str, default="merged.svg", help="name of resulting file")

    @staticmethod
    def parse_svg_groups(svg_file):
        """
        Parse out all the SVG groups from the given SVG file
        """
        tree = ET.parse(svg_file)
        root = tree.getroot()
        groups = [g for g in root if g.tag.endswith('g')]
        return groups, tree

    @staticmethod
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

    @staticmethod
    def extract_elements(svg_files):
        """
        Extract all group elements from the SVG
        """
        elements = []
        for file in svg_files:
            groups, tree = SvgMerge.parse_svg_groups(file)
            for g in groups:
                bbox = SvgMerge.get_bbox_of_group(g)
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

    @staticmethod
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

    @staticmethod
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

    def parseArgs(self, args):
        self.args = args
        for key, value in vars(self.argparser.parse_args(args=args)).items():
            default = self.argparser.get_default(key)

            # treat edge settings separately
            setattr(self, key, value)
            if value != default:
                self.non_default_args[key] = value

    def render(self, files):
        if self.args is None:
            raise RuntimeError("parseArgs must be called first")

        files = set(files)

        # convert width/height in mm to pixels
        if self.panel_width > 0 and self.panel_height > 0:
            width_px = int( (self.panel_width / 25.4) * 96)
            height_px = int( (self.panel_height / 25.4) * 96)
            margin_px = int( (self.margin / 25.4) * 96)

            logging.info("Merging %s files", len(files))
            elements = SvgMerge.extract_elements(list(files))
            for element in elements:
                if element['width'] > self.panel_width or element['height'] > self.panel_height:
                    logging.warning("Element in %s is larger than panel width and will not be included in merged output", element['source_file'])
            packed = SvgMerge.pack_elements(
                elements,
                self.panel_width,
                self.panel_height,
                margin_px,
                self.rotation,
                self.bin_algo,
                self.pack_algo
            )
            self.result_svg = SvgMerge.create_output_svg(
                packed,
                self.panel_width,
                self.panel_height,
                margin_px,
                self.debug_bbox
            )

    def close(self):
        result = io.BytesIO()
        self.result_svg.write(result, encoding='utf-8', xml_declaration=True)
        return result
