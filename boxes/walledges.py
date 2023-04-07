from __future__ import annotations
import math
from typing import Any

from boxes import Boxes, edges
from .edges import Settings, BaseEdge


class _WallMountedBox(Boxes):
    ui_group = "WallMounted"

    def __init__(self) -> None:
        super().__init__()
        self.addWallSettingsArgs()

    def addWallSettingsArgs(self):
        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(WallSettings)
        self.addSettingsArgs(SlatWallSettings)
        self.addSettingsArgs(DinRailSettings)
        self.addSettingsArgs(FrenchCleatSettings)
        self.argparser.add_argument(
            "--walltype",  action="store", type=str, default="plain",
            choices=["plain", "plain reinforced", "slatwall", "dinrail",
                     "french cleat"],
            help="Type of wall system to attach to")

    def generateWallEdges(self):
        if self.walltype.startswith("plain"):
            s = WallSettings(
                self.thickness, True,
                **self.edgesettings.get("Wall", {}))
        elif self.walltype == "slatwall":
            s = SlatWallSettings(
                self.thickness, True,
                **self.edgesettings.get("SlatWall", {}))
        elif self.walltype == "dinrail":
            s = DinRailSettings(
                self.thickness, True,
                **self.edgesettings.get("DinRail", {}))
        elif self.walltype == "french cleat":
            s = FrenchCleatSettings(
                self.thickness, True,
                **self.edgesettings.get("FrenchCleat", {}))

        s.edgeObjects(self)
        self.wallHolesAt = self.edges["|"]
        if self.walltype.endswith("reinforced"):
            self.edges["c"] = self.edges["d"]
            self.edges["C"] = self.edges["D"]

#############################################################################
####     Straight Edge / Base class
#############################################################################

