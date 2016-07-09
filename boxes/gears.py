#! /usr/bin/env python
# -*- coding: utf-8 -*-
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

import inkex, simplestyle
from os import devnull # for debugging
from math import pi, cos, sin, tan, radians, degrees, ceil, asin, acos, sqrt
two_pi = 2 * pi


__version__ = '0.9'

def uutounit(self,nn,uu):
    try:
        return self.uutounit(nn,uu)		# inkscape 0.91
    except:
        return inkex.uutounit(nn,uu)	# inkscape 0.48

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

def points_to_bbox(p):
    """ from a list of points (x,y pairs)
        - return the lower-left xy and upper-right xy
    """
    llx = urx = p[0][0]
    lly = ury = p[0][1]
    for x in p[1:]:
        if   x[0] < llx: llx = x[0]
        elif x[0] > urx: urx = x[0]
        if   x[1] < lly: lly = x[1]
        elif x[1] > ury: ury = x[1]
    return (llx, lly, urx, ury)

def points_to_bbox_center(p):
    """ from a list of points (x,y pairs)
        - find midpoint of bounding box around all points
        - return (x,y)
    """
    bbox = points_to_bbox(p)
    return ((bbox[0]+bbox[2])/2.0, (bbox[1]+bbox[3])/2.0)

def points_to_svgd(p):
    " convert list of points into a closed SVG path list"
    f = p[0]
    p = p[1:]
    svgd = 'M%.4f,%.4f' % f
    for x in p:
        svgd += 'L%.4f,%.4f' % x
    svgd += 'z'
    return svgd

def draw_SVG_circle(parent, r, cx, cy, name, style):
    " add an SVG circle entity to parent "
    circ_attribs = {'style': simplestyle.formatStyle(style),
                    'cx': str(cx), 'cy': str(cy), 
                    'r': str(r),
                    inkex.addNS('label','inkscape'):name}
    circle = inkex.etree.SubElement(parent, inkex.addNS('circle','svg'), circ_attribs )


### Undercut support functions
def undercut_min_teeth(pitch_angle, k=1.0):
    """ computes the minimum tooth count for a 
        spur gear so that no undercut with the given pitch_angle (in deg) 
        and an addendum = k * metric_module, where 0 < k < 1
    Note:
    The return value should be rounded upwards for perfect safety. E.g.
    min_teeth = int(math.ceil(undercut_min_teeth(20.0)))    # 18, not 17
    """
    x = sin(radians(pitch_angle))
    return 2*k /(x*x)

def undercut_max_k(teeth, pitch_angle=20.0):
    """ computes the maximum k value for a given teeth count and pitch_angle
        so that no undercut occurs.
    """
    x = sin(radians(pitch_angle))
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
    #dedendum = 1.157 / diametral_pitch # auto calc clearance
    dedendum = addendum
    dedendum *= 1+profile_shift
    addendum *= 1-profile_shift
    if ring_gear:
        addendum = addendum + clearance # our method
    else:
        dedendum = dedendum + clearance # our method
    #
    #
    base_radius = pitch_diameter * cos(radians(pressure_angle)) / 2.0
    outer_radius = pitch_radius + addendum
    root_radius =  pitch_radius - dedendum
    # Tooth thickness: Tooth width along pitch circle.
    tooth_thickness  = ( pi * pitch_diameter ) / ( 2.0 * num_teeth )
    # we don't use these
    working_depth = 2 / diametral_pitch
    whole_depth = 2.157 / diametral_pitch
    #outside_diameter = (num_teeth + 2) / diametral_pitch
    #
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
    fudge = +0.5 * spacing

    tas  = tan(radians(pressure_angle)) * addendum
    tasc = tan(radians(pressure_angle)) * (addendum+clearance)
    base_top = addendum+clearance
    base_bot = addendum+clearance+base_height

    x_lhs = -pitch * int(0.5*tooth_count-.5) - spacing - tab_length - tasc + fudge
    #inkex.debug("angle=%s spacing=%s"%(pressure_angle, spacing))
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
    x -= spacing # remove last adjustment
    # add base on RHS
    x_rhs = x+tasc+tab_length
    points.append((x_rhs, base_top))
    points.append((x_rhs, base_bot))
    # We don't close the path here. Caller does it.
    # points.append((x_lhs, base_bot))

    # Draw line representing the pitch circle of infinite diameter
    guide_path = None
    if draw_guides:
        p = []
        p.append( (x_lhs + 0.5 * tab_length, 0) )
        p.append( (x_rhs - 0.5 * tab_length, 0) )
        guide_path = points_to_svgd(p)
    # return points ready for use in an SVG 'path'
    return (points, guide_path)


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


