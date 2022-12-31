#!/usr/bin/env python3
""

'''
Copyright (C) 2007 Aaron Spike  (aaron @ ekips.org)
Copyright (C) 2007 Tavmjong Bah (tavmjong @ free.fr)
Copyright (C) http://cnc-club.ru/forum/viewtopic.php?f=33&t=434&p=2594#p2500
Copyright (C) 2014 Jürgen Weigert (juewei@fabmail.org)

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

2014-03-20 jw@suse.de 0.2  Option --accuracy=0 for automatic added.
2014-03-21                 sent upstream: https://bugs.launchpad.net/inkscape/+bug/1295641
2014-03-21 jw@suse.de 0.3  Fixed center of rotation for gears with odd number of teeth.
2014-04-04 juewei     0.7  Revamped calc_unit_factor(). 
2014-04-05 juewei    0.7a  Correctly positioned rack gear.
                       The geometry above the meshing line is wrong.
2014-04-06 juewei    0.7b  Undercut detection added. Reference:
               http://nptel.ac.in/courses/IIT-MADRAS/Machine_Design_II/pdf/2_2.pdf
               Manually merged https://github.com/jnweiger/inkscape-gears-dev/pull/15
2014-04-07 juewei    0.7c  Manually merged https://github.com/jnweiger/inkscape-gears-dev/pull/17
2014-04-09 juewei    0.8   Fixed https://github.com/jnweiger/inkscape-gears-dev/issues/19
			   Ring gears are ready for production now. Thanks neon22 for driving this.
			   Profile shift implemented (Advanced Tab), fixing 
			   https://github.com/jnweiger/inkscape-gears-dev/issues/9
2015-05-29 juewei 0.9 	ported to inkscape 0.91
			AttributeError: 'module' object inkex has no attribute 'uutounit
			Fixed https://github.com/jnweiger/inkscape-gears-dev
'''

from math import pi, cos, sin, tan, radians, degrees, ceil, asin, acos, sqrt
from os import devnull  # for debugging

two_pi = 2 * pi
import argparse
from boxes.vectors import kerf, vdiff, vlength

__version__ = '0.9'

def linspace(a,b,n):
    """ return list of linear interp of a to b in n steps
        - if a and b are ints - you'll get an int result.
        - n must be an integer
    """
    return [a+x*(b-a)/(n-1) for x in range(0,n)]

def involute_intersect_angle(Rb, R):
    " "
    Rb, R = float(Rb), float(R)
    return (sqrt(R**2 - Rb**2) / (Rb)) - (acos(Rb / R))

def point_on_circle(radius, angle):
    " return xy coord of the point at distance radius from origin at angle "
    x = radius * cos(angle)
    y = radius * sin(angle)
    return (x, y)

### Undercut support functions
def undercut_min_teeth(pitch_angle, k=1.0):
    """
    computes the minimum tooth count for a
    spur gear so that no undercut with the given pitch_angle (in deg)
    and an addendum = k * metric_module, where 0 < k < 1

    Note:
    The return value should be rounded upwards for perfect safety. E.g.
    min_teeth = int(math.ceil(undercut_min_teeth(20.0)))    # 18, not 17
    """
    x = max(sin(radians(pitch_angle)), 0.01)
    return 2*k /(x*x)

def undercut_max_k(teeth, pitch_angle=20.0):
    """ computes the maximum k value for a given teeth count and pitch_angle
        so that no undercut occurs.
    """
    x = max(sin(radians(pitch_angle)), 0.01)
    return 0.5 * teeth * x * x

def undercut_min_angle(teeth, k=1.0):
    """ computes the minimum pitch angle, to that the given teeth count (and
        profile shift) cause no undercut.
    """
    return degrees(asin(min(0.856, sqrt(2.0*k/teeth))))    # max 59.9 deg


def have_undercut(teeth, pitch_angle=20.0, k=1.0):
    """ returns true if the specified number of teeth would
        cause an undercut.
    """
    return (teeth < undercut_min_teeth(pitch_angle, k))