class WallEdge(BaseEdge):

    _reversed = False

    def lengths(self, length):
        return [length]

    def _joint(self, length):
        self.edge(length)

    def _section(self, nr, length):
        self.edge(length)

    def __call__(self, length, **kw):
        lengths = list(enumerate(self.lengths(length)))
        if self._reversed:
            lengths = list(reversed(lengths))

        for nr, l in lengths:
            if l == 0.0:
                continue
            if nr % 2:
                self._section(nr // 2, l)
            else:
                self._joint(l)

class WallJoinedEdge(WallEdge):
    char = "b"

    def _joint(self, length):
        t = self.settings.thickness
        self.step(-t)
        self.edges["f"](length)
        self.step(t)

    def startwidth(self) -> float:
        return self.settings.thickness

class WallBackEdge(WallEdge):

    def _section(self, nr, length):
        self.edge(length)

    def _joint(self, length):
        t = self.settings.thickness
        self.step(t)
        self.edges["F"](length)
        self.step(-t)

    def margin(self) -> float:
        return self.settings.thickness

class WallHoles(WallEdge):

    def _section(self, nr, length):
        self.rectangularHole(length/2, 0, length, self.settings.thickness)
        self.moveTo(length, 0)

    def _joint(self, length):
        self.fingerHolesAt(0, 0, length, 0)
        self.moveTo(length, 0)

    def __call__(self, x, y, length, angle, **kw):
        """
        Draw holes for a matching WallJoinedEdge

        :param x: position
        :param y: position
        :param length: length of matching edge
        :param angle:  (Default value = 90)
        """
        with self.boxes.saved_context():
            self.boxes.moveTo(x, y, angle)
            b = self.boxes.burn
            t = self.settings.thickness

            if self.boxes.debug: # XXX
                width = self.settings.thickness
                self.ctx.rectangle(b, -width / 2 + b,
                                   length - 2 * b, width - 2 * b)

            self.boxes.moveTo(length, 0, 180)
            super().__call__(length)

class WallHoleEdge(WallHoles):
    """Edge with holes for a parallel finger joint"""
    description = "Edge (parallel slot wall Holes)"

    def __init__(self, boxes, wallHoles, **kw) -> None:
        super().__init__(boxes, wallHoles.settings, **kw)
        self.wallHoles = wallHoles

    def __call__(self, length, bedBolts=None, bedBoltSettings=None, **kw):
        dist = self.wallHoles.settings.edge_width + self.settings.thickness / 2
        with self.saved_context():
            px, angle = (0, 0) if self._reversed else (length, 180)
            self.wallHoles(
                px, dist, length, angle)
        self.edge(length, tabs=2)

    def startwidth(self) -> float:
        """ """
        return self.wallHoles.settings.edge_width + self.settings.thickness

    def margin(self) -> float:
        return 0.0

class WallSettings(Settings):
    """Settings for plain WallEdges
Values:

* relative (in multiples of thickness)

 * edge_width : 1.0 : space below holes of FingerHoleEdge (multiples of thickness)

"""

    absolute_params: dict[str, Any] = {
    }

    relative_params = {
        "edge_width": 1.0,
    }

    base_class = WallEdge

    def edgeObjects(self, boxes, chars="aAbBcCdD|", add=True):
        bc = self.base_class
        bn = bc.__name__
        wallholes = type(bn+"Hole", (WallHoles, bc), {})(boxes, self)

        edges = [bc(boxes, self),
                 type(bn+"Reversed", (bc,), {'_reversed' : True})(boxes, self),
                 type(bn+"Joined", (WallJoinedEdge, bc), {})(boxes, self),
                 type(bn+"JoinedReversed", (WallJoinedEdge, bc), {'_reversed' : True})(boxes, self),
                 type(bn+"Back", (WallBackEdge, bc), {})(boxes, self),
                 type(bn+"BackReversed", (WallBackEdge, bc), {'_reversed' : True})(boxes, self),
                 type(bn+"Hole", (WallHoleEdge, bc), {})(boxes, wallholes),
                 type(bn+"HoleReversed", (WallHoleEdge, bc), {'_reversed' : True})(boxes, wallholes),
                 wallholes,
        ]
        return self._edgeObjects(edges, boxes, chars, add)

#############################################################################
####     Slat wall
#############################################################################


class SlatWallEdge(WallEdge):

    def lengths(self, length):
        pitch = self.settings.pitch
        h = self.settings.hook_height
        he = self.settings.hook_extra_height

        lengths = []
        if length < h + he:
            return [length]
        lengths = [0, h + he]
        length -= h + he
        if length > pitch:
            lengths.extend([(length // pitch) * pitch - h - 2 - 2*he,
                            h + 2 + 2*he,
                            length % pitch])
        else:
            lengths.append(length)
        return lengths

    def _section(self, nr, length):
        w = self.settings.hook_height # vertical width of hook
        hd = self.settings.hook_depth
        hdist = self.settings.hook_distance
        hh = self.settings.hook_overall_height
        ro = w # outer radius
        ri = min(w/2, hd/2) # inner radius
        rt = min(1, hd/2) # top radius
        slot = self.settings.hook_height + 2 # XXX
        if nr == 0:
            poly = [0, -90, hdist-ri, (-90, ri), hh-ri-w-rt, (90, rt),
                    hd-2*rt, (90, rt), hh-ro-rt, (90, ro), hdist+hd-ro, -90,
                    length-6]
        elif nr == 1:
            if self.settings.bottom_hook == "spring":
                r_plug = slot*.4
                slotslot = slot - r_plug * 2**0.5
                poly = [self.settings.hook_extra_height, -90,
                        5.0, -45, 0, (135, r_plug),
                        0, 90, 10, -90, slotslot, -90, 10, 90, 0,
                        (135, r_plug), 0, -45, 5, -90,
                        self.settings.hook_extra_height]
            elif self.settings.bottom_hook == "hook":
                d = 2
                poly = [self.settings.hook_extra_height + d - 1, -90,
                        4.5+hd, (90,1), slot-2, (90, 1), hd-1, 90, d,
                        -90, 5.5, -90, self.settings.hook_extra_height + 1]
            elif self.settings.bottom_hook == "stud":
                poly = [self.settings.hook_extra_height, -90,
                        6, (90, 1) , slot-2, (90, 1), 6, -90,
                        self.settings.hook_extra_height]
            else:
                poly = [2*self.settings.hook_extra_height + slot]

        if self._reversed:
            poly = reversed(poly)
        self.polyline(*poly)

    def margin(self) -> float:
        return self.settings.hook_depth + self.settings.hook_distance

class SlatWallSettings(WallSettings):
    """Settings for SlatWallEdges
Values:

* absolute_params

 * bottom_hook : "hook" : "spring", "stud" or "none"
 * pitch : 101.6 : vertical spacing of slots middle to middle (in mm)
 * hook_depth : 4.0 : horizontal width of the hook
 * hook_distance : 5.5 : horizontal space to the hook
 * hook_height : 6.0 : height of the horizontal bar of the hook
 * hook_overall_height : 12.0 : height of the hook top to bottom

* relative (in multiples of thickness)

 * hook_extra_height : 2.0 : space surrounding connectors (multiples of thickness)
 * edge_width : 1.0 : space below holes of FingerHoleEdge (multiples of thickness)

"""

    absolute_params = {
        "bottom_hook" : ("hook", "spring", "stud", "none"),
        "pitch" : 101.6,
        "hook_depth" : 4.0,
        "hook_distance" : 5.5,
        "hook_height" : 6.0,
        "hook_overall_height" : 12.0,
    }

    relative_params = {
        "hook_extra_height" : 2.0,
        "edge_width": 1.0,
    }

    base_class = SlatWallEdge


#############################################################################
####     DIN rail
#############################################################################

class DinRailEdge(WallEdge):

    def lengths(self, length):
        if length < 20:
            return [length]
        if length > 50 and self.settings.bottom == "stud":
            return [0, 20, length - 40, 20]
        return [0, 20,
                length - 20]

    def _section(self, nr, length):
        d = self.settings.depth

        if nr == 0:
            r = 1.
            poly = [0, -90, d-0.5-r, (90, r), 15+3-2*r, (90, r),
                    d-4-r, 45,
                    4*2**.5, -45, .5, -90, 6]
        elif nr == 1:
            slot = 20
            if self.settings.bottom == "stud":
                r = 1.
                poly = [0, -90, 7.5-r, (90, r),
                        slot - 2*r,
                        (90, r), 7.5-r, -90, 0]
            else:
                poly = [slot]
        if self._reversed:
            poly = reversed(poly)
        self.polyline(*poly)

    def margin(self) -> float:
        return self.settings.depth

class DinRailSettings(WallSettings):
    """Settings for DinRailEdges
Values:

* absolute_params

 * bottom : "stud" : "stud" or "none"
 * depth : 4.0 : horizontal width of the hook

* relative (in multiples of thickness)

 * edge_width : 1.0 : space below holes of FingerHoleEdge (multiples of thickness)

"""

    absolute_params = {
        "bottom" : ("stud", "none"),
        "depth" : 8.0,
    }

    relative_params = {
        "edge_width": 1.0,
    }

    base_class = DinRailEdge

#############################################################################
####     French Cleats
#############################################################################

class FrenchCleatEdge(WallEdge):

    def lengths(self, length):
        d = self.settings.depth
        t = self.settings.thickness
        s = self.settings.spacing
        h = d * math.tan(math.radians(self.settings.angle))
        # make small enough to not have finger holes
        top = 0.5*t
        bottom = 0.5 * t
        if length < top + bottom + 1.5*d + h:
            return [length]
        if length > top + bottom + 2*t + 1.5*d + h and \
           self.settings.bottom == "stud":
            return [top, 1.5*d + h, length - top - bottom - 2.5*d - h,
                    d, bottom]
        if length > top + bottom + 2.5*d + s and \
           self.settings.bottom == "hook":
            dist = ((length - top - t - 1.5*d - h) // s ) * s - 1.5*d - h
            return [top, 1.5*d + h, dist, 1.5*d + h, length-dist-top-3*d-2*h]
        return [top, 2.5*d, length-top-2.5*d]

    def _section(self, nr, length):
        d = self.settings.depth
        t = self.settings.thickness
        r = min(0.5*t, 0.1*d)
        a = self.settings.angle
        h = d * math.tan(math.radians(a))
        l = d / math.cos(math.radians(a))

        if nr == 0 or self.settings.bottom == "hook":
            poly = [0, -90, 0, (90, d), .5*d+h, 90+a, l, -90-a, length-1.5*d]
        elif nr == 1:
            if self.settings.bottom == "stud":
                r = min(t, length/4, d)
                poly = [0, -90, d-r, (90, r),
                        length - 2*r,
                        (90, r), d-r, -90, 0]
            else:
                poly = [length]
        if self._reversed:
            poly = reversed(poly)
        self.polyline(*poly)

    def margin(self) -> float:
        return self.settings.depth

class FrenchCleatSettings(WallSettings):
    """Settings for FrenchCleatEdges
Values:

* absolute_params

 * bottom : "stud" : "stud", "hook" or "none"
 * depth : 18.0 : horizontal width of the hook in mm
 * angle : 45.0 : angle of the cut (0 for horizontal)
 * spacing : 200.0 : distance of the cleats in mm (for bottom hook)

* relative (in multiples of thickness)

 * edge_width : 1.0 : space below holes of FingerHoleEdge (multiples of thickness)

"""

    absolute_params = {
        "bottom" : ("stud", "hook", "none"),
        "depth" : 18.0,
        "spacing" : 200.0,
        "angle" : 45.0,
    }

    relative_params = {
        "edge_width": 1.0,
    }

    base_class = FrenchCleatEdge