def generate_spokes_path(root_radius, spoke_width, spoke_count, mount_radius, mount_hole,
                         unit_factor, unit_label):
    """ given a set of constraints
        - generate the svg path for the gear spokes
        - lies between mount_radius (inner hole) and root_radius (bottom of the teeth)
        - spoke width also defines the spacing at the root_radius
        - mount_radius is adjusted so that spokes fit if there is room
        - if no room (collision) then spokes not drawn
    """
    # Spokes
    collision = False # assume we draw spokes
    messages = []     # messages to send back about changes.
    path = ''
    r_outer = root_radius - spoke_width
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
    if spoke_width * spoke_count +0.5 >= two_pi * mount_radius:
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
            points = []
            start_a, end_a = i * two_pi / spoke_count, (i+1) * two_pi / spoke_count
            # inner circle around mount
            asin_factor = spoke_width/mount_radius/2
            # check if need to clamp radius
            asin_factor = max(-1.0, min(1.0, asin_factor)) # no longer needed - resized above
            a = asin(asin_factor)
            points += [ point_on_circle(mount_radius, start_a + a), point_on_circle(mount_radius, end_a - a)]
            # is inner circle too small
            asin_factor = spoke_width/r_outer/2
            # check if need to clamp radius
            asin_factor = max(-1.0, min(1.0, asin_factor)) # no longer needed - resized above
            a = asin(asin_factor)
            points += [point_on_circle(r_outer, end_a - a), point_on_circle(r_outer, start_a + a) ]

            path += (
                    "M %f,%f" % points[0] +
                    "A  %f,%f %s %s %s %f,%f" % tuple((mount_radius, mount_radius, 0, 0 if spoke_count!=1 else 1, 1 ) + points[1]) +
                    "L %f,%f" % points[2] +
                    "A  %f,%f %s %s %s %f,%f" % tuple((r_outer, r_outer, 0, 0 if spoke_count!=1 else 1, 0 ) + points[3]) +
                    "Z"
                    )
    return (path, messages)