## gather all basic gear calculations in one place
def gear_calculations(num_teeth, circular_pitch, pressure_angle, clearance=0, ring_gear=False, profile_shift=0.):
    """ Put base calcs for spur/ring gears in one place.
        - negative profile shifting helps against undercut. 
    """
    diametral_pitch = pi / circular_pitch
    pitch_diameter = num_teeth / diametral_pitch
    pitch_radius = pitch_diameter / 2.0
    addendum = 1 / diametral_pitch
    dedendum = addendum
    dedendum *= 1+profile_shift
    addendum *= 1-profile_shift

    if ring_gear:
        addendum = addendum + clearance # our method
    else:
        dedendum = dedendum + clearance # our method

    base_radius = pitch_diameter * cos(radians(pressure_angle)) / 2.0
    outer_radius = pitch_radius + addendum
    root_radius =  pitch_radius - dedendum

    # Tooth thickness: Tooth width along pitch circle.
    tooth_thickness  = ( pi * pitch_diameter ) / ( 2.0 * num_teeth )

    return (pitch_radius, base_radius,
            addendum, dedendum, outer_radius, root_radius,
            tooth_thickness
            )


def generate_rack_points(tooth_count, pitch, addendum, pressure_angle,
                       base_height, tab_length, clearance=0, draw_guides=False):
    """ Return path (suitable for svg) of the Rack gear.
        - rack gear uses straight sides

            - involute on a circle of infinite radius is a simple linear ramp

        - the meshing circle touches at y = 0, 
        - the highest elevation of the teeth is at y = +addendum
        - the lowest elevation of the teeth is at y = -addendum-clearance
        - the base_height extends downwards from the lowest elevation.
        - we generate this middle tooth exactly centered on the y=0 line.
          (one extra tooth on the right hand side, if number of teeth is even)
    """
    spacing = 0.5 * pitch # rolling one pitch distance on the spur gear pitch_diameter.

    # roughly center rack in drawing, exact position is so that it meshes
    # nicely with the spur gear.
    # -0.5*spacing has a gap in the center.
    # +0.5*spacing has a tooth in the center.

    if tab_length <= 0.0:
        tab_length = 1E-8

    tas  = tan(radians(pressure_angle)) * addendum
    tasc = tan(radians(pressure_angle)) * (addendum+clearance)
    base_top = addendum+clearance
    base_bot = addendum+clearance+base_height

    x_lhs = -pitch * 0.5*tooth_count - tab_length
    # Start with base tab on LHS
    points = [] # make list of points
    points.append((x_lhs, base_bot))
    points.append((x_lhs, base_top))
    x = x_lhs + tab_length+tasc

    # An involute on a circle of infinite radius is a simple linear ramp.
    # We need to add curve at bottom and use clearance.
    for i in range(tooth_count):
        # move along path, generating the next 'tooth'
        # pitch line is at y=0. the left edge hits the pitch line at x
        points.append((x-tasc, base_top))
        points.append((x+tas, -addendum))
        points.append((x+spacing-tas, -addendum))
        points.append((x+spacing+tasc, base_top)) 
        x += pitch

    # add base on RHS
    x_rhs = x - tasc + tab_length
    points.append((x_rhs, base_top))
    points.append((x_rhs, base_bot))
    # We don't close the path here. Caller does it.
    # points.append((x_lhs, base_bot))

    # Draw line representing the pitch circle of infinite diameter
    guide_path = None
    p = []
    if draw_guides:
        p.append( (x_lhs + 0.5 * tab_length, 0) )
        p.append( (x_rhs - 0.5 * tab_length, 0) )

    return (points, p)


