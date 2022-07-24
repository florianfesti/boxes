from .edges import Settings, BaseEdge
from boxes import Boxes, edges

class _WallMountedBox(Boxes):
    ui_group = "WallMounted"

    def __init__(self):
        super().__init__()
        self.addWallSettingsArgs()

    def addWallSettingsArgs(self):
        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(WallSettings)
        self.addSettingsArgs(SlatWallSettings)
        self.addSettingsArgs(DinRailSettings)
        self.argparser.add_argument(
            "--walltype",  action="store", type=str, default="plain",
            choices=["plain", "plain reenforced", "slatwall", "dinrail"],
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

        s.edgeObjects(self)
        self.wallHolesAt = self.edges["|"]
        if self.walltype.endswith("reenforced"):
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

    def startwidth(self):
        return self.settings.thickness

class WallBackEdge(WallEdge):

    def _section(self, nr, length):
        self.edge(length)

    def _joint(self, length):
        t = self.settings.thickness
        self.step(t)
        self.edges["F"](length)
        self.step(-t)

    def margin(self):
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

    def __init__(self, boxes, wallHoles, **kw):
        super().__init__(boxes, wallHoles.settings, **kw)
        self.wallHoles = wallHoles

    def __call__(self, length, bedBolts=None, bedBoltSettings=None, **kw):
        dist = self.wallHoles.settings.edge_width + self.settings.thickness / 2
        with self.saved_context():
            px, angle = (0, 0) if self._reversed else (length, 180)
            self.wallHoles(
                px, dist, length, angle)
        self.edge(length, tabs=2)

    def startwidth(self):
        """ """
        return self.wallHoles.settings.edge_width + self.settings.thickness

    def margin(self):
        return 0.0
        
class WallSettings(Settings):

    """Settings for plain WallEdges
Values:

* relative (in multiples of thickness)

 * edge_width : 1.0 : space below holes of FingerHoleEdge (multiples of thickness)

"""

    absolute_params = {
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
        he = self.settings.hook_extra_height

        lengths = []
        if length < 6 + he:
            return [length]
        lengths = [0, 6 + he]
        length -= 6 + he
        if length > pitch:
            lengths.extend([(length // pitch) * pitch - 8 - 2*he,
                            8 + 2*he,
                            length % pitch])
        else:
            lengths.append(length)
        return lengths

    def _section(self, nr, length):
        w = 6 # vertical width of hook
        hd = self.settings.hook_depth
        ro = 6 # outer radius
        ri = 2 # inner radius
        rt = min(1, hd/2) # top radius
        slot = 8
        if nr == 0:
            poly = [0, -90, 5.5-ri, (-90, ri), 12-ri-w-rt, (90, rt),
                    hd-2*rt, (90, rt), 12-ro-rt, (90, ro), 5.5+hd-ro, -90,
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

    def margin(self):
        return 6+5.5

class SlatWallSettings(WallSettings):

    """Settings for SlatWallEdges
Values:

* absolute_params

 * bottom_hook : "hook" : "spring", "stud" or "none"
 * pitch : 101.6 : vertical spacing of slots middle to middle (in mm)
 * hook_depth : 4.0 : horizontal width of the hook

* relative (in multiples of thickness)

 * hook_extra_height : 2.0 : space surrounding connectors (multiples of thickness)
 * edge_width : 1.0 : space below holes of FingerHoleEdge (multiples of thickness)

"""

    absolute_params = {
        "bottom_hook" : ("hook", "spring", "stud", "none"),
        "pitch" : 101.6,
        "hook_depth" : 4.0,
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

    def margin(self):
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