class Gears(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        # an alternate way to get debug info:
        # could use inkex.debug(string) instead...
        try:
            self.tty = open("/dev/tty", 'w')
        except:
            self.tty = open(devnull, 'w')  # '/dev/null' for POSIX, 'nul' for Windows.
            # print >>self.tty, "gears-dev " + __version__
        self.OptionParser.add_option("-t", "--teeth",
                                     action="store", type="int",
                                     dest="teeth", default=24,
                                     help="Number of teeth")

        self.OptionParser.add_option("-s", "--system",
                                     action="store", type="string", 
                                     dest="system", default='CP',
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
                                     dest="mount_hole", default=5,
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


    def add_text(self, node, text, position, text_height=12):
        """ Create and insert a single line of text into the svg under node.
            - use 'text' type and label as anootation
            - where color is Ponoko Orange - so ignored when lasercutting
        """
        line_style = {'font-size': '%dpx' % text_height, 'font-style':'normal', 'font-weight': 'normal',
                     'fill': '#F6921E', 'font-family': 'Bitstream Vera Sans,sans-serif',
                     'text-anchor': 'middle', 'text-align': 'center'}
        line_attribs = {inkex.addNS('label','inkscape'): 'Annotation',
                       'style': simplestyle.formatStyle(line_style),
                       'x': str(position[0]),
                       'y': str((position[1] + text_height) * 1.2)
                       }
        line = inkex.etree.SubElement(node, inkex.addNS('text','svg'), line_attribs)
        line.text = text


    def calc_unit_factor(self):
        """ return the scale factor for all dimension conversions.
            - The document units are always irrelevant as
              everything in inkscape is expected to be in 90dpi pixel units
        """
        # namedView = self.document.getroot().find(inkex.addNS('namedview', 'sodipodi'))
        # doc_units = uutounit(self, 1.0, namedView.get(inkex.addNS('document-units', 'inkscape')))
        dialog_units = uutounit(self, 1.0, self.options.units)
        unit_factor = 1.0 / dialog_units
        return unit_factor

    def calc_circular_pitch(self):
        """ We use math based on circular pitch.
            Expressed in inkscape units which is 90dpi 'pixel' units.
        """
        dimension = self.options.dimension
        # print >> self.tty, "unit_factor=%s, doc_units=%s, dialog_units=%s (%s), system=%s" % (unit_factor, doc_units, dialog_units, self.options.units, self.options.system)
        if   self.options.system == 'CP': # circular pitch
            circular_pitch = dimension
        elif self.options.system == 'DP': # diametral pitch 
            circular_pitch = pi / dimension
        elif self.options.system == 'MM': # module (metric)
            circular_pitch = dimension * pi / 25.4
        else:
            inkex.debug("unknown system '%s', try CP, DP, MM" % self.options.system)
        # circular_pitch defines the size in inches.
        # We divide the internal inch factor (px = 90dpi), to remove the inch 
        # unit.
        # The internal inkscape unit is always px, 
        # it is independent of the doc_units!
        return circular_pitch / uutounit(self, 1.0, 'in')



    def effect(self):
        """ Calculate Gear factors from inputs.
            - Make list of radii, angles, and centers for each tooth and 
              iterate through them
            - Turn on other visual features e.g. cross, rack, annotations, etc
        """
        path_stroke = '#000000'  # might expose one day
        path_fill   = 'none'     # no fill - just a line
        path_stroke_width  = 0.6            # might expose one day
        path_stroke_light  = path_stroke_width * 0.25   # guides are thinner
        #
        warnings = [] # list of extra messages to be shown in annotations
        # calculate unit factor for units defined in dialog. 
        unit_factor = self.calc_unit_factor()
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
            if self.options.undercut_alert:
                inkex.debug(msg)
            else:
                print >>self.tty, msg

        # All base calcs done. Start building gear
        points = generate_spur_points(teeth, base_radius, pitch_radius, outer_radius, root_radius, accuracy_involute, accuracy_circular)

##        half_thick_angle = two_pi / (4.0 * teeth ) #?? = pi / (2.0 * teeth)
##        pitch_to_base_angle  = involute_intersect_angle( base_radius, pitch_radius )
##        pitch_to_outer_angle = involute_intersect_angle( base_radius, outer_radius ) - pitch_to_base_angle
##
##        start_involute_radius = max(base_radius, root_radius)
##        radii = linspace(start_involute_radius, outer_radius, accuracy_involute)
##        angles = [involute_intersect_angle(base_radius, r) for r in radii]
##
##        centers = [(x * two_pi / float( teeth) ) for x in range( teeth ) ]
##        points = []
##
##        for c in centers:
##            # Angles
##            pitch1 = c - half_thick_angle
##            base1  = pitch1 - pitch_to_base_angle
##            offsetangles1 = [ base1 + x for x in angles]
##            points1 = [ point_on_circle( radii[i], offsetangles1[i]) for i in range(0,len(radii)) ]
##
##            pitch2 = c + half_thick_angle
##            base2  = pitch2 + pitch_to_base_angle
##            offsetangles2 = [ base2 - x for x in angles] 
##            points2 = [ point_on_circle( radii[i], offsetangles2[i]) for i in range(0,len(radii)) ]
##
##            points_on_outer_radius = [ point_on_circle(outer_radius, x) for x in linspace(offsetangles1[-1], offsetangles2[-1], accuracy_circular) ]
##
##            if root_radius > base_radius:
##                pitch_to_root_angle = pitch_to_base_angle - involute_intersect_angle(base_radius, root_radius )
##                root1 = pitch1 - pitch_to_root_angle
##                root2 = pitch2 + pitch_to_root_angle
##                points_on_root = [point_on_circle (root_radius, x) for x in linspace(root2, root1+(two_pi/float(teeth)), accuracy_circular) ]
##                p_tmp = points1 + points_on_outer_radius[1:-1] + points2[::-1] + points_on_root[1:-1] # [::-1] reverses list; [1:-1] removes first and last element
##            else:
##                points_on_root = [point_on_circle (root_radius, x) for x in linspace(base2, base1+(two_pi/float(teeth)), accuracy_circular) ]
##                p_tmp = points1 + points_on_outer_radius[1:-1] + points2[::-1] + points_on_root # [::-1] reverses list
##
##            points.extend( p_tmp )

        path = points_to_svgd( points )
        bbox_center = points_to_bbox_center( points )

        # Spokes (add to current path)
        if not self.options.internal_ring:  # only draw internals if spur gear
            spokes_path, msg = generate_spokes_path(root_radius, spoke_width, spoke_count, mount_radius, mount_hole,
                                                    unit_factor, self.options.units)
            warnings.extend(msg)
            path += spokes_path

            # Draw mount hole
            # A : rx,ry  x-axis-rotation, large-arch-flag, sweepflag  x,y
            r = mount_hole / 2
            path += (
                    "M %f,%f" % (0,r) +
                    "A  %f,%f %s %s %s %f,%f" % (r,r, 0,0,0, 0,-r) +
                    "A  %f,%f %s %s %s %f,%f" % (r,r, 0,0,0, 0,r) 
                    )
        else:
            # its a ring gear
            # which only has an outer ring where width = spoke width
            r = outer_radius + spoke_width
            path += (
                    "M %f,%f" % (0,r) +
                    "A  %f,%f %s %s %s %f,%f" % (r,r, 0,0,0, 0,-r) +
                    "A  %f,%f %s %s %s %f,%f" % (r,r, 0,0,0, 0,r) 
                    )

        # Embed gear in group to make animation easier:
        #  Translate group, Rotate path.
        t = 'translate(' + str( self.view_center[0] ) + ',' + str( self.view_center[1] ) + ')'
        g_attribs = { inkex.addNS('label','inkscape'):'Gear' + str( teeth ),
                      inkex.addNS('transform-center-x','inkscape'): str(-bbox_center[0]),
                      inkex.addNS('transform-center-y','inkscape'): str(-bbox_center[1]),
                      'transform':t,
                      'info':'N:'+str(teeth)+'; Pitch:'+ str(pitch) + '; Pressure Angle: '+str(angle) }
        # add the group to the current layer
        g = inkex.etree.SubElement(self.current_layer, 'g', g_attribs )

        # Create gear path under top level group
        style = { 'stroke': path_stroke, 'fill': path_fill, 'stroke-width': path_stroke_width }
        gear_attribs = { 'style': simplestyle.formatStyle(style), 'd': path }
        gear = inkex.etree.SubElement(g, inkex.addNS('path','svg'), gear_attribs )

        # Add center
        if centercross:
            style = { 'stroke': path_stroke, 'fill': path_fill, 'stroke-width': path_stroke_light }
            cs = str(pitch / 3) # centercross length
            d = 'M-'+cs+',0L'+cs+',0M0,-'+cs+'L0,'+cs  # 'M-10,0L10,0M0,-10L0,10'
            center_attribs = { inkex.addNS('label','inkscape'): 'Center cross',
                               'style': simplestyle.formatStyle(style), 'd': d }
            center = inkex.etree.SubElement(g, inkex.addNS('path','svg'), center_attribs )

        # Add pitch circle (for mating)
        if pitchcircle:
            style = { 'stroke': path_stroke, 'fill': path_fill, 'stroke-width': path_stroke_light }
            draw_SVG_circle(g, pitch_radius, 0, 0, 'Pitch circle', style)

        # Add Rack (below)
        if self.options.drawrack:
            base_height = self.options.base_height * unit_factor
            tab_width = self.options.base_tab * unit_factor
            tooth_count = self.options.teeth_length
            (points, guide_path) = generate_rack_points(tooth_count, pitch, addendum, angle,
                                                        base_height, tab_width, clearance, pitchcircle)
            path = points_to_svgd(points)
            # position below Gear, so that it meshes nicely
            # xoff = 0          ## if teeth % 4 == 2.
            # xoff = -0.5*pitch     ## if teeth % 4 == 0.
            # xoff = -0.75*pitch    ## if teeth % 4 == 3.
            # xoff = -0.25*pitch    ## if teeth % 4 == 1.
            xoff = (-0.5, -0.25, 0, -0.75)[teeth % 4] * pitch
            t = 'translate(' + str( xoff ) + ',' + str( pitch_radius ) + ')'
            g_attribs = { inkex.addNS('label', 'inkscape'): 'RackGear' + str(tooth_count),
                          'transform': t }
            rack = inkex.etree.SubElement(g, 'g', g_attribs)

            # Create SVG Path for gear
            style = {'stroke': path_stroke, 'fill': 'none', 'stroke-width': path_stroke_width }
            gear_attribs = { 'style': simplestyle.formatStyle(style), 'd': path }
            gear = inkex.etree.SubElement(
                rack, inkex.addNS('path', 'svg'), gear_attribs)
            if guide_path is not None:
                style2 = { 'stroke': path_stroke, 'fill': 'none', 'stroke-width': path_stroke_light }
                gear_attribs2 = { 'style': simplestyle.formatStyle(style2), 'd': guide_path }
                gear = inkex.etree.SubElement(
                    rack, inkex.addNS('path', 'svg'), gear_attribs2)


        # Add Annotations (above)
        if self.options.annotation:
            outer_dia = outer_radius * 2
            if self.options.internal_ring:
                outer_dia += 2 * spoke_width
            notes = []
            notes.extend(warnings)
            #notes.append('Document (%s) scale conversion = %2.4f' % (self.document.getroot().find(inkex.addNS('namedview', 'sodipodi')).get(inkex.addNS('document-units', 'inkscape')), unit_factor))
            notes.extend(['Teeth: %d   CP: %2.4f(%s) ' % (teeth, pitch / unit_factor, self.options.units),
                          'DP: %2.3f Module: %2.4f' % (pi / pitch * unit_factor, pitch / pi * 25.4),
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
                self.add_text(g, note, [0,y], text_height)
                y += text_height * 1.2

if __name__ == '__main__':
    e = Gears()
    e.affect()

# Notes