def generate_spur_points(teeth, base_radius, pitch_radius, outer_radius, root_radius, accuracy_involute, accuracy_circular):
    """ given a set of core gear params
        - generate the svg path for the gear
    """
    half_thick_angle = two_pi / (4.0 * teeth ) #?? = pi / (2.0 * teeth)
    pitch_to_base_angle  = involute_intersect_angle( base_radius, pitch_radius )
    pitch_to_outer_angle = involute_intersect_angle( base_radius, outer_radius ) - pitch_to_base_angle

    start_involute_radius = max(base_radius, root_radius)
    radii = linspace(start_involute_radius, outer_radius, accuracy_involute)
    angles = [involute_intersect_angle(base_radius, r) for r in radii]

    centers = [(x * two_pi / float( teeth) ) for x in range( teeth ) ]
    points = []

    for c in centers:
    # Angles
        pitch1 = c - half_thick_angle
        base1  = pitch1 - pitch_to_base_angle
        offsetangles1 = [ base1 + x for x in angles]
        points1 = [ point_on_circle( radii[i], offsetangles1[i]) for i in range(0,len(radii)) ]

        pitch2 = c + half_thick_angle
        base2  = pitch2 + pitch_to_base_angle
        offsetangles2 = [ base2 - x for x in angles] 
        points2 = [ point_on_circle( radii[i], offsetangles2[i]) for i in range(0,len(radii)) ]

        points_on_outer_radius = [ point_on_circle(outer_radius, x) for x in linspace(offsetangles1[-1], offsetangles2[-1], accuracy_circular) ]

        if root_radius > base_radius:
            pitch_to_root_angle = pitch_to_base_angle - involute_intersect_angle(base_radius, root_radius )
            root1 = pitch1 - pitch_to_root_angle
            root2 = pitch2 + pitch_to_root_angle
            points_on_root = [point_on_circle (root_radius, x) for x in linspace(root2, root1+(two_pi/float(teeth)), accuracy_circular) ]
            p_tmp = points1 + points_on_outer_radius[1:-1] + points2[::-1] + points_on_root[1:-1] # [::-1] reverses list; [1:-1] removes first and last element
        else:
            points_on_root = [point_on_circle (root_radius, x) for x in linspace(base2, base1+(two_pi/float(teeth)), accuracy_circular) ]
            p_tmp = points1 + points_on_outer_radius[1:-1] + points2[::-1] + points_on_root # [::-1] reverses list

        points.extend( p_tmp )

    return (points)

def inkbool(val):
    return val not in ("False", False, "0", 0, "None", None)

class OptionParser(argparse.ArgumentParser):

    types = {
        "int" : int,
        "float" : float,
        "string" : str,
        "inkbool" : inkbool,
        }

    def add_option(self, short, long_, **kw):
        kw["type"] = self.types[kw["type"]]
        names = []
        if short:
            names.append("-" + short.replace("-", "_")[1:])
        if long_:
            names.append("--" + long_.replace("-", "_")[2:])
        self.add_argument(*names, **kw)

class Gears():

    def __init__(self, boxes, **kw):
        # an alternate way to get debug info:
        # could use inkex.debug(string) instead...
        try:
            self.tty = open("/dev/tty", 'w')
        except:
            self.tty = open(devnull, 'w')  # '/dev/null' for POSIX, 'nul' for Windows.
            # print >>self.tty, "gears-dev " + __version__

        self.boxes = boxes
        self.OptionParser = OptionParser()
        self.OptionParser.add_option("-t", "--teeth",
                                     action="store", type="int",
                                     dest="teeth", default=24,
                                     help="Number of teeth")

        self.OptionParser.add_option("-s", "--system",
                                     action="store", type="string", 
                                     dest="system", default='MM',
                                     help="Select system: 'CP' (Cyclic Pitch (default)), 'DP' (Diametral Pitch), 'MM' (Metric Module)")

        self.OptionParser.add_option("-d", "--dimension",
                                     action="store", type="float",
                                     dest="dimension", default=1.0,
                                     help="Tooth size, depending on system (which defaults to CP)")


        self.OptionParser.add_option("-a", "--angle",
                                     action="store", type="float",
                                     dest="angle", default=20.0,
                                     help="Pressure Angle (common values: 14.5, 20, 25 degrees)")

        self.OptionParser.add_option("-p", "--profile-shift",
                                     action="store", type="float",
                                     dest="profile_shift", default=20.0,
                                     help="Profile shift [in percent of the module]. Negative values help against undercut")

        self.OptionParser.add_option("-u", "--units",
                                     action="store", type="string",
                                     dest="units", default='mm',
                                     help="Units this dialog is using")

        self.OptionParser.add_option("-A", "--accuracy",
                                     action="store", type="int",
                                     dest="accuracy", default=0,
                                     help="Accuracy of involute: automatic: 5..20 (default), best: 20(default), medium 10, low: 5; good acuracy is important with a low tooth count")
        # Clearance: Radial distance between top of tooth on one gear to bottom of gap on another.
        self.OptionParser.add_option("", "--clearance",
                                     action="store", type="float",
                                     dest="clearance", default=0.0,
                                     help="Clearance between bottom of gap of this gear and top of tooth of another")

        self.OptionParser.add_option("", "--annotation",
                                     action="store", type="inkbool", 
                                     dest="annotation", default=False,
                                     help="Draw annotation text")

        self.OptionParser.add_option("-i", "--internal-ring",
                                     action="store", type="inkbool",
                                     dest="internal_ring", default=False,
                                     help="Ring (or Internal) gear style (default: normal spur gear)")

        self.OptionParser.add_option("", "--mount-hole",
                                     action="store", type="float",
                                     dest="mount_hole", default=0.,
                                     help="Mount hole diameter")

        self.OptionParser.add_option("", "--mount-diameter",
                                     action="store", type="float",
                                     dest="mount_diameter", default=15,
                                     help="Mount support diameter")

        self.OptionParser.add_option("", "--spoke-count",
                                     action="store", type="int",
                                     dest="spoke_count", default=3,
                                     help="Spokes count")

        self.OptionParser.add_option("", "--spoke-width",
                                     action="store", type="float",
                                     dest="spoke_width", default=5,
                                     help="Spoke width")

        self.OptionParser.add_option("", "--holes-rounding",
                                     action="store", type="float",
                                     dest="holes_rounding", default=5,
                                     help="Holes rounding")

        self.OptionParser.add_option("", "--active-tab",
                                     action="store", type="string",
                                     dest="active_tab", default='',
                                     help="Active tab. Not used now.")

        self.OptionParser.add_option("-x", "--centercross",
                                     action="store", type="inkbool", 
                                     dest="centercross", default=False,
                                     help="Draw cross in center")

        self.OptionParser.add_option("-c", "--pitchcircle",
                                     action="store", type="inkbool",
                                     dest="pitchcircle", default=False,
                                     help="Draw pitch circle (for mating)")

        self.OptionParser.add_option("-r", "--draw-rack",
                                     action="store", type="inkbool", 
                                     dest="drawrack", default=False,
                                     help="Draw rack gear instead of spur gear")

        self.OptionParser.add_option("", "--rack-teeth-length",
                                     action="store", type="int",
                                     dest="teeth_length", default=12,
                                     help="Length (in teeth) of rack")

        self.OptionParser.add_option("", "--rack-base-height",
                                     action="store", type="float",
                                     dest="base_height", default=8,
                                     help="Height of base of rack")

        self.OptionParser.add_option("", "--rack-base-tab",
                                     action="store", type="float",
                                     dest="base_tab", default=14,
                                     help="Length of tabs on ends of rack")

        self.OptionParser.add_option("", "--undercut-alert",
                                     action="store", type="inkbool", 
                                     dest="undercut_alert", default=False,
                                     help="Let the user confirm a warning dialog if undercut occurs. This dialog also shows helpful hints against undercut")

    def drawPoints(self, lines, kerfdir=1, close=True):

        if not lines:
            return

        if kerfdir != 0:
            lines = kerf(lines, self.boxes.burn*kerfdir, closed=close)

        self.boxes.ctx.save()
        self.boxes.ctx.move_to(*lines[0])

        for x, y in lines[1:]:
            self.boxes.ctx.line_to(x, y)

        if close:
            self.boxes.ctx.line_to(*lines[0])
        self.boxes.ctx.restore()

    def calc_circular_pitch(self):
        """ We use math based on circular pitch.
        """
        dimension = self.options.dimension
        if   self.options.system == 'CP': # circular pitch
            circular_pitch = dimension * 25.4
        elif self.options.system == 'DP': # diametral pitch 
            circular_pitch = pi * 25.4 / dimension
        elif self.options.system == 'MM': # module (metric)
            circular_pitch = pi * dimension
        else:
            raise ValueError("unknown system '%s', try CP, DP, MM" % self.options.system)

        # circular_pitch defines the size in mm
        return circular_pitch

    def generate_spokes(self, root_radius, spoke_width, spokes, mount_radius, mount_hole,
                             unit_factor, unit_label):
        """ given a set of constraints
            - generate the svg path for the gear spokes
            - lies between mount_radius (inner hole) and root_radius (bottom of the teeth)
            - spoke width also defines the spacing at the root_radius
            - mount_radius is adjusted so that spokes fit if there is room
            - if no room (collision) then spokes not drawn
        """

        if not spokes:
            return []

        # Spokes
        collision = False # assume we draw spokes
        messages = []     # messages to send back about changes.
        spoke_holes = []
        r_outer = root_radius - spoke_width

        try:
            spoke_count = spokes
            spokes = [i*2*pi/spokes for i in range(spoke_count)]
        except TypeError:
            spoke_count = len(spokes)
            spokes = [radians(a) for a in spokes]
        spokes.append(spokes[0]+two_pi)

        # checks for collision with spokes
        # check for mount hole collision with inner spokes
        if mount_radius <= mount_hole/2:
            adj_factor = (r_outer - mount_hole/2) / 5

            if adj_factor < 0.1:
                # not enough reasonable room
                collision = True
            else:
                mount_radius = mount_hole/2 + adj_factor # small fix
                messages.append("Mount support too small. Auto increased to %2.2f%s." % (mount_radius/unit_factor*2, unit_label))

        # then check to see if cross-over on spoke width
        for i in range(spoke_count):
            angle = spokes[i]-spokes[i-1]

            if spoke_width >= angle * mount_radius:
                adj_factor = 1.2 # wrong value. its probably one of the points distances calculated below
                mount_radius += adj_factor
                messages.append("Too many spokes. Increased Mount support by %2.3f%s" % (adj_factor/unit_factor, unit_label))

        # check for collision with outer rim
        if r_outer <= mount_radius:
            # not enough room to draw spokes so cancel
            collision = True
        if collision: # don't draw spokes if no room.
            messages.append("Not enough room for Spokes. Decrease Spoke width.")
        else: # draw spokes

            for i in range(spoke_count):
                self.boxes.ctx.save()
                start_a, end_a = spokes[i], spokes[i+1]
                # inner circle around mount
                asin_factor = spoke_width/mount_radius/2
                # check if need to clamp radius
                asin_factor = max(-1.0, min(1.0, asin_factor)) # no longer needed - resized above
                a = asin(asin_factor)

                # is inner circle too small
                asin_factor = spoke_width/r_outer/2
                # check if need to clamp radius
                asin_factor = max(-1.0, min(1.0, asin_factor)) # no longer needed - resized above
                a2 = asin(asin_factor)
                l = vlength(vdiff(point_on_circle(mount_radius, start_a + a),
                                  point_on_circle(r_outer, start_a + a2)))
                self.boxes.moveTo(*point_on_circle(mount_radius, start_a + a), degrees=degrees(start_a))
                self.boxes.polyline(
                    l,
                    +90+degrees(a2), 0,
                    (degrees(end_a-start_a-2*a2), r_outer), 0,
                    +90+degrees(a2),
                    l, 90-degrees(a), 0,
                    (-degrees(end_a-start_a-2*a), mount_radius),
                    0, 90+degrees(a2), 0
                )

                self.boxes.ctx.restore()

        return messages

    def sizes(self, **kw):
        self.options = self.OptionParser.parse_args(["--%s=%s" % (name,value) for name, value in kw.items()])
        # Pitch (circular pitch): Length of the arc from one tooth to the next)
        # Pitch diameter: Diameter of pitch circle.
        pitch = self.calc_circular_pitch()

        if self.options.drawrack:
            base_height = self.options.base_height * unit_factor
            tab_width = self.options.base_tab * unit_factor
            tooth_count = self.options.teeth_length
            width = tooth_count * pitch + 2*tab_width
            height = base_height+ 2* addendum
            return 0, width, height

        teeth = self.options.teeth
        # Angle of tangent to tooth at circular pitch wrt radial line.
        angle = self.options.angle
        # Clearance: Radial distance between top of tooth on one gear to
        # bottom of gap on another.
        clearance = self.options.clearance # * unit_factor
        # Replace section below with this call to get the combined gear_calculations() above
        (pitch_radius, base_radius, addendum, dedendum,
         outer_radius, root_radius, tooth) = gear_calculations(teeth, pitch, angle, clearance, self.options.internal_ring, self.options.profile_shift*0.01)
        if self.options.internal_ring:
            outer_radius += self.options.spoke_width
        return pitch_radius, 2*outer_radius, 2*outer_radius

    def gearCarrier(self, r, spoke_width, positions, mount_radius, mount_hole, circle=True, callback=None, move=None):
        width = 2*r+spoke_width

        if self.boxes.move(width, width, move, before=True):
            return

        try:
            positions = [i*360/positions for i in range(positions)]
        except TypeError:
            pass

        self.boxes.ctx.save()
        self.boxes.moveTo(width/2.0, width/2.0)
        if callback:
            self.boxes.cc(callback, None)
        self.generate_spokes(r+0.5*spoke_width, spoke_width, positions, mount_radius, mount_hole, 1, "")
        self.boxes.hole(0, 0, mount_hole)

        for angle in positions:
            self.boxes.ctx.save()
            self.boxes.moveTo(0, 0, angle)
            self.boxes.hole(r, 0, mount_hole)
            self.boxes.ctx.restore()

        self.boxes.moveTo(r+0.5*spoke_width+self.boxes.burn, 0, 90)
        self.boxes.corner(360, r+0.5*spoke_width)
        
        self.boxes.ctx.restore()
        self.boxes.move(width, width, move)

    def __call__(self, teeth_only=False, move="", callback=None, **kw):
        """ Calculate Gear factors from inputs.
            - Make list of radii, angles, and centers for each tooth and 
              iterate through them
            - Turn on other visual features e.g. cross, rack, annotations, etc
        """
        self.options = self.OptionParser.parse_args(["--%s=%s" % (name,value) for name, value in kw.items()])

        warnings = [] # list of extra messages to be shown in annotations
        # calculate unit factor for units defined in dialog. 
        unit_factor = 1
        # User defined options
        teeth = self.options.teeth
        # Angle of tangent to tooth at circular pitch wrt radial line.
        angle = self.options.angle 
        # Clearance: Radial distance between top of tooth on one gear to 
        # bottom of gap on another.
        clearance = self.options.clearance * unit_factor
        mount_hole = self.options.mount_hole * unit_factor
        # for spokes
        mount_radius = self.options.mount_diameter * 0.5 * unit_factor
        spoke_count = self.options.spoke_count
        spoke_width = self.options.spoke_width * unit_factor
        holes_rounding = self.options.holes_rounding * unit_factor # unused
        # visible guide lines
        centercross = self.options.centercross # draw center or not (boolean)
        pitchcircle = self.options.pitchcircle # draw pitch circle or not (boolean)

        # Accuracy of teeth curves
        accuracy_involute = 20 # Number of points of the involute curve
        accuracy_circular = 9  # Number of points on circular parts
        if self.options.accuracy is not None:
            if self.options.accuracy == 0:  
                # automatic
                if   teeth < 10: accuracy_involute = 20
                elif teeth < 30: accuracy_involute = 12
                else:            accuracy_involute = 6
            else:
                accuracy_involute = self.options.accuracy

            accuracy_circular = max(3, int(accuracy_involute/2) - 1) # never less than three
        # print >>self.tty, "accuracy_circular=%s accuracy_involute=%s" % (accuracy_circular, accuracy_involute)
        # Pitch (circular pitch): Length of the arc from one tooth to the next)
        # Pitch diameter: Diameter of pitch circle.
        pitch = self.calc_circular_pitch()
        # Replace section below with this call to get the combined gear_calculations() above
        (pitch_radius, base_radius, addendum, dedendum,
         outer_radius, root_radius, tooth) = gear_calculations(teeth, pitch, angle, clearance, self.options.internal_ring, self.options.profile_shift*0.01)

        b = self.boxes.burn
        # Add Rack (instead)
        if self.options.drawrack:
            base_height = self.options.base_height * unit_factor
            tab_width = self.options.base_tab * unit_factor
            tooth_count = self.options.teeth_length
            (points, guide_points) = generate_rack_points(tooth_count, pitch, addendum, angle,
                                                          base_height, tab_width, clearance, pitchcircle)
            width = tooth_count * pitch + 2 * tab_width
            height = base_height + 2 * addendum
            if self.boxes.move(width, height, move, before=True):
                return

            self.boxes.cc(callback, None)
            self.boxes.moveTo(width/2.0, base_height+addendum, -180)
            if base_height < 0:
                points = points[1:-1]
            self.drawPoints(points, close=base_height >= 0)
            self.drawPoints(guide_points, kerfdir=0)
            self.boxes.move(width, height, move)

            return

        # Move only
        width = height = 2 * outer_radius
        if self.options.internal_ring:
            width = height = width + 2 * self.options.spoke_width

        if not teeth_only and self.boxes.move(width, height, move, before=True):
            return

        # Detect Undercut of teeth
##        undercut = int(ceil(undercut_min_teeth( angle )))
##        needs_undercut = teeth < undercut #? no longer needed ?
        if have_undercut(teeth, angle, 1.0):
            min_teeth = int(ceil(undercut_min_teeth(angle, 1.0)))
            min_angle = undercut_min_angle(teeth, 1.0) + .1
            max_k = undercut_max_k(teeth, angle)
            msg = "Undercut Warning: This gear (%d teeth) will not work well.\nTry tooth count of %d or more,\nor a pressure angle of %.1f [deg] or more,\nor try a profile shift of %d %%.\nOr other decent combinations." % (teeth, min_teeth, min_angle, int(100.*max_k)-100.)
            # alas annotation cannot handle the degree symbol. Also it ignore newlines.
            # so split and make a list
            warnings.extend(msg.split("\n"))

        # All base calcs done. Start building gear
        points = generate_spur_points(teeth, base_radius, pitch_radius, outer_radius, root_radius, accuracy_involute, accuracy_circular)

        if not teeth_only:
            self.boxes.moveTo(width/2, height/2)
        self.boxes.cc(callback, None, 0, 0)
        self.drawPoints(points)
        # Spokes
        if not teeth_only and not self.options.internal_ring:  # only draw internals if spur gear
            msg = self.generate_spokes(root_radius, spoke_width, spoke_count, mount_radius, mount_hole,
                                                    unit_factor, self.options.units)
            warnings.extend(msg)

            # Draw mount hole
            # A : rx,ry  x-axis-rotation, large-arch-flag, sweepflag  x,y
            r = mount_hole / 2
            self.boxes.hole(0, 0, r)
        elif not teeth_only:
            # its a ring gear
            # which only has an outer ring where width = spoke width
            r = outer_radius + spoke_width + self.boxes.burn
            self.boxes.ctx.save()
            self.boxes.moveTo(r, 0)
            self.boxes.ctx.arc(-r, 0, r, 0, 2*pi)
            self.boxes.ctx.restore()

        # Add center
        if centercross:
            cs = pitch / 3.0 # centercross length
            self.boxes.ctx.save()
            self.boxes.ctx.move_to(-cs, 0)
            self.boxes.ctx.line_to(+cs, 0)
            self.boxes.ctx.move_to(0, -cs)
            self.boxes.ctx.line_to(0, +cs)
            self.boxes.ctx.restore()

        # Add pitch circle (for mating)
        if pitchcircle:
            self.boxes.hole(0, 0, pitch_radius)

        # Add Annotations (above)
        if self.options.annotation:
            outer_dia = outer_radius * 2

            if self.options.internal_ring:
                outer_dia += 2 * spoke_width

            notes = []
            notes.extend(warnings)
            #notes.append('Document (%s) scale conversion = %2.4f' % (self.document.getroot().find(inkex.addNS('namedview', 'sodipodi')).get(inkex.addNS('document-units', 'inkscape')), unit_factor))
            notes.extend(['Teeth: %d   CP: %2.4f(%s) ' % (teeth, pitch / unit_factor, self.options.units),
                          'DP: %2.3f Module: %2.4f(mm)' % (25.4 * pi / pitch, pitch),
                          'Pressure Angle: %2.2f degrees' % (angle),
                          'Pitch diameter: %2.3f %s' % (pitch_radius * 2 / unit_factor, self.options.units),
                          'Outer diameter: %2.3f %s' % (outer_dia / unit_factor, self.options.units),
                          'Base diameter:  %2.3f %s' % (base_radius * 2 / unit_factor, self.options.units)#,
                          #'Addendum:      %2.4f %s'  % (addendum / unit_factor, self.options.units),
                          #'Dedendum:      %2.4f %s'  % (dedendum / unit_factor, self.options.units)
                          ])
            # text height relative to gear size.
            # ranges from 10 to 22 over outer radius size 60 to 360
            text_height = max(10, min(10+(outer_dia-60)/24, 22))
            # position above
            y = - outer_radius - (len(notes)+1) * text_height * 1.2

            for note in notes:
                self.boxes.text(note, -outer_radius, y)
                y += text_height * 1.2

        if not teeth_only:
            self.boxes.move(width, height, move)

