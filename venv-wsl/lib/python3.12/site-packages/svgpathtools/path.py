"""This submodule contains the class definitions of the the main five classes
svgpathtools is built around: Path, Line, QuadraticBezier, CubicBezier, and
Arc."""

# External dependencies
from __future__ import annotations
import re
try:
    from collections.abc import MutableSequence  # noqa
except ImportError:
    from collections import MutableSequence  # noqa
from warnings import warn
from operator import itemgetter
import numpy as np
from itertools import tee
from functools import reduce

# these imports were originally from math and cmath, now are from numpy
# in order to encourage code that generalizes to vector inputs
from numpy import sqrt, cos, sin, tan, arccos as acos, arcsin as asin, \
    degrees, radians, log, pi, ceil
from numpy import exp, sqrt as csqrt, angle as phase, isnan

try:
    from scipy.integrate import quad
    _quad_available = True
except:
    _quad_available = False

# Internal dependencies
from .bezier import (bezier_intersections, bezier_bounding_box, split_bezier,
                     bezier_by_line_intersections, polynomial2bezier,
                     bezier2polynomial)
from .misctools import BugException
from .polytools import rational_limit, polyroots, polyroots01, imag, real

# To maintain forward/backward compatibility
try:
    str = basestring
except NameError:
    pass


COMMANDS = set('MmZzLlHhVvCcSsQqTtAa')
UPPERCASE = set('MZLHVCSQTA')

COMMAND_RE = re.compile(r"([MmZzLlHhVvCcSsQqTtAa])")
FLOAT_RE = re.compile(r"[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?")

# Default Parameters ##########################################################

# path segment .length() parameters for arc length computation
LENGTH_MIN_DEPTH = 5
LENGTH_ERROR = 1e-12
USE_SCIPY_QUAD = True  # for elliptic Arc segment arc length computation

# path segment .ilength() parameters for inverse arc length computation
ILENGTH_MIN_DEPTH = 5
ILENGTH_ERROR = 1e-12
ILENGTH_S_TOL = 1e-12
ILENGTH_MAXITS = 10000

# compatibility/implementation related warnings and parameters
CLOSED_WARNING_ON = True
_NotImplemented4ArcException = \
    Exception("This method has not yet been implemented for Arc objects.")
# _NotImplemented4QuadraticException = \
#     Exception("This method has not yet been implemented for QuadraticBezier "
#               "objects.")
_is_smooth_from_warning = \
    ("The name of this method is somewhat misleading (yet kept for "
     "compatibility with scripts created using svg.path 2.0).  This method "
     "is meant only for d-string creation and should NOT be used to check "
     "for kinks.  To check a segment for differentiability, use the "
     "joins_smoothly_with() method instead or the kinks() function (in "
     "smoothing.py).\nTo turn off this warning, set "
     "warning_on=False.")


# Miscellaneous ###############################################################

def bezier_segment(*bpoints):
    if len(bpoints) == 2:
        start, end = bpoints
        return Line(start, end)
    elif len(bpoints) == 4:
        start, control1, control2, end = bpoints
        return CubicBezier(start, control1, control2, end)
    elif len(bpoints) == 3:
        start, control, end = bpoints
        return QuadraticBezier(start, control, end)
    else:
        assert len(bpoints) in (2, 3, 4)


def is_bezier_segment(seg):
    return (isinstance(seg, Line) or
            isinstance(seg, QuadraticBezier) or
            isinstance(seg, CubicBezier))


def is_path_segment(seg):
    return is_bezier_segment(seg) or isinstance(seg, Arc)


def is_bezier_path(path):
    """Checks that all segments in path are a Line, QuadraticBezier, or
    CubicBezier object."""
    return isinstance(path, Path) and all(map(is_bezier_segment, path))


def concatpaths(list_of_paths):
    """Takes in a sequence of paths and returns their concatenations into a
    single path (following the order of the input sequence)."""
    return Path(*[seg for path in list_of_paths for seg in path])


def bbox2path(xmin, xmax, ymin, ymax):
    """Converts a bounding box 4-tuple to a Path object."""
    b = Line(xmin + 1j*ymin, xmax + 1j*ymin)
    t = Line(xmin + 1j*ymax, xmax + 1j*ymax)
    r = Line(xmax + 1j*ymin, xmax + 1j*ymax)
    l = Line(xmin + 1j*ymin, xmin + 1j*ymax)
    return Path(b, r, t.reversed(), l.reversed())


def polyline(*points):
    """Converts a list of points to a Path composed of lines connecting those 
    points (i.e. a linear spline or polyline).  See also `polygon()`."""
    return Path(*[Line(points[i], points[i+1])
                  for i in range(len(points) - 1)])


def polygon(*points):
    """Converts a list of points to a Path composed of lines connecting those 
    points, then closes the path by connecting the last point to the first.  
    See also `polyline()`."""
    return Path(*[Line(points[i], points[(i + 1) % len(points)])
                  for i in range(len(points))])


# Conversion###################################################################

def bpoints2bezier(bpoints):
    """Converts a list of length 2, 3, or 4 to a CubicBezier, QuadraticBezier,
    or Line object, respectively.
    See also: poly2bez."""
    order = len(bpoints) - 1
    if order == 3:
        return CubicBezier(*bpoints)
    elif order == 2:
        return QuadraticBezier(*bpoints)
    elif order == 1:
        return Line(*bpoints)
    else:
        assert len(bpoints) in {2, 3, 4}


def poly2bez(poly, return_bpoints=False):
    """Converts a cubic or lower order Polynomial object (or a sequence of
    coefficients) to a CubicBezier, QuadraticBezier, or Line object as
    appropriate.  If return_bpoints=True then this will instead only return
    the control points of the corresponding Bezier curve.
    Note: The inverse operation is available as a method of CubicBezier,
    QuadraticBezier and Line objects."""
    bpoints = polynomial2bezier(poly)
    if return_bpoints:
        return bpoints
    else:
        return bpoints2bezier(bpoints)


def bez2poly(bez, numpy_ordering=True, return_poly1d=False):
    """Converts a Bezier object or tuple of Bezier control points to a tuple
    of coefficients of the expanded polynomial.
    return_poly1d : returns a numpy.poly1d object.  This makes computations
    of derivatives/anti-derivatives and many other operations quite quick.
    numpy_ordering : By default (to accommodate numpy) the coefficients will
    be output in reverse standard order.
    Note:  This function is redundant thanks to the .poly() method included
    with all bezier segment classes."""
    if is_bezier_segment(bez):
        bez = bez.bpoints()
    return bezier2polynomial(bez,
                             numpy_ordering=numpy_ordering,
                             return_poly1d=return_poly1d)


# Geometric####################################################################
def transform_segments_together(path, transformation):
    """Makes sure that, if joints were continuous, they're kept that way."""
    transformed_segs = [transformation(seg) for seg in path]

    for i, (sa, sb) in enumerate(path.joints()):
        if sa.end == sb.start:
            transformed_segs[i].end = transformed_segs[(i + 1) % len(path)].start
    return Path(*transformed_segs)


def rotate(curve, degs, origin=None):
    """Returns curve rotated by `degs` degrees (CCW) around the point `origin`
    (a complex number).  By default origin is either `curve.point(0.5)`, or in
    the case that curve is an Arc object, `origin` defaults to `curve.center`.
    """
    def rotate_point(z):
        return exp(1j*radians(degs))*(z - origin) + origin

    if origin is None:
        if isinstance(curve, Arc):
            origin = curve.center
        else:
            origin = curve.point(0.5)

    if isinstance(curve, Path):
        transformation = lambda seg: rotate(seg, degs, origin=origin)
        return transform_segments_together(curve, transformation)
    elif is_bezier_segment(curve):
        return bpoints2bezier([rotate_point(bpt) for bpt in curve.bpoints()])
    elif isinstance(curve, Arc):
        new_start = rotate_point(curve.start)
        new_end = rotate_point(curve.end)
        new_rotation = curve.rotation + degs
        return Arc(new_start, radius=curve.radius, rotation=new_rotation,
                   large_arc=curve.large_arc, sweep=curve.sweep, end=new_end)
    else:
        raise TypeError("Input `curve` should be a Path, Line, "
                        "QuadraticBezier, CubicBezier, or Arc object.")


def translate(curve, z0):
    """Shifts the curve by the complex quantity z such that
    translate(curve, z0).point(t) = curve.point(t) + z0"""
    if isinstance(curve, Path):
        transformation = lambda seg: translate(seg, z0)
        return transform_segments_together(curve, transformation)
    elif is_bezier_segment(curve):
        return bpoints2bezier([bpt + z0 for bpt in curve.bpoints()])
    elif isinstance(curve, Arc):
        new_start = curve.start + z0
        new_end = curve.end + z0
        return Arc(new_start, radius=curve.radius, rotation=curve.rotation,
                   large_arc=curve.large_arc, sweep=curve.sweep, end=new_end)
    else:
        raise TypeError("Input `curve` should be a Path, Line, "
                        "QuadraticBezier, CubicBezier, or Arc object.")


def scale(curve, sx, sy=None, origin=0j):
    """Scales `curve`, about `origin`, by diagonal matrix `[[sx,0],[0,sy]]`.

    Notes:
    ------
    * If `sy` is not specified, it is assumed to be equal to `sx` and 
    a scalar transformation of `curve` about `origin` will be returned.
    I.e.
        scale(curve, sx, origin).point(t) == 
            ((curve.point(t) - origin) * sx) + origin
    """

    if sy is None:
        isy = 1j*sx
    else:
        isy = 1j*sy

    def _scale(z):
        if sy is None:
            return sx*z
        return sx*z.real + isy*z.imag          

    def scale_bezier(bez):
        p = [_scale(c) for c in bez2poly(bez)]
        p[-1] += origin - _scale(origin)
        return poly2bez(p)

    if isinstance(curve, Path):
        transformation = lambda seg: scale(seg, sx, sy, origin)
        return transform_segments_together(curve, transformation)
    elif is_bezier_segment(curve):
        return scale_bezier(curve)
    elif isinstance(curve, Arc):
        if sy is None or sy == sx:
            return Arc(start=sx*(curve.start - origin) + origin,
                       radius=sx*curve.radius,
                       rotation=curve.rotation, 
                       large_arc=curve.large_arc, 
                       sweep=curve.sweep, 
                       end=sx*(curve.end - origin) + origin)
        else:
            raise Exception("\nFor `Arc` objects, only scale transforms "
                            "with sx==sy are implemented.\n")
    else:
        raise TypeError("Input `curve` should be a Path, Line, "
                        "QuadraticBezier, CubicBezier, or Arc object.")


def transform(curve, tf):
    """Transforms the curve by the homogeneous transformation matrix tf"""

    if all((tf == np.eye(3)).ravel()):
        return curve  # tf is identity, return curve as is

    def to_point(p):
        return np.array([[p.real], [p.imag], [1.0]])

    def to_vector(z):
        return np.array([[z.real], [z.imag], [0.0]])

    def to_complex(v):
        return v.item(0) + 1j * v.item(1)

    if isinstance(curve, Path):
        transformation = lambda seg: transform(seg, tf)
        return transform_segments_together(curve, transformation)

    elif is_bezier_segment(curve):
        return bpoints2bezier([to_complex(tf.dot(to_point(p)))
                               for p in curve.bpoints()])
    elif isinstance(curve, Arc):
        new_start = to_complex(tf.dot(to_point(curve.start)))
        new_end = to_complex(tf.dot(to_point(curve.end)))
        
        # Based on https://math.stackexchange.com/questions/2349726/
        rx2 = curve.radius.real ** 2
        ry2 = curve.radius.imag ** 2

        Q = np.array([[1/rx2, 0], [0, 1/ry2]])
        invT = np.linalg.inv(tf[:2,:2])
        D = reduce(np.matmul, [invT.T, Q, invT])

        eigvals, eigvecs = np.linalg.eigh(0.5*(D+D.T))  # symmetrized in case of floating point error; D already symmetric

        rx = 1 / np.sqrt(eigvals[0])
        ry = 1 / np.sqrt(eigvals[1])

        new_radius = complex(rx, ry)

        xeigvec = eigvecs[:, 0]
        rot = np.degrees(np.arctan2(xeigvec[1], xeigvec[0]))

        if new_radius.real == 0 or new_radius.imag == 0 :
            return Line(new_start, new_end)
        else:
            if tf[0][0] * tf[1][1] >= 0.0:
                new_sweep = curve.sweep
            else:
                new_sweep = not curve.sweep
            return Arc(new_start, radius=new_radius, rotation=curve.rotation + rot,
                       large_arc=curve.large_arc, sweep=new_sweep, end=new_end,
                       autoscale_radius=True)

    else:
        raise TypeError("Input `curve` should be a Path, Line, "
                        "QuadraticBezier, CubicBezier, or Arc object.")


def bezier_unit_tangent(seg, t):
    """Returns the unit tangent of the segment at t.

    Notes
    -----
    If you receive a RuntimeWarning, try the following:
    >>> import numpy
    >>> old_numpy_error_settings = numpy.seterr(invalid='raise')
    This can be undone with:
    >>> numpy.seterr(**old_numpy_error_settings)
    """

    dseg = seg.derivative(t)

    # Note: dseg might be numpy value, use np.seterr(invalid='raise')
    try:
        unit_tangent = dseg/abs(dseg)
    except (ZeroDivisionError, FloatingPointError):
        # This may be a removable singularity, if so we just need to compute
        # the limit.
        # Note: limit{{dseg / abs(dseg)} = sqrt(limit{dseg**2 / abs(dseg)**2})
        dseg_poly = seg.poly().deriv()
        dseg_abs_squared_poly = (real(dseg_poly) ** 2 +
                                 imag(dseg_poly) ** 2)
        try:
            unit_tangent = csqrt(rational_limit(dseg_poly**2,
                                            dseg_abs_squared_poly, t))
        except ValueError:
            bef = seg.poly().deriv()(t - 1e-4)
            aft = seg.poly().deriv()(t + 1e-4)
            mes = ("Unit tangent appears to not be well-defined at "
                   "t = {}, \n".format(t) +
                   "seg.poly().deriv()(t - 1e-4) = {}\n".format(bef) +
                   "seg.poly().deriv()(t + 1e-4) = {}".format(aft))
            raise ValueError(mes)
    return unit_tangent


def segment_curvature(self, t, use_inf=False):
    """returns the curvature of the segment at t.

    Notes
    -----
    If you receive a RuntimeWarning, run command
    >>> old = np.seterr(invalid='raise')
    This can be undone with
    >>> np.seterr(**old)
    """

    dz = self.derivative(t)
    ddz = self.derivative(t, n=2)
    dx, dy = dz.real, dz.imag
    ddx, ddy = ddz.real, ddz.imag
    old_np_seterr = np.seterr(invalid='raise')
    try:
        kappa = abs(dx*ddy - dy*ddx)/sqrt(dx*dx + dy*dy)**3
    except (ZeroDivisionError, FloatingPointError):
        # tangent vector is zero at t, use polytools to find limit
        p = self.poly()
        dp = p.deriv()
        ddp = dp.deriv()
        dx, dy = real(dp), imag(dp)
        ddx, ddy = real(ddp), imag(ddp)
        f2 = (dx*ddy - dy*ddx)**2
        g2 = (dx*dx + dy*dy)**3
        lim2 = rational_limit(f2, g2, t)
        if lim2 < 0:  # impossible, must be numerical error
            return 0
        kappa = sqrt(lim2)
    finally:
        np.seterr(**old_np_seterr)
    return kappa


def bezier_radialrange(seg, origin, return_all_global_extrema=False):
    """returns the tuples (d_min, t_min) and (d_max, t_max) which minimize and
    maximize, respectively, the distance d = |self.point(t)-origin|.
    return_all_global_extrema:  Multiple such t_min or t_max values can exist.
    By default, this will only return one. Set return_all_global_extrema=True
    to return all such global extrema."""

    def _radius(tau):
        return abs(seg.point(tau) - origin)

    shifted_seg_poly = seg.poly() - origin
    r_squared = real(shifted_seg_poly) ** 2 + \
                imag(shifted_seg_poly) ** 2
    extremizers = [0, 1] + polyroots01(r_squared.deriv())
    extrema = [(_radius(t), t) for t in extremizers]

    if return_all_global_extrema:
        raise NotImplementedError
    else:
        seg_global_min = min(extrema, key=itemgetter(0))
        seg_global_max = max(extrema, key=itemgetter(0))
        return seg_global_min, seg_global_max


def closest_point_in_path(pt, path):
    """returns (|path.seg.point(t)-pt|, t, seg_idx) where t and seg_idx
    minimize the distance between pt and curve path[idx].point(t) for 0<=t<=1
    and any seg_idx.
    Warning:  Multiple such global minima can exist.  This will only return
    one."""
    return path.radialrange(pt)[0]


def farthest_point_in_path(pt, path):
    """returns (|path.seg.point(t)-pt|, t, seg_idx) where t and seg_idx
    maximize the distance between pt and curve path[idx].point(t) for 0<=t<=1
    and any seg_idx.
    :rtype : object
    :param pt:
    :param path:
    Warning:  Multiple such global maxima can exist.  This will only return
    one."""
    return path.radialrange(pt)[1]


def path_encloses_pt(pt, opt, path):
    """returns true if pt is a point enclosed by path (which must be a Path
    object satisfying path.isclosed==True).  opt is a point you know is
    NOT enclosed by path."""
    assert path.isclosed()
    intersections = Path(Line(pt, opt)).intersect(path)
    if len(intersections) % 2:
        return True
    else:
        return False


def segment_length(curve, start, end, start_point, end_point,
                   error=LENGTH_ERROR, min_depth=LENGTH_MIN_DEPTH, depth=0):
    """Recursively approximates the length by straight lines"""
    mid = (start + end)/2
    mid_point = curve.point(mid)
    length = abs(end_point - start_point)
    first_half = abs(mid_point - start_point)
    second_half = abs(end_point - mid_point)

    length2 = first_half + second_half
    if (length2 - length > error) or (depth < min_depth):
        # Calculate the length of each segment:
        depth += 1
        return (segment_length(curve, start, mid, start_point, mid_point,
                               error, min_depth, depth) +
                segment_length(curve, mid, end, mid_point, end_point,
                               error, min_depth, depth))
    # This is accurate enough.
    return length2


def inv_arclength(curve, s, s_tol=ILENGTH_S_TOL, maxits=ILENGTH_MAXITS,
                  error=ILENGTH_ERROR, min_depth=ILENGTH_MIN_DEPTH):
    """INPUT: curve should be a CubicBezier, Line, of Path of CubicBezier
    and/or Line objects.
    OUTPUT: Returns a float, t, such that the arc length of curve from 0 to
    t is approximately s.
    s_tol - exit when |s(t) - s| < s_tol where
        s(t) = seg.length(0, t, error, min_depth) and seg is either curve or,
        if curve is a Path object, then seg is a segment in curve.
    error - used to compute lengths of cubics and arcs
    min_depth - used to compute lengths of cubics and arcs
    Note:  This function is not designed to be efficient, but if it's slower
    than you need, make sure you have scipy installed."""

    curve_length = curve.length(error=error, min_depth=min_depth)
    assert curve_length > 0
    if not 0 <= s <= curve_length:
        raise ValueError("s is not in interval [0, curve.length()].")

    if s == 0:
        return 0
    if s == curve_length:
        return 1

    if isinstance(curve, Path):
        seg_lengths = [seg.length(error=error, min_depth=min_depth)
                       for seg in curve]
        lsum = 0
        # Find which segment the point we search for is located on
        for k, len_k in enumerate(seg_lengths):
            if lsum <= s <= lsum + len_k:
                t = inv_arclength(curve[k], s - lsum, s_tol=s_tol,
                                  maxits=maxits, error=error,
                                  min_depth=min_depth)
                return curve.t2T(k, t)
            lsum += len_k
        return 1

    elif isinstance(curve, Line):
        return s / curve.length(error=error, min_depth=min_depth)

    elif (isinstance(curve, QuadraticBezier) or
          isinstance(curve, CubicBezier) or
          isinstance(curve, Arc)):
        t_upper = 1
        t_lower = 0
        iteration = 0
        while iteration < maxits:
            iteration += 1
            t = (t_lower + t_upper)/2
            s_t = curve.length(t1=t, error=error, min_depth=min_depth)
            if abs(s_t - s) < s_tol:
                return t
            elif s_t < s:  # t too small
                t_lower = t
            else:  # s < s_t, t too big
                t_upper = t
            if t_upper == t_lower:
                warn("t is as close as a float can be to the correct value, "
                     "but |s(t) - s| = {} > s_tol".format(abs(s_t-s)))
                return t
        raise Exception("Maximum iterations reached with s(t) - s = {}."
                        "".format(s_t - s))
    else:
        raise TypeError("First argument must be a Line, QuadraticBezier, "
                        "CubicBezier, Arc, or Path object.")

# Operations###################################################################


def crop_bezier(seg, t0, t1):
    """Crop a copy of this `self` from `self.point(t0)` to `self.point(t1)`."""
    assert t0 < t1
    if t0 == 0:
        cropped_seg = seg.split(t1)[0]
    elif t1 == 1:
        cropped_seg = seg.split(t0)[1]
    else:
        pt1 = seg.point(t1)

        # trim off the 0 <= t < t0 part
        trimmed_seg = crop_bezier(seg, t0, 1)

        # find the adjusted t1 (i.e. the t1 such that
        # trimmed_seg.point(t1) ~= pt))and trim off the t1 < t <= 1 part
        t1_adj = trimmed_seg.radialrange(pt1)[0][1]
        cropped_seg = crop_bezier(trimmed_seg, 0, t1_adj)
    return cropped_seg


# Main Classes ################################################################


class Line(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __hash__(self) -> int:
        return hash((self.start, self.end))

    def __repr__(self):
        return 'Line(start=%s, end=%s)' % (self.start, self.end)

    def __eq__(self, other):
        if not isinstance(other, Line):
            return False
        return self.start == other.start and self.end == other.end

    def __ne__(self, other):
        if not isinstance(other, Line):
            return NotImplemented
        return not self == other

    def __getitem__(self, item):
        return self.bpoints()[item]

    def __len__(self):
        return 2

    def joins_smoothly_with(self, previous, wrt_parameterization=False):
        """Checks if this segment joins smoothly with previous segment.  By
        default, this only checks that this segment starts moving (at t=0) in
        the same direction (and from the same positive) as previous stopped
        moving (at t=1).  To check if the tangent magnitudes also match, set
        wrt_parameterization=True."""
        if wrt_parameterization:
            return self.start == previous.end and np.isclose(
                self.derivative(0), previous.derivative(1))
        else:
            return self.start == previous.end and np.isclose(
                self.unit_tangent(0), previous.unit_tangent(1))

    def point(self, t):
        """returns the coordinates of the Bezier curve evaluated at t."""
        distance = self.end - self.start
        return self.start + distance*t

    def points(self, ts):
        """Faster than running Path.point many times."""
        return self.poly()(ts)

    def length(self, t0=0, t1=1, error=None, min_depth=None):
        """returns the length of the line segment between t0 and t1."""
        return abs(self.end - self.start)*(t1-t0)

    def ilength(self, s, s_tol=ILENGTH_S_TOL, maxits=ILENGTH_MAXITS,
                error=ILENGTH_ERROR, min_depth=ILENGTH_MIN_DEPTH):
        """Returns a float, t, such that self.length(0, t) is approximately s.
        See the inv_arclength() docstring for more details."""
        return inv_arclength(self, s, s_tol=s_tol, maxits=maxits, error=error,
                             min_depth=min_depth)

    def bpoints(self):
        """returns the Bezier control points of the segment."""
        return self.start, self.end

    def poly(self, return_coeffs=False):
        """returns the line as a Polynomial object."""
        p = self.bpoints()
        coeffs = ([p[1] - p[0], p[0]])
        if return_coeffs:
            return coeffs
        else:
            return np.poly1d(coeffs)

    def derivative(self, t=None, n=1):
        """returns the nth derivative of the segment at t."""
        assert self.end != self.start
        if n == 1:
            return self.end - self.start
        elif n > 1:
            return 0
        else:
            raise ValueError("n should be a positive integer.")

    def unit_tangent(self, t=None):
        """returns the unit tangent of the segment at t."""
        assert self.end != self.start
        dseg = self.end - self.start
        return dseg/abs(dseg)

    def normal(self, t=None):
        """returns the (right hand rule) unit normal vector to self at t."""
        return -1j*self.unit_tangent(t)

    def curvature(self, t):
        """returns the curvature of the line, which is always zero."""
        return 0

    # def icurvature(self, kappa):
    #     """returns a list of t-values such that 0 <= t<= 1 and
    #     seg.curvature(t) = kappa."""
    #     if kappa:
    #         raise ValueError("The .icurvature() method for Line elements will "
    #                          "return an empty list if kappa is nonzero and "
    #                          "will raise this exception when kappa is zero as "
    #                          "this is true at every point on the line.")
    #     return []

    def reversed(self):
        """returns a copy of the Line object with its orientation reversed."""
        return Line(self.end, self.start)

    def intersect(self, other_seg, tol=None):
        """Finds the intersections of two segments.
        returns a list of tuples (t1, t2) such that
        self.point(t1) == other_seg.point(t2).
        Note: This will fail if the two segments coincide for more than a
        finite collection of points.
        tol is not used."""
        if isinstance(other_seg, (Line, QuadraticBezier, CubicBezier)):
            ob = [e.real for e in other_seg.bpoints()]
            sb = [e.real for e in self.bpoints()]
            if min(ob) > max(sb):
                return []
            if max(ob) < min(sb):
                return []
            ob = [e.imag for e in other_seg.bpoints()]
            sb = [e.imag for e in self.bpoints()]
            if min(ob) > max(sb):
                return []
            if max(ob) < min(sb):
                return []
        if isinstance(other_seg, Line):
            assert other_seg.end != other_seg.start and self.end != self.start
            assert self != other_seg
            # Solve the system [p1-p0, q1-q0]*[t1, t2]^T = q0 - p0
            # where self == Line(p0, p1) and other_seg == Line(q0, q1)
            a = (self.start.real, self.end.real)
            b = (self.start.imag, self.end.imag)
            c = (other_seg.start.real, other_seg.end.real)
            d = (other_seg.start.imag, other_seg.end.imag)
            denom = ((a[1] - a[0])*(d[0] - d[1]) -
                     (b[1] - b[0])*(c[0] - c[1]))
            if np.isclose(denom, 0):
                return []
            t1 = (c[0]*(b[0] - d[1]) -
                  c[1]*(b[0] - d[0]) -
                  a[0]*(d[0] - d[1]))/denom
            t2 = -(a[1]*(b[0] - d[0]) -
                   a[0]*(b[1] - d[0]) -
                   c[0]*(b[0] - b[1]))/denom
            if 0 <= t1 <= 1 and 0 <= t2 <= 1:
                return [(t1, t2)]
            return []
        elif isinstance(other_seg, QuadraticBezier):
            t2t1s = bezier_by_line_intersections(other_seg, self)
            return [(t1, t2) for t2, t1 in t2t1s]
        elif isinstance(other_seg, CubicBezier):
            t2t1s = bezier_by_line_intersections(other_seg, self)
            return [(t1, t2) for t2, t1 in t2t1s]
        elif isinstance(other_seg, Arc):
            t2t1s = other_seg.intersect(self)
            return [(t1, t2) for t2, t1 in t2t1s]
        elif isinstance(other_seg, Path):
            raise TypeError(
                "other_seg must be a path segment, not a Path object, use "
                "Path.intersect().")
        else:
            raise TypeError("other_seg must be a path segment.")

    def bbox(self):
        """returns the bounding box for the segment in the form
        (xmin, xmax, ymin, ymax)."""
        xmin = min(self.start.real, self.end.real)
        xmax = max(self.start.real, self.end.real)
        ymin = min(self.start.imag, self.end.imag)
        ymax = max(self.start.imag, self.end.imag)
        return xmin, xmax, ymin, ymax

    def point_to_t(self, point):
        """If the point lies on the Line, returns its `t` parameter.
        If the point does not lie on the Line, returns None."""

        # Single-precision floats have only 7 significant figures of
        # resolution, so test that we're within 6 sig figs.
        if np.isclose(point, self.start, rtol=0, atol=1e-6):
            return 0.0
        elif np.isclose(point, self.end, rtol=0, atol=1e-6):
            return 1.0

        # Finding the point "by hand" here is much faster than calling
        # radialrange(), see the discussion on PR #40:
        # https://github.com/mathandy/svgpathtools/pull/40#issuecomment-358134261

        p = self.poly()
        # p(t) = (p_1 * t) + p_0 = point
        # t = (point - p_0) / p_1
        t = (point - p[0]) / p[1]
        if np.isclose(t.imag, 0) and (t.real >= 0.0) and (t.real <= 1.0):
            return t.real
        return None

    def cropped(self, t0, t1):
        """returns a cropped copy of this segment which starts at
        self.point(t0) and ends at self.point(t1)."""
        return Line(self.point(t0), self.point(t1))

    def split(self, t):
        """returns two segments, whose union is this segment and which join at
        self.point(t)."""
        pt = self.point(t)
        return Line(self.start, pt), Line(pt, self.end)

    def radialrange(self, origin, **kwargs):
        """compute points in self that are min and max distance to origin.

        Args:
            origin (complex): the point extremize distance to

        Returns:
            tuples (d_min, t_min) and (d_max, t_max) which minimize and
            maximize, respectively, the distance d = |self.point(t)-origin|.
        """

        x, y = origin.real, origin.imag
        p0, p1 = self.start, self.end
        x0, y0, x1, y1 = p0.real, p0.imag, p1.real, p1.imag

        dx, dy = x1 - x0, y1 - y0
        numerator, denominator = dx * (x - x0) + dy * (y - y0), dx * dx + dy * dy
        t = numerator / denominator

        if 0 < t < 1:
            # get distance to origin at 0, 1, and t
            d0, d1, dt = (
                abs(p0 - origin),
                abs(p1 - origin),
                abs(self.point(t) - origin)
            )
            if d0 < d1:
                return (dt, t), (d1, 1)
            return (dt, t), (d0, 0)
        else:
            # get distance to origin at t = 0 and t = 1
            d0, d1 = abs(p0 - origin), abs(p1 - origin)
            if d0 < d1:
                return (d0, 0), (d1, 1)
            return (d1, 1), (d0, 0)

    def rotated(self, degs, origin=None):
        """Returns a copy of self rotated by `degs` degrees (CCW) around the
        point `origin` (a complex number).  By default `origin` is either
        `self.point(0.5)`, or in the case that self is an Arc object,
        `origin` defaults to `self.center`."""
        return rotate(self, degs, origin=origin)

    def translated(self, z0):
        """Returns a copy of self shifted by the complex quantity `z0` such
        that self.translated(z0).point(t) = self.point(t) + z0 for any t."""
        return translate(self, z0)

    def scaled(self, sx, sy=None, origin=0j):
        """Scale transform.  See `scale` function for further explanation."""
        return scale(self, sx=sx, sy=sy, origin=origin)


class QuadraticBezier(object):
    # For compatibility with old pickle files.
    _length_info = {'length': None, 'bpoints': None}

    def __init__(self, start, control, end):
        self.start = start
        self.end = end
        self.control = control

        # used to know if self._length needs to be updated
        self._length_info = {'length': None, 'bpoints': None}

    def __hash__(self) -> int:
        return hash((self.start, self.control, self.end))

    def __repr__(self):
        return 'QuadraticBezier(start=%s, control=%s, end=%s)' % (
            self.start, self.control, self.end)

    def __eq__(self, other):
        if not isinstance(other, QuadraticBezier):
            return False
        return self.start == other.start and self.end == other.end \
            and self.control == other.control

    def __ne__(self, other):
        if not isinstance(other, QuadraticBezier):
            return NotImplemented
        return not self == other

    def __getitem__(self, item):
        return self.bpoints()[item]

    def __len__(self):
        return 3

    def is_smooth_from(self, previous, warning_on=True):
        """[Warning: The name of this method is somewhat misleading (yet kept
        for compatibility with scripts created using svg.path 2.0).  This
        method is meant only for d string creation and should not be used to
        check for kinks.  To check a segment for differentiability, use the
        joins_smoothly_with() method instead.]"""
        if warning_on:
            warn(_is_smooth_from_warning)
        if isinstance(previous, QuadraticBezier):
            return (self.start == previous.end and
                    (self.control - self.start) == (
                        previous.end - previous.control))
        else:
            return self.control == self.start

    def joins_smoothly_with(self, previous, wrt_parameterization=False,
                            error=0):
        """Checks if this segment joins smoothly with previous segment.  By
        default, this only checks that this segment starts moving (at t=0) in
        the same direction (and from the same positive) as previous stopped
        moving (at t=1).  To check if the tangent magnitudes also match, set
        wrt_parameterization=True."""
        if wrt_parameterization:
            return self.start == previous.end and abs(
                self.derivative(0) - previous.derivative(1)) <= error
        else:
            return self.start == previous.end and abs(
                self.unit_tangent(0) - previous.unit_tangent(1)) <= error

    def point(self, t):
        """returns the coordinates of the Bezier curve evaluated at t."""
        tc = 1 - t
        return tc*tc*self.start + 2*tc*t*self.control + t*t*self.end

    def points(self, ts):
        """Faster than running Path.point many times."""
        return self.poly()(ts)

    def length(self, t0=0, t1=1, error=None, min_depth=None):
        if t0 == 1 and t1 == 0:
            if self._length_info['bpoints'] == self.bpoints():
                return self._length_info['length']
        a = self.start - 2*self.control + self.end
        b = 2*(self.control - self.start)
        a_dot_b = a.real*b.real + a.imag*b.imag

        if abs(a) < 1e-12:
            s = abs(b)*(t1 - t0)
        else:
            c2 = 4 * (a.real ** 2 + a.imag ** 2)
            c1 = 4 * a_dot_b
            c0 = b.real ** 2 + b.imag ** 2

            beta = c1 / (2 * c2)
            gamma = c0 / c2 - beta ** 2

            dq1_mag = sqrt(c2 * t1 ** 2 + c1 * t1 + c0)
            dq0_mag = sqrt(c2 * t0 ** 2 + c1 * t0 + c0)
            rand_num = sqrt(c2) * (t1 + beta) + dq1_mag
            rand_den = sqrt(c2) * (t0 + beta) + dq0_mag
            logarand = log(rand_num / rand_den) if rand_den != 0 else 0
            s = (t1 + beta) * dq1_mag - (t0 + beta) * dq0_mag + \
                gamma * sqrt(c2) * logarand
            s /= 2
            if isnan(s):
                tstar = abs(b) / (2 * abs(a))
                if t1 < tstar:
                    return abs(a) * (t0 ** 2 - t1 ** 2) - abs(b) * (t0 - t1)
                elif tstar < t0:
                    return abs(a) * (t1 ** 2 - t0 ** 2) - abs(b) * (t1 - t0)
                else:
                    return abs(a) * (t1 ** 2 + t0 ** 2) - abs(b) * (t1 + t0) + \
                           abs(b) ** 2 / (2 * abs(a))

        if t0 == 1 and t1 == 0:
            self._length_info['length'] = s
            self._length_info['bpoints'] = self.bpoints()
            return self._length_info['length']
        else:
            return s

    def ilength(self, s, s_tol=ILENGTH_S_TOL, maxits=ILENGTH_MAXITS,
                error=ILENGTH_ERROR, min_depth=ILENGTH_MIN_DEPTH):
        """Returns a float, t, such that self.length(0, t) is approximately s.
        See the inv_arclength() docstring for more details."""
        return inv_arclength(self, s, s_tol=s_tol, maxits=maxits, error=error,
                             min_depth=min_depth)

    def bpoints(self):
        """returns the Bezier control points of the segment."""
        return self.start, self.control, self.end

    def poly(self, return_coeffs=False):
        """returns the quadratic as a Polynomial object."""
        p = self.bpoints()
        coeffs = (p[0] - 2*p[1] + p[2], 2*(p[1] - p[0]), p[0])
        if return_coeffs:
            return coeffs
        else:
            return np.poly1d(coeffs)

    def derivative(self, t, n=1):
        """returns the nth derivative of the segment at t.
        Note: Bezier curves can have points where their derivative vanishes.
        If you are interested in the tangent direction, use the unit_tangent()
        method instead."""
        p = self.bpoints()
        if n == 1:
            return 2*((p[1] - p[0])*(1 - t) + (p[2] - p[1])*t)
        elif n == 2:
            return 2*(p[2] - 2*p[1] + p[0])
        elif n > 2:
            return 0
        else:
            raise ValueError("n should be a positive integer.")

    def unit_tangent(self, t):
        """returns the unit tangent vector of the segment at t (centered at
        the origin and expressed as a complex number).  If the tangent
        vector's magnitude is zero, this method will find the limit of
        self.derivative(tau)/abs(self.derivative(tau)) as tau approaches t."""
        return bezier_unit_tangent(self, t)

    def normal(self, t):
        """returns the (right hand rule) unit normal vector to self at t."""
        return -1j*self.unit_tangent(t)

    def curvature(self, t):
        """returns the curvature of the segment at t."""
        return segment_curvature(self, t)

    # def icurvature(self, kappa):
    #     """returns a list of t-values such that 0 <= t<= 1 and
    #     seg.curvature(t) = kappa."""
    #     z = self.poly()
    #     x, y = real(z), imag(z)
    #     dx, dy = x.deriv(), y.deriv()
    #     ddx, ddy = dx.deriv(), dy.deriv()
    #
    #     p = kappa**2*(dx**2 + dy**2)**3 - (dx*ddy - ddx*dy)**2
    #     return polyroots01(p)

    def reversed(self):
        """returns a copy of the QuadraticBezier object with its orientation
        reversed."""
        new_quad = QuadraticBezier(self.end, self.control, self.start)
        if self._length_info['length']:
            new_quad._length_info = self._length_info
            new_quad._length_info['bpoints'] = (
                self.end, self.control, self.start)
        return new_quad

    def intersect(self, other_seg, tol=1e-12):
        """Finds the intersections of two segments.
        returns a list of tuples (t1, t2) such that
        self.point(t1) == other_seg.point(t2).
        Note: This will fail if the two segments coincide for more than a
        finite collection of points."""
        if isinstance(other_seg, (Line, QuadraticBezier, CubicBezier)):
            ob = [e.real for e in other_seg.bpoints()]
            sb = [e.real for e in self.bpoints()]
            if min(ob) > max(sb):
                return []
            if max(ob) < min(sb):
                return []
            ob = [e.imag for e in other_seg.bpoints()]
            sb = [e.imag for e in self.bpoints()]
            if min(ob) > max(sb):
                return []
            if max(ob) < min(sb):
                return []
        if isinstance(other_seg, Line):
            return bezier_by_line_intersections(self, other_seg)
        elif isinstance(other_seg, QuadraticBezier):
            assert self != other_seg
            longer_length = max(self.length(), other_seg.length())
            return bezier_intersections(self, other_seg,
                                        longer_length=longer_length,
                                        tol=tol, tol_deC=tol)
        elif isinstance(other_seg, CubicBezier):
            longer_length = max(self.length(), other_seg.length())
            return bezier_intersections(self, other_seg,
                                        longer_length=longer_length,
                                        tol=tol, tol_deC=tol)
        elif isinstance(other_seg, Arc):
            t2t1s = other_seg.intersect(self)
            return [(t1, t2) for t2, t1 in t2t1s]
        elif isinstance(other_seg, Path):
            raise TypeError(
                "other_seg must be a path segment, not a Path object, use "
                "Path.intersect().")
        else:
            raise TypeError("other_seg must be a path segment.")

    def bbox(self):
        """returns the bounding box for the segment in the form
        (xmin, xmax, ymin, ymax)."""
        return bezier_bounding_box(self)

    def split(self, t):
        """returns two segments, whose union is this segment and which join at
        self.point(t)."""
        bpoints1, bpoints2 = split_bezier(self.bpoints(), t)
        return QuadraticBezier(*bpoints1), QuadraticBezier(*bpoints2)

    def cropped(self, t0, t1):
        """returns a cropped copy of this segment which starts at
        self.point(t0) and ends at self.point(t1)."""
        return QuadraticBezier(*crop_bezier(self, t0, t1))

    def radialrange(self, origin, return_all_global_extrema=False):
        """returns the tuples (d_min, t_min) and (d_max, t_max) which minimize
        and maximize, respectively, the distance d = |self.point(t)-origin|."""
        return bezier_radialrange(self, origin,
                return_all_global_extrema=return_all_global_extrema)

    def rotated(self, degs, origin=None):
        """Returns a copy of self rotated by `degs` degrees (CCW) around the
        point `origin` (a complex number).  By default `origin` is either
        `self.point(0.5)`, or in the case that self is an Arc object,
        `origin` defaults to `self.center`."""
        return rotate(self, degs, origin=origin)

    def translated(self, z0):
        """Returns a copy of self shifted by the complex quantity `z0` such
        that self.translated(z0).point(t) = self.point(t) + z0 for any t."""
        return translate(self, z0)

    def scaled(self, sx, sy=None, origin=0j):
        """Scale transform.  See `scale` function for further explanation."""
        return scale(self, sx=sx, sy=sy, origin=origin)


class CubicBezier(object):
    # For compatibility with old pickle files.
    _length_info = {'length': None, 'bpoints': None, 'error': None,
                    'min_depth': None}

    def __init__(self, start, control1, control2, end):
        self.start = start
        self.control1 = control1
        self.control2 = control2
        self.end = end

        # used to know if self._length needs to be updated
        self._length_info = {'length': None, 'bpoints': None, 'error': None,
                             'min_depth': None}

    def __hash__(self) -> int:
        return hash((self.start, self.control1, self.control2, self.end))

    def __repr__(self):
        return 'CubicBezier(start=%s, control1=%s, control2=%s, end=%s)' % (
            self.start, self.control1, self.control2, self.end)

    def __eq__(self, other):
        if not isinstance(other, CubicBezier):
            return False
        return self.start == other.start and self.end == other.end \
            and self.control1 == other.control1 \
            and self.control2 == other.control2

    def __ne__(self, other):
        if not isinstance(other, CubicBezier):
            return NotImplemented
        return not self == other

    def __getitem__(self, item):
        return self.bpoints()[item]

    def __len__(self):
        return 4

    def is_smooth_from(self, previous, warning_on=True):
        """[Warning: The name of this method is somewhat misleading (yet kept
        for compatibility with scripts created using svg.path 2.0).  This
        method is meant only for d string creation and should not be used to
        check for kinks.  To check a segment for differentiability, use the
        joins_smoothly_with() method instead.]"""
        if warning_on:
            warn(_is_smooth_from_warning)
        if isinstance(previous, CubicBezier):
            return (self.start == previous.end and
                    (self.control1 - self.start) == (
                        previous.end - previous.control2))
        else:
            return self.control1 == self.start

    def joins_smoothly_with(self, previous, wrt_parameterization=False):
        """Checks if this segment joins smoothly with previous segment.  By
        default, this only checks that this segment starts moving (at t=0) in
        the same direction (and from the same positive) as previous stopped
        moving (at t=1).  To check if the tangent magnitudes also match, set
        wrt_parameterization=True."""
        if wrt_parameterization:
            return self.start == previous.end and np.isclose(
                self.derivative(0), previous.derivative(1))
        else:
            return self.start == previous.end and np.isclose(
                self.unit_tangent(0), previous.unit_tangent(1))

    def point(self, t):
        """Evaluate the cubic Bezier curve at t using Horner's rule."""
        # algebraically equivalent to
        # P0*(1-t)**3 + 3*P1*t*(1-t)**2 + 3*P2*(1-t)*t**2 + P3*t**3
        # for (P0, P1, P2, P3) = self.bpoints()
        return self.start + t*(
            3*(self.control1 - self.start) + t*(
                3*(self.start + self.control2) - 6*self.control1 + t*(
                    -self.start + 3*(self.control1 - self.control2) + self.end
                )))

    def points(self, ts):
        """Faster than running Path.point many times."""
        return self.poly()(ts)

    def length(self, t0=0, t1=1, error=LENGTH_ERROR, min_depth=LENGTH_MIN_DEPTH):
        """Calculate the length of the path up to a certain position"""
        if t0 == 0 and t1 == 1:
            if self._length_info['bpoints'] == self.bpoints() \
                    and self._length_info['error'] >= error \
                    and self._length_info['min_depth'] >= min_depth:
                return self._length_info['length']

        # using scipy.integrate.quad is quick
        if _quad_available:
            s = quad(lambda tau: abs(self.derivative(tau)), t0, t1,
                            epsabs=error, limit=1000)[0]
        else:
            s = segment_length(self, t0, t1, self.point(t0), self.point(t1),
                               error, min_depth, 0)

        if t0 == 0 and t1 == 1:
            self._length_info['length'] = s
            self._length_info['bpoints'] = self.bpoints()
            self._length_info['error'] = error
            self._length_info['min_depth'] = min_depth
            return self._length_info['length']
        else:
            return s

    def ilength(self, s, s_tol=ILENGTH_S_TOL, maxits=ILENGTH_MAXITS,
                error=ILENGTH_ERROR, min_depth=ILENGTH_MIN_DEPTH):
        """Returns a float, t, such that self.length(0, t) is approximately s.
        See the inv_arclength() docstring for more details."""
        return inv_arclength(self, s, s_tol=s_tol, maxits=maxits, error=error,
                             min_depth=min_depth)

    def bpoints(self):
        """returns the Bezier control points of the segment."""
        return self.start, self.control1, self.control2, self.end

    def poly(self, return_coeffs=False):
        """Returns a the cubic as a Polynomial object."""
        p = self.bpoints()
        coeffs = (-p[0] + 3*(p[1] - p[2]) + p[3],
                  3*(p[0] - 2*p[1] + p[2]),
                  3*(-p[0] + p[1]),
                  p[0])
        if return_coeffs:
            return coeffs
        else:
            return np.poly1d(coeffs)

    def derivative(self, t, n=1):
        """returns the nth derivative of the segment at t.
        Note: Bezier curves can have points where their derivative vanishes.
        If you are interested in the tangent direction, use the unit_tangent()
        method instead."""
        p = self.bpoints()
        if n == 1:
            return 3*(p[1] - p[0])*(1 - t)**2 + 6*(p[2] - p[1])*(1 - t)*t + 3*(
                p[3] - p[2])*t**2
        elif n == 2:
            return 6*(
                (1 - t)*(p[2] - 2*p[1] + p[0]) + t*(p[3] - 2*p[2] + p[1]))
        elif n == 3:
            return 6*(p[3] - 3*(p[2] - p[1]) - p[0])
        elif n > 3:
            return 0
        else:
            raise ValueError("n should be a positive integer.")

    def unit_tangent(self, t):
        """returns the unit tangent vector of the segment at t (centered at
        the origin and expressed as a complex number).  If the tangent
        vector's magnitude is zero, this method will find the limit of
        self.derivative(tau)/abs(self.derivative(tau)) as tau approaches t."""
        return bezier_unit_tangent(self, t)

    def normal(self, t):
        """returns the (right hand rule) unit normal vector to self at t."""
        return -1j * self.unit_tangent(t)

    def curvature(self, t):
        """returns the curvature of the segment at t."""
        return segment_curvature(self, t)

    # def icurvature(self, kappa):
    #     """returns a list of t-values such that 0 <= t<= 1 and
    #     seg.curvature(t) = kappa."""
    #     z = self.poly()
    #     x, y = real(z), imag(z)
    #     dx, dy = x.deriv(), y.deriv()
    #     ddx, ddy = dx.deriv(), dy.deriv()
    #
    #     p = kappa**2*(dx**2 + dy**2)**3 - (dx*ddy - ddx*dy)**2
    #     return polyroots01(p)

    def reversed(self):
        """returns a copy of the CubicBezier object with its orientation
        reversed."""
        new_cub = CubicBezier(self.end, self.control2, self.control1,
                              self.start)
        if self._length_info['length']:
            new_cub._length_info = self._length_info
            new_cub._length_info['bpoints'] = (
                self.end, self.control2, self.control1, self.start)
        return new_cub

    def intersect(self, other_seg, tol=1e-12):
        """Finds the intersections of two segments.

        Returns:
            (list[tuple[float]]) a list of tuples (t1, t2) such that
            self.point(t1) == other_seg.point(t2).

        Scope:
            This will fail if the two segments coincide for more than a
            finite collection of points.
        """
        if isinstance(other_seg, (Line, QuadraticBezier, CubicBezier)):
            ob = [e.real for e in other_seg.bpoints()]
            sb = [e.real for e in self.bpoints()]
            if min(ob) > max(sb):
                return []
            if max(ob) < min(sb):
                return []
            ob = [e.imag for e in other_seg.bpoints()]
            sb = [e.imag for e in self.bpoints()]
            if min(ob) > max(sb):
                return []
            if max(ob) < min(sb):
                return []
        if isinstance(other_seg, Line):
            return bezier_by_line_intersections(self, other_seg)
        elif (isinstance(other_seg, QuadraticBezier) or
              isinstance(other_seg, CubicBezier)):
            assert self != other_seg
            longer_length = max(self.length(), other_seg.length())
            return bezier_intersections(
                self, other_seg, longer_length=longer_length, tol=tol, tol_deC=tol
            )
        elif isinstance(other_seg, Arc):
            return [(t1, t2) for t2, t1 in other_seg.intersect(self)]
        elif isinstance(other_seg, Path):
            raise TypeError("`other_seg` must be a path segment, not a "
                            "`Path` object, use `Path.intersect()`.")
        else:
            raise TypeError("`other_seg` must be a path segment.")

    def bbox(self):
        """returns bounding box in format (xmin, xmax, ymin, ymax)."""
        return bezier_bounding_box(self)

    def split(self, t):
        """Splits a copy of `self` at t and returns the two subsegments."""
        bpoints1, bpoints2 = split_bezier(self.bpoints(), t)
        return CubicBezier(*bpoints1), CubicBezier(*bpoints2)

    def cropped(self, t0, t1):
        """returns a cropped copy of this segment which starts at
        self.point(t0) and ends at self.point(t1)."""
        return CubicBezier(*crop_bezier(self, t0, t1))

    def radialrange(self, origin, return_all_global_extrema=False):
        """returns the tuples (d_min, t_min) and (d_max, t_max) which minimize
        and maximize, respectively, the distance d = |self.point(t)-origin|."""
        return bezier_radialrange(
            self, origin, return_all_global_extrema=return_all_global_extrema)

    def rotated(self, degs, origin=None):
        """Returns a copy of self rotated by `degs` degrees (CCW) around the
        point `origin` (a complex number).  By default `origin` is either
        `self.point(0.5)`, or in the case that self is an Arc object,
        `origin` defaults to `self.center`."""
        return rotate(self, degs, origin=origin)

    def translated(self, z0):
        """Returns a copy of self shifted by the complex quantity `z0` such
        that self.translated(z0).point(t) = self.point(t) + z0 for any t."""
        return translate(self, z0)

    def scaled(self, sx, sy=None, origin=0j):
        """Scale transform.  See `scale` function for further explanation."""
        return scale(self, sx=sx, sy=sy, origin=origin)


class Arc(object):
    def __init__(self, start, radius, rotation, large_arc, sweep, end,
                 autoscale_radius=True):
        r"""
        This should be thought of as a part of an ellipse connecting two
        points on that ellipse, start and end.
        Parameters
        ----------
        start : complex
            The start point of the curve. Note: `start` and `end` cannot be the
            same.  To make a full ellipse or circle, use two `Arc` objects.
        radius : complex
            rx + 1j*ry, where rx and ry are the radii of the ellipse (also
            known as its semi-major and semi-minor axes, or vice-versa or if
            rx < ry).
            Note: If rx = 0 or ry = 0 then this arc is treated as a
            straight line segment joining the endpoints.
            Note: If rx or ry has a negative sign, the sign is dropped; the
            absolute value is used instead.
            Note:  If no such ellipse exists, the radius will be scaled so
            that one does (unless autoscale_radius is set to False).
        rotation : float
            This is the CCW angle (in degrees) from the positive x-axis of the
            current coordinate system to the x-axis of the ellipse.
        large_arc : bool
            Given two points on an ellipse, there are two elliptical arcs
            connecting those points, the first going the short way around the
            ellipse, and the second going the long way around the ellipse.  If
            `large_arc == False`, the shorter elliptical arc will be used.  If
            `large_arc == True`, then longer elliptical will be used.
            In other words, `large_arc` should be 0 for arcs spanning less than
            or equal to 180 degrees and 1 for arcs spanning greater than 180
            degrees.
        sweep : bool
            For any acceptable parameters `start`, `end`, `rotation`, and
            `radius`, there are two ellipses with the given major and minor
            axes (radii) which connect `start` and `end`.  One which connects
            them in a CCW fashion and one which connected them in a CW
            fashion.  If `sweep == True`, the CCW ellipse will be used.  If
            `sweep == False`, the CW ellipse will be used.  See note on curve
            orientation below.
        end : complex
            The end point of the curve. Note: `start` and `end` cannot be the
            same.  To make a full ellipse or circle, use two `Arc` objects.
        autoscale_radius : bool
            If `autoscale_radius == True`, then will also scale `self.radius`
            in the case that no ellipse exists with the input parameters
            (see inline comments for further explanation).

        Derived Parameters/Attributes
        -----------------------------
        self.theta : float
            This is the phase (in degrees) of self.u1transform(self.start).
            It is $\theta_1$ in the official documentation and ranges from
            -180 to 180.
        self.delta : float
            This is the angular distance (in degrees) between the start and
            end of the arc after the arc has been sent to the unit circle
            through self.u1transform().
            It is $\Delta\theta$ in the official documentation and ranges from
            -360 to 360; being positive when the arc travels CCW and negative
            otherwise (i.e. is positive/negative when sweep == True/False).
        self.center : complex
            This is the center of the arc's ellipse.
        self.phi : float
            The arc's rotation in radians, i.e. `radians(self.rotation)`.
        self.rot_matrix : complex
            Equal to `exp(1j * self.phi)` which is also equal to
            `cos(self.phi) + 1j*sin(self.phi)`.


        Note on curve orientation (CW vs CCW)
        -------------------------------------
        The notions of clockwise (CW) and counter-clockwise (CCW) are reversed
        in some sense when viewing SVGs (as the y coordinate starts at the top
        of the image and increases towards the bottom).
        """
        assert start != end
        assert radius.real != 0 and radius.imag != 0

        self.start = start
        self.radius = abs(radius.real) + 1j*abs(radius.imag)
        self.rotation = rotation
        self.large_arc = bool(large_arc)
        self.sweep = bool(sweep)
        self.end = end
        self.autoscale_radius = autoscale_radius

        self.segment_length_hash = None
        self.segment_length = None

        # Convenience parameters
        self.phi = radians(self.rotation)
        self.rot_matrix = exp(1j*self.phi)

        # Derive derived parameters
        self._parameterize()

    def apoints(self) -> tuple[complex, complex, float, bool, bool, complex]:
        """Analog of the Bezier path method, .bpoints(), for Arc objects."""
        return self.start, self.radius, self.rotation, self.large_arc, self.sweep, self.end

    def __hash__(self) -> int:
        return hash(self.apoints())

    def __repr__(self):
        params = (self.start, self.radius, self.rotation,
                  self.large_arc, self.sweep, self.end)
        return ("Arc(start={}, radius={}, rotation={}, "
                "large_arc={}, sweep={}, end={})".format(*params))

    def __eq__(self, other):
        if not isinstance(other, Arc):
            return False
        return self.start == other.start and self.end == other.end \
            and self.radius == other.radius \
            and self.rotation == other.rotation \
            and self.large_arc == other.large_arc and self.sweep == other.sweep

    def __ne__(self, other):
        if not isinstance(other, Arc):
            return NotImplemented
        return not self == other

    def _parameterize(self):
        # See http://www.w3.org/TR/SVG/implnote.html#ArcImplementationNotes
        # my notation roughly follows theirs
        rx = self.radius.real
        ry = self.radius.imag
        rx_sqd = rx*rx
        ry_sqd = ry*ry

        # Transform z-> z' = x' + 1j*y'
        # = self.rot_matrix**(-1)*(z - (end+start)/2)
        # coordinates.  This translates the ellipse so that the midpoint
        # between self.end and self.start lies on the origin and rotates
        # the ellipse so that the its axes align with the xy-coordinate axes.
        # Note:  This sends self.end to -self.start
        zp1 = (1/self.rot_matrix)*(self.start - self.end)/2
        x1p, y1p = zp1.real, zp1.imag
        x1p_sqd = x1p*x1p
        y1p_sqd = y1p*y1p

        # Correct out of range radii
        # Note: an ellipse going through start and end with radius and phi
        # exists if and only if radius_check is true
        radius_check = (x1p_sqd/rx_sqd) + (y1p_sqd/ry_sqd)
        if radius_check > 1:
            if self.autoscale_radius:
                rx *= sqrt(radius_check)
                ry *= sqrt(radius_check)
                self.radius = rx + 1j*ry
                rx_sqd = rx*rx
                ry_sqd = ry*ry
            else:
                raise ValueError("No such elliptic arc exists.")

        # Compute c'=(c_x', c_y'), the center of the ellipse in (x', y') coords
        # Noting that, in our new coord system, (x_2', y_2') = (-x_1', -x_2')
        # and our ellipse is cut out by of the plane by the algebraic equation
        # (x'-c_x')**2 / r_x**2 + (y'-c_y')**2 / r_y**2 = 1,
        # we can find c' by solving the system of two quadratics given by
        # plugging our transformed endpoints (x_1', y_1') and (x_2', y_2')
        tmp = rx_sqd*y1p_sqd + ry_sqd*x1p_sqd
        radicand = (rx_sqd*ry_sqd - tmp) / tmp
        radical = 0 if np.isclose(radicand, 0) else sqrt(radicand)

        if self.large_arc == self.sweep:
            cp = -radical*(rx*y1p/ry - 1j*ry*x1p/rx)
        else:
            cp = radical*(rx*y1p/ry - 1j*ry*x1p/rx)

        # The center in (x,y) coordinates is easy to find knowing c'
        self.center = exp(1j*self.phi)*cp + (self.start + self.end)/2

        # Now we do a second transformation, from (x', y') to (u_x, u_y)
        # coordinates, which is a translation moving the center of the
        # ellipse to the origin and a dilation stretching the ellipse to be
        # the unit circle
        u1 = (x1p - cp.real)/rx + 1j*(y1p - cp.imag)/ry  # transformed start
        u2 = (-x1p - cp.real)/rx + 1j*(-y1p - cp.imag)/ry  # transformed end

        # clip in case of floating point error
        u1 = np.clip(u1.real, -1, 1) + 1j*np.clip(u1.imag, -1, 1)
        u2 = np.clip(u2.real, -1, 1) + 1j * np.clip(u2.imag, -1, 1)

        # Now compute theta and delta (we'll define them as we go)
        # delta is the angular distance of the arc (w.r.t the circle)
        # theta is the angle between the positive x'-axis and the start point
        # on the circle
        if u1.imag > 0:
            self.theta = degrees(acos(u1.real))
        elif u1.imag < 0:
            self.theta = -degrees(acos(u1.real))
        else:
            if u1.real > 0:  # start is on pos u_x axis
                self.theta = 0
            else:  # start is on neg u_x axis
                # Note: This behavior disagrees with behavior documented in
                # http://www.w3.org/TR/SVG/implnote.html#ArcImplementationNotes
                # where theta is set to 0 in this case.
                self.theta = 180

        det_uv = u1.real*u2.imag - u1.imag*u2.real

        acosand = u1.real*u2.real + u1.imag*u2.imag
        acosand = np.clip(acosand.real, -1, 1) + np.clip(acosand.imag, -1, 1)
        
        if det_uv > 0:
            self.delta = degrees(acos(acosand))
        elif det_uv < 0:
            self.delta = -degrees(acos(acosand))
        else:
            if u1.real*u2.real + u1.imag*u2.imag > 0:
                # u1 == u2
                self.delta = 0
            else:
                # u1 == -u2
                # Note: This behavior disagrees with behavior documented in
                # http://www.w3.org/TR/SVG/implnote.html#ArcImplementationNotes
                # where delta is set to 0 in this case.
                self.delta = 180

        if not self.sweep and self.delta >= 0:
            self.delta -= 360
        elif self.large_arc and self.delta <= 0:
            self.delta += 360

    def point(self, t):

        angle = (self.theta + t*self.delta)*pi/180
        cosphi = self.rot_matrix.real
        sinphi = self.rot_matrix.imag
        rx = self.radius.real
        ry = self.radius.imag

        x = rx*cosphi*cos(angle) - ry*sinphi*sin(angle) + self.center.real
        y = rx*sinphi*cos(angle) + ry*cosphi*sin(angle) + self.center.imag
        return x + y*1j

    def point_to_t(self, point):
        """If the point lies on the Arc, returns its `t` parameter.
        If the point does not lie on the Arc, returns None.
        This function only works on Arcs with rotation == 0.0"""

        def in_range(min, max, val):
            return (min <= val) and (max >= val)

        # Single-precision floats have only 7 significant figures of
        # resolution, so test that we're within 6 sig figs.
        if np.isclose(point, self.start, rtol=0.0, atol=1e-6):
            return 0.0
        elif np.isclose(point, self.end, rtol=0.0, atol=1e-6):
            return 1.0

        if self.rotation != 0.0:
            raise ValueError("Arc.point_to_t() only works on non-rotated Arcs.")

        v = point - self.center
        distance_from_center = sqrt((v.real * v.real) + (v.imag * v.imag))
        min_radius = min(self.radius.real, self.radius.imag)
        max_radius = max(self.radius.real, self.radius.imag)
        if (distance_from_center < min_radius) and not np.isclose(distance_from_center, min_radius):
            return None
        if (distance_from_center > max_radius) and not np.isclose(distance_from_center, max_radius):
            return None

        # x = center_x + radius_x cos(radians(theta + t delta))
        # y = center_y + radius_y sin(radians(theta + t delta))
        #
        # For x:
        # cos(radians(theta + t delta)) = (x - center_x) / radius_x
        # radians(theta + t delta) = acos((x - center_x) / radius_x)
        # theta + t delta = degrees(acos((x - center_x) / radius_x))
        # t_x = (degrees(acos((x - center_x) / radius_x)) - theta) / delta
        #
        # Similarly for y:
        # t_y = (degrees(asin((y - center_y) / radius_y)) - theta) / delta

        x = point.real
        y = point.imag

        #
        # +Y points down!
        #
        # sweep mean clocwise
        # sweep && (delta > 0)
        # !sweep && (delta < 0)
        #
        # -180 <= theta_1 <= 180
        #
        # large_arc && (-360 <= delta <= 360)
        # !large_arc && (-180 < delta < 180)
        #

        end_angle = self.theta + self.delta
        min_angle = min(self.theta, end_angle)
        max_angle = max(self.theta, end_angle)

        acos_arg = (x - self.center.real) / self.radius.real
        if acos_arg > 1.0:
            acos_arg = 1.0
        elif acos_arg < -1.0:
            acos_arg = -1.0

        x_angle_0 = degrees(acos(acos_arg))
        while x_angle_0 < min_angle:
            x_angle_0 += 360.0
        while x_angle_0 > max_angle:
            x_angle_0 -= 360.0

        x_angle_1 = -1.0 * x_angle_0
        while x_angle_1 < min_angle:
            x_angle_1 += 360.0
        while x_angle_1 > max_angle:
            x_angle_1 -= 360.0

        t_x_0 = (x_angle_0 - self.theta) / self.delta
        t_x_1 = (x_angle_1 - self.theta) / self.delta

        asin_arg = (y - self.center.imag) / self.radius.imag
        if asin_arg > 1.0:
            asin_arg = 1.0
        elif asin_arg < -1.0:
            asin_arg = -1.0

        y_angle_0 = degrees(asin(asin_arg))
        while y_angle_0 < min_angle:
            y_angle_0 += 360.0
        while y_angle_0 > max_angle:
            y_angle_0 -= 360.0

        y_angle_1 = 180 - y_angle_0
        while y_angle_1 < min_angle:
            y_angle_1 += 360.0
        while y_angle_1 > max_angle:
            y_angle_1 -= 360.0

        t_y_0 = (y_angle_0 - self.theta) / self.delta
        t_y_1 = (y_angle_1 - self.theta) / self.delta

        t = None
        if np.isclose(t_x_0, t_y_0):
            t = (t_x_0 + t_y_0) / 2.0
        elif np.isclose(t_x_0, t_y_1):
            t = (t_x_0 + t_y_1) / 2.0
        elif np.isclose(t_x_1, t_y_0):
            t = (t_x_1 + t_y_0) / 2.0
        elif np.isclose(t_x_1, t_y_1):
            t = (t_x_1 + t_y_1) / 2.0
        else:
            # Comparing None and float yields a result in python2,
            # but throws TypeError in python3.  This fix (suggested by
            # @CatherineH) explicitly handles and avoids the case where
            # the None-vs-float comparison would have happened below.
            return None

        if (t >= 0.0) and (t <= 1.0):
            return t

        return None

    def centeriso(self, z):
        """Isometry to a centered aligned ellipse.

        This is an isometry that shifts and rotates `self`'s underlying
        ellipse so that it's centered on the origin and has its axes
        aligned with the xy-axes.

        Args:
            z (:obj:`complex` or :obj:`numpy.ndarray[complex]`): a point
                to send through the above-described isometry.

        Returns:
            (:obj:`complex` or :obj:`numpy.ndarray[complex]`) The point(s) f(z),
                where f is the above described isometry of the xy-plane (i.e.
                the one-dimensional complex plane).
        """
        return (1/self.rot_matrix)*(z - self.center)

    def icenteriso(self, zeta):
        """The inverse of the `centeriso()` method."""
        return self.rot_matrix*zeta + self.center

    def u1transform(self, z):
        """Similar to the `centeriso()` method, but maps to the unit circle."""
        zeta = self.centeriso(z)
        x, y = real(zeta), imag(zeta)
        return x/self.radius.real + 1j*y/self.radius.imag

    def iu1transform(self, zeta):
        """The inverse of the `u1transform()` method."""
        x = real(zeta)
        y = imag(zeta)
        z = x*self.radius.real + y*self.radius.imag
        return self.rot_matrix*z + self.center

    def length(self, t0=0, t1=1, error=LENGTH_ERROR, min_depth=LENGTH_MIN_DEPTH):
        """Computes the length of the Arc segment, `self`, from t0 to t1.

        Notes:
        * The length of an elliptical large_arc segment requires numerical
        integration, and in that case it's simpler to just do a geometric
        approximation, as for cubic bezier curves.
        """
        assert 0 <= t0 <= 1 and 0 <= t1 <= 1

        if t0 == 0 and t1 == 1:
            h = hash(self)
            if self.segment_length_hash is None or self.segment_length_hash != h:
                self.segment_length_hash = h
                if _quad_available:
                    self.segment_length = quad(lambda tau: abs(self.derivative(tau)),
                                               t0, t1, epsabs=error, limit=1000)[0]
                else:
                    self.segment_length = segment_length(self, t0, t1, self.point(t0),
                                                         self.point(t1), error, min_depth, 0)
            return self.segment_length

        if _quad_available:
            return quad(lambda tau: abs(self.derivative(tau)), t0, t1,
                        epsabs=error, limit=1000)[0]
        else:
            return segment_length(self, t0, t1, self.point(t0), self.point(t1),
                                  error, min_depth, 0)

    def ilength(self, s, s_tol=ILENGTH_S_TOL, maxits=ILENGTH_MAXITS,
                error=ILENGTH_ERROR, min_depth=ILENGTH_MIN_DEPTH):
        """Approximates the unique `t` such that self.length(0, t) = s.

        Args:
            s (float): A length between 0 and `self.length()`.

        Returns:
             (float) The t, such that self.length(0, t) is approximately s.

        For more info:
            See the inv_arclength() docstring.
        """
        return inv_arclength(self, s, s_tol=s_tol, maxits=maxits, error=error,
                             min_depth=min_depth)

    def joins_smoothly_with(self, previous, wrt_parameterization=False,
                            error=0):
        """Checks if this segment joins smoothly with previous segment.  By
        default, this only checks that this segment starts moving (at t=0) in
        the same direction (and from the same positive) as previous stopped
        moving (at t=1).  To check if the tangent magnitudes also match, set
        wrt_parameterization=True."""
        if wrt_parameterization:
            return self.start == previous.end and abs(
                self.derivative(0) - previous.derivative(1)) <= error
        else:
            return self.start == previous.end and abs(
                self.unit_tangent(0) - previous.unit_tangent(1)) <= error

    def derivative(self, t, n=1):
        """returns the nth derivative of the segment at t."""
        angle = radians(self.theta + t*self.delta)
        phi = radians(self.rotation)
        rx = self.radius.real
        ry = self.radius.imag
        k = (self.delta*pi/180)**n  # ((d/dt)angle)**n

        if n % 4 == 0 and n > 0:
            return rx*cos(phi)*cos(angle) - ry*sin(phi)*sin(angle) + 1j*(
                rx*sin(phi)*cos(angle) + ry*cos(phi)*sin(angle))
        elif n % 4 == 1:
            return k*(-rx*cos(phi)*sin(angle) - ry*sin(phi)*cos(angle) + 1j*(
                -rx*sin(phi)*sin(angle) + ry*cos(phi)*cos(angle)))
        elif n % 4 == 2:
            return k*(-rx*cos(phi)*cos(angle) + ry*sin(phi)*sin(angle) + 1j*(
                -rx*sin(phi)*cos(angle) - ry*cos(phi)*sin(angle)))
        elif n % 4 == 3:
            return k*(rx*cos(phi)*sin(angle) + ry*sin(phi)*cos(angle) + 1j*(
                rx*sin(phi)*sin(angle) - ry*cos(phi)*cos(angle)))
        else:
            raise ValueError("n should be a positive integer.")

    def unit_tangent(self, t):
        """returns the unit tangent vector of the segment at t (centered at
        the origin and expressed as a complex number)."""
        dseg = self.derivative(t)
        return dseg/abs(dseg)

    def normal(self, t):
        """returns the (right hand rule) unit normal vector to self at t."""
        return -1j*self.unit_tangent(t)

    def curvature(self, t):
        """returns the curvature of the segment at t."""
        return segment_curvature(self, t)

    # def icurvature(self, kappa):
    #     """returns a list of t-values such that 0 <= t<= 1 and
    #     seg.curvature(t) = kappa."""
    #
    #     a, b = self.radius.real, self.radius.imag
    #     if kappa > min(a, b)/max(a, b)**2 or kappa <= 0:
    #         return []
    #     if a==b:
    #         if kappa != 1/a:
    #             return []
    #         else:
    #             raise ValueError(
    #                 "The .icurvature() method for Arc elements with "
    #                 "radius.real == radius.imag (i.e. circle segments) "
    #                 "will raise this exception when kappa is 1/radius.real as "
    #                 "this is true at every point on the circle segment.")
    #
    #     # kappa = a*b / (a^2sin^2(tau) + b^2cos^2(tau))^(3/2), tau=2*pi*phase
    #     sin2 = np.poly1d([1, 0])
    #     p = kappa**2*(a*sin2 + b*(1 - sin2))**3 - a*b
    #     sin2s = polyroots01(p)
    #     taus = []
    #
    #     for sin2 in sin2s:
    #         taus += [np.arcsin(sqrt(sin2)), np.arcsin(-sqrt(sin2))]
    #
    #     # account for the other branch of arcsin
    #     sgn = lambda x: x/abs(x) if x else 0
    #     other_taus = [sgn(tau)*np.pi - tau for tau in taus if abs(tau) != np.pi/2]
    #     taus = taus + other_taus
    #
    #     # get rid of points not included in segment
    #     ts = [phase2t(tau) for tau in taus]
    #
    #     return [t for t in ts if 0<=t<=1]


    def reversed(self):
        """returns a copy of the Arc object with its orientation reversed."""
        return Arc(self.end, self.radius, self.rotation, self.large_arc,
                   not self.sweep, self.start)

    def phase2t(self, psi):
        """Converts phase to t-value.

        I.e. given phase, psi, such that -np.pi < psi <= np.pi, approximates
        the unique t-value such that `self.u1transform(self.point(t))` equals
        `np.exp(1j*psi)`.

        Args:
            psi (float): The phase in radians.

        Returns:
            (float): the corresponding t-value.

        """
        def _deg(rads, domain_lower_limit):
            # Convert rads to degrees in [0, 360) domain
            degs = degrees(rads % (2*pi))

            # Convert to [domain_lower_limit, domain_lower_limit + 360) domain
            k = domain_lower_limit // 360
            degs += k * 360
            if degs < domain_lower_limit:
                degs += 360
            return degs

        if self.delta > 0:
            degs = _deg(psi, domain_lower_limit=self.theta)
        else:
            degs = _deg(psi, domain_lower_limit=self.theta)
        return (degs - self.theta)/self.delta

    def intersect(self, other_seg, tol=1e-12):
        """NOT FULLY IMPLEMENTED.  Finds the intersections of two segments.
        returns a list of tuples (t1, t2) such that
        self.point(t1) == other_seg.point(t2).
        Note: This will fail if the two segments coincide for more than a
        finite collection of points.

        Note: Arc related intersections are only partially supported, i.e. are
        only half-heartedly implemented and not well tested.  Please feel free
        to let me know if you're interested in such a feature -- or even better
        please submit an implementation if you want to code one."""

        # This special case can be easily solved algebraically.
        if (self.rotation == 0) and isinstance(other_seg, Line):
            a = self.radius.real
            b = self.radius.imag

            # Ignore the ellipse's center point (to pretend that it's
            # centered at the origin), and translate the Line to match.
            l = Line(start=(other_seg.start-self.center), end=(other_seg.end-self.center))

            # This gives us the translated Line as a parametric equation.
            # s = p1 t + p0
            p = l.poly()

            if p[1].real == 0.0:
                # The `x` value doesn't depend on `t`, the line is vertical.
                c = p[0].real
                x_values = [c]

                # Substitute the line `x = c` into the equation for the
                # (origin-centered) ellipse.
                #
                # x^2/a^2 + y^2/b^2 = 1
                # c^2/a^2 + y^2/b^2 = 1
                # y^2/b^2 = 1 - c^2/a^2
                # y^2 = b^2(1 - c^2/a^2)
                # y = +-b sqrt(1 - c^2/a^2)

                discriminant = 1 - (c * c)/(a * a)
                if discriminant < 0:
                    return []
                elif discriminant == 0:
                    y_values = [0]
                else:
                    val = b * sqrt(discriminant)
                    y_values = [val, -val]

            else:
                # This is a non-vertical line.
                #
                # Convert the Line's parametric equation to the "y = mx + c" format.
                # x = p1.real t + p0.real
                # y = p1.imag t + p0.imag
                #
                # t = (x - p0.real) / p1.real
                # t = (y - p0.imag) / p1.imag
                #
                # (y - p0.imag) / p1.imag = (x - p0.real) / p1.real
                # (y - p0.imag) = ((x - p0.real) * p1.imag) / p1.real
                # y = ((x - p0.real) * p1.imag) / p1.real + p0.imag
                # y = (x p1.imag - p0.real * p1.imag) / p1.real + p0.imag
                # y = x p1.imag/p1.real - p0.real p1.imag / p1.real + p0.imag
                # m = p1.imag/p1.real
                # c = -m p0.real + p0.imag
                m = p[1].imag / p[1].real
                c = (-m * p[0].real) + p[0].imag

                # Substitute the line's y(x) equation into the equation for
                # the ellipse.  We can pretend the ellipse is centered at the
                # origin, since we shifted the Line by the ellipse's center.
                #
                # x^2/a^2 + y^2/b^2 = 1
                # x^2/a^2 + (mx+c)^2/b^2 = 1
                # (b^2 x^2 + a^2 (mx+c)^2)/(a^2 b^2) = 1
                # b^2 x^2 + a^2 (mx+c)^2 = a^2 b^2
                # b^2 x^2 + a^2(m^2 x^2 + 2mcx + c^2) = a^2 b^2
                # b^2 x^2 + a^2 m^2 x^2 + 2a^2 mcx + a^2 c^2 - a^2 b^2 = 0
                # (a^2 m^2 + b^2)x^2 + 2a^2 mcx + a^2(c^2 - b^2) = 0
                #
                # The quadratic forumla tells us:  x = (-B +- sqrt(B^2 - 4AC)) / 2A
                # Where:
                #     A = a^2 m^2 + b^2
                #     B = 2 a^2 mc
                #     C = a^2(c^2 - b^2)
                #
                # The determinant is: B^2 - 4AC
                #
                # The solution simplifies to:
                # x = (-a^2 mc +- a b sqrt(a^2 m^2 + b^2 - c^2)) / (a^2 m^2 + b^2)
                #
                # Solving the line for x(y) and substituting *that* into
                # the equation for the ellipse gives this solution for y:
                # y = (b^2 c +- abm sqrt(a^2 m^2 + b^2 - c^2)) / (a^2 m^2 + b^2)

                denominator = (a * a * m * m) + (b * b)

                discriminant = denominator - (c * c)
                if discriminant < 0:
                    return []

                x_sqrt = a * b * sqrt(discriminant)
                x1 = (-(a * a * m * c) + x_sqrt) / denominator 
                x2 = (-(a * a * m * c) - x_sqrt) / denominator 
                x_values = [x1]
                if x1 != x2:
                    x_values.append(x2)

                y_sqrt = x_sqrt * m
                y1 = ((b * b * c) + y_sqrt) / denominator
                y2 = ((b * b * c) - y_sqrt) / denominator
                y_values = [y1]
                if y1 != y2:
                    y_values.append(y2)

            intersections = []
            for x in x_values:
                for y in y_values:
                    p = complex(x, y) + self.center
                    my_t = self.point_to_t(p)
                    if my_t == None:
                        continue
                    other_t = other_seg.point_to_t(p)
                    if other_t == None:
                        continue
                    intersections.append([my_t, other_t])
            return intersections

        elif is_bezier_segment(other_seg):
            # if self and other_seg intersect, they will itersect at the
            # same points after being passed through the `u1transform`
            # isometry. Since this isometry maps self to the unit circle,
            # the intersections will be easy to find (just look for any
            # points where other_seg is a distance of one from the origin.
            # Moreoever, the t-values that the intersection happen at will
            # be unchanged by the isometry.
            u1poly = np.poly1d(self.u1transform(other_seg.poly()))
            u1poly_mag2 = real(u1poly)**2 + imag(u1poly)**2
            t2s = [t for t in polyroots01(u1poly_mag2 - 1) if 0 <= t <= 1]
            t1s = [self.phase2t(phase(u1poly(t2))) for t2 in t2s]

            return [(t1, t2) for t1, t2 in zip(t1s, t2s) if 0 <= t1 <= 1]

        elif isinstance(other_seg, Arc):
            assert other_seg != self

            import sys

            # From "Intersection of two circles", at
            # http://paulbourke.net/geometry/circlesphere/

            # It's easy to find the intersections of two circles, so
            # compute that and see if any of those
            # intersection points are on the arcs.
            if (self.rotation == 0) and (self.radius.real == self.radius.imag) and (other_seg.rotation == 0) and (other_seg.radius.real == other_seg.radius.imag):
                r0 = self.radius.real
                r1 = other_seg.radius.real
                p0 = self.center
                p1 = other_seg.center
                d = abs(p0 - p1)
                possible_inters = []

                if d > (r0 + r1):
                    # The circles are farther apart than the sum of
                    # their radii: no intersections possible.
                    pass

                elif d < abs(r0 - r1):
                    # The small circle is wholly contained within the
                    # large circle: no intersections possible.
                    pass

                elif (np.isclose(d, 0, rtol=0.0, atol=1e-6)) and (np.isclose(r0, r1, rtol=0.0, atol=1e-6)):
                    # The Arcs lie on the same circle: they have the
                    # same center and are of equal radius.

                    def point_in_seg_interior(point, seg):
                        t = seg.point_to_t(point)
                        if (not t or
                                np.isclose(t, 0.0, rtol=0.0, atol=1e-6) or
                                np.isclose(t, 1.0, rtol=0.0, atol=1e-6)):
                            return False
                        return True

                    # If either end of either segment is in the interior
                    # of the other segment, then the Arcs overlap
                    # in an infinite number of points, and we return
                    # "no intersections".
                    if (
                            point_in_seg_interior(self.start, other_seg) or
                            point_in_seg_interior(self.end, other_seg) or
                            point_in_seg_interior(other_seg.start, self) or
                            point_in_seg_interior(other_seg.end, self)
                    ):
                        return []

                    # If they touch at their endpoint(s) and don't go
                    # in "overlapping directions", then we accept that
                    # as intersections.

                    if (self.start == other_seg.start) and (self.sweep != other_seg.sweep):
                        possible_inters.append((0.0, 0.0))

                    if (self.start == other_seg.end) and (self.sweep == other_seg.sweep):
                        possible_inters.append((0.0, 1.0))

                    if (self.end == other_seg.start) and (self.sweep == other_seg.sweep):
                        possible_inters.append((1.0, 0.0))

                    if (self.end == other_seg.end) and (self.sweep != other_seg.sweep):
                        possible_inters.append((1.0, 1.0))

                elif np.isclose(d, r0 + r1, rtol=0.0, atol=1e-6):
                    # The circles are tangent, so the Arcs may touch
                    # at exactly one point.  The circles lie outside
                    # each other.
                    l = Line(start=p0, end=p1)
                    p = l.point(r0/d)
                    possible_inters.append((self.point_to_t(p), other_seg.point_to_t(p)))

                elif np.isclose(d, abs(r0 - r1), rtol=0.0, atol=1e-6):
                    # The circles are tangent, so the Arcs may touch
                    # at exactly one point.  One circle lies inside
                    # the other.
                    # Make a line from the center of the inside circle
                    # to the center of the outside circle, and walk
                    # along it the negative of the small radius.
                    l = Line(start=p0, end=p1)
                    little_r = r0
                    if r0 > r1:
                        l = Line(start=p1, end=p0)
                        little_r = r1
                    p = l.point(-little_r/d)
                    possible_inters.append((self.point_to_t(p), other_seg.point_to_t(p)))

                else:
                    a = (pow(r0, 2.0) - pow(r1, 2.0) + pow(d, 2.0)) / (2.0 * d)
                    h = sqrt(pow(r0, 2.0) - pow(a, 2.0))
                    p2 = p0 + (a * (p1 - p0) / d)

                    x30 = p2.real + (h * (p1.imag - p0.imag) / d)
                    x31 = p2.real - (h * (p1.imag - p0.imag) / d)

                    y30 = p2.imag - (h * (p1.real - p0.real) / d)
                    y31 = p2.imag + (h * (p1.real - p0.real) / d)

                    p30 = complex(x30, y30)
                    p31 = complex(x31, y31)

                    possible_inters.append((self.point_to_t(p30), other_seg.point_to_t(p30)))
                    possible_inters.append((self.point_to_t(p31), other_seg.point_to_t(p31)))

                inters = []
                for p in possible_inters:
                    self_t = p[0]
                    if (self_t is None) or (self_t < 0.0) or (self_t > 1.0): continue
                    other_t = p[1]
                    if (other_t is None) or (other_t < 0.0) or (other_t > 1.0): continue
                    assert(np.isclose(self.point(self_t), other_seg.point(other_t), rtol=0.0, atol=1e-6))
                    i = (self_t, other_t)
                    inters.append(i)

                return inters

            # This could be made explicit to increase efficiency
            longer_length = max(self.length(), other_seg.length())
            inters = bezier_intersections(self, other_seg,
                                          longer_length=longer_length,
                                          tol=tol, tol_deC=tol)

            # ad hoc fix for redundant solutions
            if len(inters) > 2:
                def keyfcn(tpair):
                    t1, t2 = tpair
                    return abs(self.point(t1) - other_seg.point(t2))
                inters.sort(key=keyfcn)
                for idx in range(1, len(inters)-1):
                    if (abs(inters[idx][0] - inters[idx + 1][0])
                            <  abs(inters[idx][0] - inters[0][0])):
                        return [inters[0], inters[idx]]
                else:
                    return [inters[0], inters[-1]]
            return inters

        else:
            raise TypeError("other_seg should be a Arc, Line, "
                            "QuadraticBezier, or CubicBezier object.")

    def bbox(self):
        """returns a bounding box for the segment in the form
        (xmin, xmax, ymin, ymax)."""
        # a(t) = radians(self.theta + self.delta*t)
        #      = (2*pi/360)*(self.theta + self.delta*t)
        # x'=0: ~~~~~~~~~
        # -rx*cos(phi)*sin(a(t)) = ry*sin(phi)*cos(a(t))
        # -(rx/ry)*cot(phi)*tan(a(t)) = 1
        # a(t) = arctan(-(ry/rx)tan(phi)) + pi*k === atan_x
        # y'=0: ~~~~~~~~~~
        # rx*sin(phi)*sin(a(t)) = ry*cos(phi)*cos(a(t))
        # (rx/ry)*tan(phi)*tan(a(t)) = 1
        # a(t) = arctan((ry/rx)*cot(phi))
        # atanres = arctan((ry/rx)*cot(phi)) === atan_y
        # ~~~~~~~~
        # (2*pi/360)*(self.theta + self.delta*t) = atanres + pi*k
        # Therfore, for both x' and y', we have...
        # t = ((atan_{x/y} + pi*k)*(360/(2*pi)) - self.theta)/self.delta
        # for all k s.t. 0 < t < 1
        from math import atan, tan

        if cos(self.phi) == 0:
            atan_x = pi/2
            atan_y = 0
        elif sin(self.phi) == 0:
            atan_x = 0
            atan_y = pi/2
        else:
            rx, ry = self.radius.real, self.radius.imag
            atan_x = atan(-(ry/rx)*tan(self.phi))
            atan_y = atan((ry/rx)/tan(self.phi))

        def angle_inv(ang, k):  # inverse of angle from Arc.derivative()
            return ((ang + pi*k)*(360/(2*pi)) - self.theta)/self.delta

        xtrema = [self.start.real, self.end.real]
        ytrema = [self.start.imag, self.end.imag]

        for k in range(-4, 5):
            tx = angle_inv(atan_x, k)
            ty = angle_inv(atan_y, k)
            if 0 <= tx <= 1:
                xtrema.append(self.point(tx).real)
            if 0 <= ty <= 1:
                ytrema.append(self.point(ty).imag)
        xmin = max(xtrema)
        return min(xtrema), max(xtrema), min(ytrema), max(ytrema)

    def split(self, t):
        """returns two segments, whose union is this segment and which join
        at self.point(t)."""
        return self.cropped(0, t), self.cropped(t, 1)

    def cropped(self, t0, t1):
        """returns a cropped copy of this segment which starts at
        self.point(t0) and ends at self.point(t1)."""
        if abs(self.delta*(t1 - t0)) <= 180:
            new_large_arc = 0
        else:
            new_large_arc = 1
        return Arc(self.point(t0), radius=self.radius, rotation=self.rotation,
                   large_arc=new_large_arc, sweep=self.sweep,
                   end=self.point(t1), autoscale_radius=self.autoscale_radius)

    def radialrange(self, origin, return_all_global_extrema=False):
        """returns the tuples (d_min, t_min) and (d_max, t_max) which minimize
        and maximize, respectively, the distance,
        d = |self.point(t)-origin|."""

        # u1orig = self.u1transform(origin)
        # if abs(u1orig) == 1:  # origin lies on ellipse
        #     t = self.phase2t(phase(u1orig))
        #     d_min = 0
        #
        # # Transform to a coordinate system where the ellipse is centered
        # # at the origin and its axes are horizontal/vertical
        # zeta0 = self.centeriso(origin)
        # a, b = self.radius.real, self.radius.imag
        # x0, y0 = zeta0.real, zeta0.imag
        #
        # # Find t s.t. z'(t)
        # a2mb2 = (a**2 - b**2)
        # if u1orig.imag:  # x != x0
        #
        #     coeffs = [a2mb2**2,
        #               2*a2mb2*b**2*y0,
        #               (-a**4 + (2*a**2 - b**2 + y0**2)*b**2 + x0**2)*b**2,
        #               -2*a2mb2*b**4*y0,
        #               -b**6*y0**2]
        #     ys = polyroots(coeffs, realroots=True,
        #                    condition=lambda r: -b <= r <= b)
        #     xs = (a*sqrt(1 - y**2/b**2) for y in ys)
        #
        #     ts = [self.phase2t(phase(self.u1transform(self.icenteriso(
        #         complex(x, y))))) for x, y in zip(xs, ys)]
        #
        # else:  # This case is very similar, see notes and assume instead y0!=y
        #     b2ma2 = (b**2 - a**2)
        #     coeffs = [b2ma2**2,
        #               2*b2ma2*a**2*x0,
        #               (-b**4 + (2*b**2 - a**2 + x0**2)*a**2 + y0**2)*a**2,
        #               -2*b2ma2*a**4*x0,
        #               -a**6*x0**2]
        #     xs = polyroots(coeffs, realroots=True,
        #                    condition=lambda r: -a <= r <= a)
        #     ys = (b*sqrt(1 - x**2/a**2) for x in xs)
        #
        #     ts = [self.phase2t(phase(self.u1transform(self.icenteriso(
        #         complex(x, y))))) for x, y in zip(xs, ys)]

        raise _NotImplemented4ArcException

    def rotated(self, degs, origin=None):
        """Returns a copy of self rotated by `degs` degrees (CCW) around the
        point `origin` (a complex number).  By default `origin` is either
        `self.point(0.5)`, or in the case that self is an Arc object,
        `origin` defaults to `self.center`."""
        return rotate(self, degs, origin=origin)

    def translated(self, z0):
        """Returns a copy of self shifted by the complex quantity `z0` such
        that self.translated(z0).point(t) = self.point(t) + z0 for any t."""
        return translate(self, z0)

    def scaled(self, sx, sy=None, origin=0j):
        """Scale transform.  See `scale` function for further explanation."""
        return scale(self, sx=sx, sy=sy, origin=origin)

    def as_cubic_curves(self, curves=1):
        """Generates cubic curves to approximate this arc"""
        slice_t = radians(self.delta) / float(curves)

        current_t = radians(self.theta)
        rx = self.radius.real # * self.radius_scale
        ry = self.radius.imag # * self.radius_scale
        p_start = self.start

        theta = radians(self.rotation)
        x0 = self.center.real
        y0 = self.center.imag
        cos_theta = cos(theta)
        sin_theta = sin(theta)

        for i in range(curves):
            next_t = current_t + slice_t

            alpha = sin(slice_t) * (sqrt(4 + 3 * pow(tan((slice_t) / 2.0), 2)) - 1) / 3.0

            cos_start_t = cos(current_t)
            sin_start_t = sin(current_t)

            ePrimen1x = -rx * cos_theta * sin_start_t - ry * sin_theta * cos_start_t
            ePrimen1y = -rx * sin_theta * sin_start_t + ry * cos_theta * cos_start_t

            cos_end_t = cos(next_t)
            sin_end_t = sin(next_t)

            p2En2x = x0 + rx * cos_end_t * cos_theta - ry * sin_end_t * sin_theta
            p2En2y = y0 + rx * cos_end_t * sin_theta + ry * sin_end_t * cos_theta
            p_end = p2En2x + p2En2y * 1j
            if i == curves - 1:
                p_end = self.end

            ePrimen2x = -rx * cos_theta * sin_end_t - ry * sin_theta * cos_end_t
            ePrimen2y = -rx * sin_theta * sin_end_t + ry * cos_theta * cos_end_t

            p_c1 = (p_start.real + alpha * ePrimen1x) + (p_start.imag + alpha * ePrimen1y) * 1j
            p_c2 = (p_end.real - alpha * ePrimen2x) + (p_end.imag - alpha * ePrimen2y) * 1j

            yield CubicBezier(p_start, p_c1, p_c2, p_end)
            p_start = p_end
            current_t = next_t

    def as_quad_curves(self, curves=1):
        """Generates quadratic curves to approximate this arc"""
        slice_t = radians(self.delta) / float(curves)

        current_t = radians(self.theta)
        a = self.radius.real  # * self.radius_scale
        b = self.radius.imag  # * self.radius_scale
        p_start = self.start

        theta = radians(self.rotation)
        cx = self.center.real
        cy = self.center.imag

        cos_theta = cos(theta)
        sin_theta = sin(theta)

        for i in range(curves):
            next_t = current_t + slice_t
            mid_t = (next_t + current_t) / 2
            cos_end_t = cos(next_t)
            sin_end_t = sin(next_t)
            p2En2x = cx + a * cos_end_t * cos_theta - b * sin_end_t * sin_theta
            p2En2y = cy + a * cos_end_t * sin_theta + b * sin_end_t * cos_theta
            p_end = p2En2x + p2En2y * 1j
            if i == curves - 1:
                p_end = self.end
            cos_mid_t = cos(mid_t)
            sin_mid_t = sin(mid_t)
            alpha = (4.0 - cos(slice_t)) / 3.0
            px = cx + alpha * (a * cos_mid_t * cos_theta - b * sin_mid_t * sin_theta)
            py = cy + alpha * (a * cos_mid_t * sin_theta + b * sin_mid_t * cos_theta)
            yield QuadraticBezier(p_start, px + py * 1j, p_end)
            p_start = p_end
            current_t = next_t


class Path(MutableSequence):
    """A Path is a sequence of path segments"""

    # Put it here, so there is a default if unpickled.
    _closed = False
    _start = None
    _end = None
    element = None
    transform = None
    meta = None  # meant as container for storage of arbitrary meta data

    def __init__(self, *segments, **kw):
        self._length = None
        self._lengths = None
        if 'closed' in kw:
            self.closed = kw['closed']  # DEPRECATED
        if len(segments) >= 1:
            if isinstance(segments[0], str):
                if len(segments) >= 2:
                    current_pos = segments[1]
                elif 'current_pos' in kw:
                    current_pos = kw['current_pos']
                else:
                    current_pos = 0j
                self._segments = list()
                self._parse_path(segments[0], current_pos)
            else:
                self._segments = list(segments)
        else:
            self._segments = list()
        if self._segments:
            self._start = self._segments[0].start
            self._end = self._segments[-1].end
        else:
            self._start = None
            self._end = None

        if 'tree_element' in kw:
            self._tree_element = kw['tree_element']

    def __hash__(self) -> int:

        def _pointify(segment):
            return segment.apoints() if isinstance(segment, Arc) else segment.bpoints()

        pts = tuple(x for segment in self._segments for x in _pointify(segment))
        return hash(pts + (self._closed,))

    def __getitem__(self, index):
        return self._segments[index]

    def __setitem__(self, index, value):
        self._segments[index] = value
        self._length = None
        self._start = self._segments[0].start
        self._end = self._segments[-1].end

    def __delitem__(self, index):
        del self._segments[index]
        self._length = None
        if len(self._segments) > 0:
            self._start = self._segments[0].start
            self._end = self._segments[-1].end
        else:
            self._start = None
            self._end = None

    def __iter__(self):
        return self._segments.__iter__()

    def __contains__(self, x):
        return self._segments.__contains__(x)

    def insert(self, index, value):
        self._segments.insert(index, value)
        self._length = None
        self._start = self._segments[0].start
        self._end = self._segments[-1].end

    def reversed(self):
        """returns a copy of the Path object with its orientation reversed."""
        newpath = [seg.reversed() for seg in self]
        newpath.reverse()
        return Path(*newpath)

    def __len__(self):
        return len(self._segments)

    def __repr__(self):
        return "Path({})".format(
            ",\n     ".join(repr(x) for x in self._segments))

    def __eq__(self, other):
        if not isinstance(other, Path):
            return False
        if len(self) != len(other):
            return False
        for s, o in zip(self._segments, other._segments):
            if not s == o:
                return False
        return True

    def __ne__(self, other):
        if not isinstance(other, Path):
            return NotImplemented
        return not self == other

    def _calc_lengths(self, error=LENGTH_ERROR, min_depth=LENGTH_MIN_DEPTH):
        if self._length is not None:
            return

        lengths = [each.length(error=error, min_depth=min_depth) for each in
                   self._segments]
        self._length = sum(lengths)
        if self._length == 0:
            self._lengths = lengths  # all lengths are 0.
        else:
            self._lengths = [each / self._length for each in lengths]

    def point(self, pos):

        # Shortcuts
        if len(self._segments) == 0:
            raise ValueError("This path contains no segments!")
        if pos == 0.0:
            return self._segments[0].point(pos)
        if pos == 1.0:
            return self._segments[-1].point(pos)

        self._calc_lengths()
        # Find which segment the point we search for is located on:
        segment_start = 0
        for index, segment in enumerate(self._segments):
            segment_end = segment_start + self._lengths[index]
            if segment_end >= pos:
                # This is the segment! How far in on the segment is the point?
                segment_pos = (pos - segment_start)/(
                    segment_end - segment_start)
                return segment.point(segment_pos)
            segment_start = segment_end
        raise RuntimeError("Something has gone wrong.  Could not compute Path.point({}) for path {}".format(pos, self))

    def length(self, T0=0, T1=1, error=LENGTH_ERROR, min_depth=LENGTH_MIN_DEPTH):
        self._calc_lengths(error=error, min_depth=min_depth)
        if T0 == 0 and T1 == 1:
            return self._length
        else:
            if len(self) == 1:
                return self[0].length(t0=T0, t1=T1)
            idx0, t0 = self.T2t(T0)
            idx1, t1 = self.T2t(T1)
            if idx0 == idx1:
                return self[idx0].length(t0=t0, t1=t1)
            return (self[idx0].length(t0=t0) +
                    sum(self[idx].length() for idx in range(idx0 + 1, idx1)) +
                    self[idx1].length(t1=t1))

    def ilength(self, s, s_tol=ILENGTH_S_TOL, maxits=ILENGTH_MAXITS,
                error=ILENGTH_ERROR, min_depth=ILENGTH_MIN_DEPTH):
        """Returns a float, t, such that self.length(0, t) is approximately s.
        See the inv_arclength() docstring for more details."""
        return inv_arclength(self, s, s_tol=s_tol, maxits=maxits, error=error,
                             min_depth=min_depth)

    def iscontinuous(self):
        """Checks if a path is continuous with respect to its
        parameterization."""
        return all(self[i].end == self[i+1].start for i in range(len(self) - 1))

    def continuous_subpaths(self):
        """Breaks self into its continuous components, returning a list of
        continuous subpaths.
        I.e.
        (all(subpath.iscontinuous() for subpath in self.continuous_subpaths())
         and self == concatpaths(self.continuous_subpaths()))
        )
        """
        subpaths = []
        subpath_start = 0
        for i in range(len(self) - 1):
            if self[i].end != self[(i+1) % len(self)].start:
                subpaths.append(Path(*self[subpath_start: i+1]))
                subpath_start = i+1
        subpaths.append(Path(*self[subpath_start: len(self)]))
        return subpaths

    def isclosed(self):
        """This function determines if a connected path is closed."""
        assert len(self) != 0
        assert self.iscontinuous()
        return self.start == self.end

    def isclosedac(self):
        assert len(self) != 0
        return self.start == self.end

    def _is_closable(self):
        try:
            end = self[-1].end
        except IndexError:
            return True
        for segment in self:
            if segment.start == end:
                return True
        return False

    @property
    def closed(self, warning_on=CLOSED_WARNING_ON):
        """The closed attribute is deprecated, please use the isclosed()
        method instead.  See _closed_warning for more information."""
        mes = ("This attribute is deprecated, consider using isclosed() "
               "method instead.\n\nThis attribute is kept for compatibility "
               "with scripts created using svg.path (v2.0). You can prevent "
               "this warning in the future by setting "
               "CLOSED_WARNING_ON=False.")
        if warning_on:
            warn(mes)
        return self._closed and self._is_closable()

    @closed.setter
    def closed(self, value):
        value = bool(value)
        if value and not self._is_closable():
            raise ValueError("End does not coincide with a segment start.")
        self._closed = value

    @property
    def start(self):
        if not self._start and len(self._segments)>0:
            self._start = self._segments[0].start
        return self._start

    @start.setter
    def start(self, pt):
        self._start = pt
        if len(self._segments)>0:
            self._segments[0].start = pt

    @property
    def end(self):
        if not self._end and len(self._segments)>0:
            self._end = self._segments[-1].end
        return self._end

    @end.setter
    def end(self, pt):
        self._end = pt
        if len(self._segments)>0:
            self._segments[-1].end = pt

    def d(self, useSandT=False, use_closed_attrib=False, rel=False):
        """Returns a path d-string for the path object.
        For an explanation of useSandT and use_closed_attrib, see the
        compatibility notes in the README."""
        if len(self) == 0:
            return ''
        if use_closed_attrib:
            self_closed = self.iscontinuous() and self.isclosed()
            if self_closed:
                segments = self[:-1]
            else:
                segments = self[:]
        else:
            self_closed = False
            segments = self[:]
    
        current_pos = None
        parts = []
        previous_segment = None
        end = self[-1].end
    
        for segment in segments:
            seg_start = segment.start
            # If the start of this segment does not coincide with the end of
            # the last segment or if this segment is actually the close point
            # of a closed path, then we should start a new subpath here.
            if current_pos != seg_start or \
                    (self_closed and seg_start == end and use_closed_attrib):
                if rel:
                    _seg_start = seg_start - current_pos if current_pos is not None else seg_start
                else:
                    _seg_start = seg_start
                parts.append('M {},{}'.format(_seg_start.real, _seg_start.imag))
    
            if isinstance(segment, Line):
                if rel:
                    _seg_end = segment.end - seg_start
                else:
                    _seg_end = segment.end
                parts.append('L {},{}'.format(_seg_end.real, _seg_end.imag))
            elif isinstance(segment, CubicBezier):
                if useSandT and segment.is_smooth_from(previous_segment,
                                                       warning_on=False):
                    if rel:
                        _seg_control2 = segment.control2 - seg_start
                        _seg_end = segment.end - seg_start
                    else:
                        _seg_control2 = segment.control2
                        _seg_end = segment.end
                    args = (_seg_control2.real, _seg_control2.imag,
                            _seg_end.real, _seg_end.imag)
                    parts.append('S {},{} {},{}'.format(*args))
                else:
                    if rel:
                        _seg_control1 = segment.control1 - seg_start
                        _seg_control2 = segment.control2 - seg_start
                        _seg_end = segment.end - seg_start
                    else:
                        _seg_control1 = segment.control1
                        _seg_control2 = segment.control2
                        _seg_end = segment.end
                    args = (_seg_control1.real, _seg_control1.imag,
                            _seg_control2.real, _seg_control2.imag,
                            _seg_end.real, _seg_end.imag)
                    parts.append('C {},{} {},{} {},{}'.format(*args))
            elif isinstance(segment, QuadraticBezier):
                if useSandT and segment.is_smooth_from(previous_segment,
                                                       warning_on=False):
                    if rel:
                        _seg_end = segment.end - seg_start
                    else:
                        _seg_end = segment.end
                    args = _seg_end.real, _seg_end.imag
                    parts.append('T {},{}'.format(*args))
                else:
                    if rel:
                        _seg_control = segment.control - seg_start
                        _seg_end = segment.end - seg_start
                    else:
                        _seg_control = segment.control
                        _seg_end = segment.end
                    args = (_seg_control.real, _seg_control.imag,
                            _seg_end.real, _seg_end.imag)
                    parts.append('Q {},{} {},{}'.format(*args))
    
            elif isinstance(segment, Arc):
                if rel:
                    _seg_end = segment.end - seg_start
                else:
                    _seg_end = segment.end
                args = (segment.radius.real, segment.radius.imag,
                        segment.rotation,int(segment.large_arc),
                        int(segment.sweep),_seg_end.real, _seg_end.imag)
                parts.append('A {},{} {} {:d},{:d} {},{}'.format(*args))
            current_pos = segment.end
            previous_segment = segment
    
        if self_closed:
            parts.append('Z')
    
        s = ' '.join(parts)
        return s if not rel else s.lower()

    def joins_smoothly_with(self, previous, wrt_parameterization=False):
        """Checks if this Path object joins smoothly with previous
        path/segment.  By default, this only checks that this Path starts
        moving (at t=0) in the same direction (and from the same positive) as
        previous stopped moving (at t=1).  To check if the tangent magnitudes
        also match, set wrt_parameterization=True."""
        if wrt_parameterization:
            return self[0].start == previous.end and self.derivative(
                0) == previous.derivative(1)
        else:
            return self[0].start == previous.end and self.unit_tangent(
                0) == previous.unit_tangent(1)

    def T2t(self, T):
        """returns the segment index, `seg_idx`, and segment parameter, `t`,
        corresponding to the path parameter `T`.  In other words, this is the
        inverse of the `Path.t2T()` method."""
        if T == 1:
            return len(self)-1, 1
        if T == 0:
            return 0, 0
        self._calc_lengths()
        # Find which segment self.point(T) falls on:
        T0 = 0  # the T-value the current segment starts on
        for seg_idx, seg_length in enumerate(self._lengths):
            T1 = T0 + seg_length  # the T-value the current segment ends on
            if T1 >= T:
                # This is the segment!
                t = (T - T0)/seg_length
                return seg_idx, t
            T0 = T1

        assert 0 <= T <= 1
        raise BugException

    def t2T(self, seg, t):
        """returns the path parameter T which corresponds to the segment
        parameter t.  In other words, for any Path object, path, and any
        segment in path, seg,  T(t) = path.t2T(seg, t) is the unique
        reparameterization such that path.point(T(t)) == seg.point(t) for all
        0 <= t <= 1.
        Input Note: seg can be a segment in the Path object or its
        corresponding index."""
        self._calc_lengths()
        # Accept an index or a segment for seg
        if isinstance(seg, int):
            seg_idx = seg
        else:
            try:
                seg_idx = self.index(seg)
            except ValueError:
                assert is_path_segment(seg) or isinstance(seg, int)
                raise

        segment_start = sum(self._lengths[:seg_idx])
        segment_end = segment_start + self._lengths[seg_idx]
        T = (segment_end - segment_start)*t + segment_start
        return T

    def derivative(self, T, n=1):
        """returns the tangent vector of the Path at T (centered at the origin
        and expressed as a complex number).
        Note: Bezier curves can have points where their derivative vanishes.
        If you are interested in the tangent direction, use unit_tangent()
        method instead."""
        seg_idx, t = self.T2t(T)
        seg = self._segments[seg_idx]
        return seg.derivative(t, n=n)/seg.length()**n

    def unit_tangent(self, T):
        """returns the unit tangent vector of the Path at T (centered at the
        origin and expressed as a complex number).  If the tangent vector's
        magnitude is zero, this method will find the limit of
        self.derivative(tau)/abs(self.derivative(tau)) as tau approaches T."""
        seg_idx, t = self.T2t(T)
        return self._segments[seg_idx].unit_tangent(t)

    def normal(self, t):
        """returns the (right hand rule) unit normal vector to self at t."""
        return -1j*self.unit_tangent(t)

    def curvature(self, T):
        """returns the curvature of this Path object at T and outputs
        float('inf') if not differentiable at T."""
        seg_idx, t = self.T2t(T)
        seg = self[seg_idx]
        if np.isclose(t, 0) and (seg_idx != 0 or self.end==self.start):
            previous_seg_in_path = self._segments[
                (seg_idx - 1) % len(self._segments)]
            if not seg.joins_smoothly_with(previous_seg_in_path):
                return float('inf')
        elif np.isclose(t, 1) and (seg_idx != len(self) - 1 or
                                   self.end == self.start):
            next_seg_in_path = self._segments[
                (seg_idx + 1) % len(self._segments)]
            if not next_seg_in_path.joins_smoothly_with(seg):
                return float('inf')
        dz = self.derivative(T)
        ddz = self.derivative(T, n=2)
        dx, dy = dz.real, dz.imag
        ddx, ddy = ddz.real, ddz.imag
        return abs(dx*ddy - dy*ddx)/(dx*dx + dy*dy)**1.5

    # def icurvature(self, kappa):
    #     """returns a list of T-values such that 0 <= T <= 1 and
    #     seg.curvature(t) = kappa.
    #     Note: not implemented for paths containing Arc segments."""
    #     assert is_bezier_path(self)
    #     Ts = []
    #     for i, seg in enumerate(self):
    #         Ts += [self.t2T(i, t) for t in seg.icurvature(kappa)]
    #     return Ts

    def area(self, chord_length=1e-4):
        """Find area enclosed by path.
        
        Approximates any Arc segments in the Path with lines
        approximately `chord_length` long, and returns the area enclosed
        by the approximated Path.  Default chord length is 0.01.  If Arc
        segments are included in path, to ensure accurate results, make
        sure this `chord_length` is set to a reasonable value (e.g. by
        checking curvature).
                
        Notes
        -----
        * Negative area results from clockwise (as opposed to
        counter-clockwise) parameterization of the input Path.
        
        To Contributors
        ---------------
        This is one of many parts of `svgpathtools` that could be 
        improved by a noble soul implementing a piecewise-linear 
        approximation scheme for paths (one with controls to guarantee a
        desired accuracy).
        """

        def area_without_arcs(path):
            area_enclosed = 0
            for seg in path:
                x = real(seg.poly())
                dy = imag(seg.poly()).deriv()
                integrand = x*dy
                integral = integrand.integ()
                area_enclosed += integral(1) - integral(0)
            return area_enclosed

        def seg2lines(seg_):
            """Find piecewise-linear approximation of `seg`."""
            num_lines = int(ceil(seg_.length() / chord_length))
            pts = [seg_.point(t) for t in np.linspace(0, 1, num_lines+1)]
            return [Line(pts[i], pts[i+1]) for i in range(num_lines)]

        assert self.isclosed()

        bezier_path_approximation = []
        for seg in self:
            if isinstance(seg, Arc):
                bezier_path_approximation += seg2lines(seg)
            else:
                bezier_path_approximation.append(seg)
        return area_without_arcs(Path(*bezier_path_approximation))

    def intersect(self, other_curve, justonemode=False, tol=1e-12):
        """Finds intersections of `self` with `other_curve`

        Args:
            other_curve: the path or path segment to check for intersections
                with `self`
            justonemode (bool): if true, returns only the first
                intersection found.
            tol (float): A tolerance used to check for redundant intersections
                (see comment above the code block where tol is used).

        Returns:
            (list[tuple[float, Curve, float]]): list of intersections, each
                in the format ((T1, seg1, t1), (T2, seg2, t2)), where
                self.point(T1) == seg1.point(t1) == seg2.point(t2) == other_curve.point(T2)

        Scope:
            If the two path objects coincide for more than a finite set of
            points, this code will iterate to max depth and/or raise an error.
        """
        path1 = self
        path2 = other_curve if isinstance(other_curve, Path) else Path(other_curve)
        assert path1 != path2

        intersection_list = []
        for seg1 in path1:
            for seg2 in path2:
                if justonemode and intersection_list:
                    return intersection_list[0]
                for t1, t2 in seg1.intersect(seg2, tol=tol):
                    T1 = path1.t2T(seg1, t1)
                    T2 = path2.t2T(seg2, t2)
                    intersection_list.append(((T1, seg1, t1), (T2, seg2, t2)))

        if justonemode and intersection_list:
            return intersection_list[0]

        # Note: If the intersection takes place at a joint (point one seg ends
        # and next begins in path) then intersection_list may contain a
        # redundant intersection.  This code block checks for and removes said
        # redundancies.
        if intersection_list:
            pts = [_seg1.point(_t1) for _T1, _seg1, _t1 in list(zip(*intersection_list))[0]]
            indices2remove = []
            for ind1 in range(len(pts)):
                for ind2 in range(ind1 + 1, len(pts)):
                    if abs(pts[ind1] - pts[ind2]) < tol:
                        # then there's a redundancy. Remove it.
                        indices2remove.append(ind2)
            intersection_list = [inter for ind, inter in
                                 enumerate(intersection_list) if
                                 ind not in indices2remove]
        return intersection_list

    def bbox(self):
        """returns bounding box in the form (xmin, xmax, ymin, ymax)."""
        bbs = [seg.bbox() for seg in self._segments]
        xmins, xmaxs, ymins, ymaxs = list(zip(*bbs))
        xmin = min(xmins)
        xmax = max(xmaxs)
        ymin = min(ymins)
        ymax = max(ymaxs)
        return xmin, xmax, ymin, ymax

    def cropped(self, T0, T1):
        """returns a cropped copy of the path."""
        assert 0 <= T0 <= 1 and 0 <= T1<= 1
        assert T0 != T1
        assert not (T0 == 1 and T1 == 0)

        if T0 == 1 and 0 < T1 < 1 and self.isclosed():
            return self.cropped(0, T1)

        if T1 == 1:
            seg1 = self[-1]
            t_seg1 = 1
            i1 = len(self) - 1
        else:
            seg1_idx, t_seg1 = self.T2t(T1)
            seg1 = self[seg1_idx]
            if np.isclose(t_seg1, 0):
                i1 = (self.index(seg1) - 1) % len(self)
                seg1 = self[i1]
                t_seg1 = 1
            else:
                i1 = self.index(seg1)
        if T0 == 0:
            seg0 = self[0]
            t_seg0 = 0
            i0 = 0
        else:
            seg0_idx, t_seg0 = self.T2t(T0)
            seg0 = self[seg0_idx]
            if np.isclose(t_seg0, 1):
                i0 = (self.index(seg0) + 1) % len(self)
                seg0 = self[i0]
                t_seg0 = 0
            else:
                i0 = self.index(seg0)

        if T0 < T1 and i0 == i1:
            new_path = Path(seg0.cropped(t_seg0, t_seg1))
        else:
            new_path = Path(seg0.cropped(t_seg0, 1))

            # T1<T0 must cross discontinuity case
            if T1 < T0:
                if not self.isclosed():
                    raise ValueError("This path is not closed, thus T0 must "
                                     "be less than T1.")
                else:
                    for i in range(i0 + 1, len(self)):
                        new_path.append(self[i])
                    for i in range(0, i1):
                        new_path.append(self[i])

            # T0<T1 straight-forward case
            else:
                for i in range(i0 + 1, i1):
                    new_path.append(self[i])

            if t_seg1 != 0:
                new_path.append(seg1.cropped(0, t_seg1))
        return new_path

    def radialrange(self, origin, return_all_global_extrema=False):
        """returns the tuples (d_min, t_min, idx_min), (d_max, t_max, idx_max)
        which minimize and maximize, respectively, the distance
        d = |self[idx].point(t)-origin|."""
        if return_all_global_extrema:
            raise NotImplementedError
        else:
            global_min = (np.inf, None, None)
            global_max = (0, None, None)
            for seg_idx, seg in enumerate(self):
                seg_global_min, seg_global_max = seg.radialrange(origin)
                if seg_global_min[0] < global_min[0]:
                    global_min = seg_global_min + (seg_idx,)
                if seg_global_max[0] > global_max[0]:
                    global_max = seg_global_max + (seg_idx,)
            return global_min, global_max

    def rotated(self, degs, origin=None):
        """Returns a copy of self rotated by `degs` degrees (CCW) around the
        point `origin` (a complex number).  By default `origin` is either
        `self.point(0.5)`, or in the case that self is an Arc object,
        `origin` defaults to `self.center`."""
        return rotate(self, degs, origin=origin)

    def translated(self, z0):
        """Returns a copy of self shifted by the complex quantity `z0` such
        that self.translated(z0).point(t) = self.point(t) + z0 for any t."""
        return translate(self, z0)

    def scaled(self, sx, sy=None, origin=0j):
        """Scale transform.  See `scale` function for further explanation."""
        return scale(self, sx=sx, sy=sy, origin=origin)

    def is_contained_by(self, other):
        """Returns true if the path is fully contained in other closed path"""
        assert isinstance(other, Path)
        assert other.isclosed()
        assert self != other

        if self.intersect(other, justonemode=True):
            return False

        pt = self.point(0)
        xmin, xmax, ymin, ymax = other.bbox()
        pt_in_bbox = (xmin <= pt.real <= xmax) and (ymin <= pt.imag <= ymax)

        if not pt_in_bbox:
            return False

        opt = complex(xmin-1, ymin-1)
        return path_encloses_pt(pt, opt, other)

    def approximate_arcs_with_cubics(self, error=0.1):
        """
        Iterates through this path and replaces any Arcs with cubic bezier curves.
        """
        tau = pi * 2
        sweep_limit = degrees(tau * error)
        for s in range(len(self)-1, -1, -1):
            segment = self[s]
            if not isinstance(segment, Arc):
                continue
            arc_required = int(ceil(abs(segment.delta) / sweep_limit))
            self[s:s+1] = list(segment.as_cubic_curves(arc_required))

    def approximate_arcs_with_quads(self, error=0.1):
        """
        Iterates through this path and replaces any Arcs with quadratic bezier curves.
        """
        tau = pi * 2
        sweep_limit = degrees(tau * error)
        for s in range(len(self)-1, -1, -1):
            segment = self[s]
            if not isinstance(segment, Arc):
                continue
            arc_required = int(ceil(abs(segment.delta) / sweep_limit))
            self[s:s+1] = list(segment.as_quad_curves(arc_required))

    def joints(self):
        """returns generator of segment joints 
        
        I.e. Path(s0, s1, s2, ..., sn).joints() returns generator 
            (s0, s1), (s1, s2), ..., (sn, s0)

        credit: https://docs.python.org/3/library/itertools.html#recipes
        """
        a, b = tee(self)
        next(b, None)
        return zip(a, b)

    def _tokenize_path(self, pathdef):
        for x in COMMAND_RE.split(pathdef):
            if x in COMMANDS:
                yield x
            for token in FLOAT_RE.findall(x):
                yield token

    def _parse_path(self, pathdef, current_pos=0j, tree_element=None):
        # In the SVG specs, initial movetos are absolute, even if
        # specified as 'm'. This is the default behavior here as well.
        # But if you pass in a current_pos variable, the initial moveto
        # will be relative to that current_pos. This is useful.
        elements = list(self._tokenize_path(pathdef))
        # Reverse for easy use of .pop()
        elements.reverse()

        segments = self._segments

        start_pos = None
        command = None

        while elements:

            if elements[-1] in COMMANDS:
                # New command.
                last_command = command  # Used by S and T
                command = elements.pop()
                absolute = command in UPPERCASE
                command = command.upper()
            else:
                # If this element starts with numbers, it is an implicit command
                # and we don't change the command. Check that it's allowed:
                if command is None:
                    raise ValueError("Unallowed implicit command in %s, position %s" % (
                        pathdef, len(pathdef.split()) - len(elements)))
                last_command = command  # Used by S and T

            if command == 'M':
                # Moveto command.
                x = elements.pop()
                y = elements.pop()
                pos = float(x) + float(y) * 1j
                if absolute:
                    current_pos = pos
                else:
                    current_pos += pos

                # when M is called, reset start_pos
                # This behavior of Z is defined in svg spec:
                # http://www.w3.org/TR/SVG/paths.html#PathDataClosePathCommand
                start_pos = current_pos

                # Implicit moveto commands are treated as lineto commands.
                # So we set command to lineto here, in case there are
                # further implicit commands after this moveto.
                command = 'L'

            elif command == 'Z':
                # Close path
                if not (current_pos == start_pos):
                    segments.append(Line(current_pos, start_pos))
                self._closed = True
                current_pos = start_pos
                command = None

            elif command == 'L':
                x = elements.pop()
                y = elements.pop()
                pos = float(x) + float(y) * 1j
                if not absolute:
                    pos += current_pos
                segments.append(Line(current_pos, pos))
                current_pos = pos

            elif command == 'H':
                x = elements.pop()
                pos = float(x) + current_pos.imag * 1j
                if not absolute:
                    pos += current_pos.real
                segments.append(Line(current_pos, pos))
                current_pos = pos

            elif command == 'V':
                y = elements.pop()
                pos = current_pos.real + float(y) * 1j
                if not absolute:
                    pos += current_pos.imag * 1j
                segments.append(Line(current_pos, pos))
                current_pos = pos

            elif command == 'C':
                control1 = float(elements.pop()) + float(elements.pop()) * 1j
                control2 = float(elements.pop()) + float(elements.pop()) * 1j
                end = float(elements.pop()) + float(elements.pop()) * 1j

                if not absolute:
                    control1 += current_pos
                    control2 += current_pos
                    end += current_pos

                segments.append(CubicBezier(current_pos, control1, control2, end))
                current_pos = end

            elif command == 'S':
                # Smooth curve. First control point is the "reflection" of
                # the second control point in the previous path.

                if last_command not in 'CS':
                    # If there is no previous command or if the previous command
                    # was not an C, c, S or s, assume the first control point is
                    # coincident with the current point.
                    control1 = current_pos
                else:
                    # The first control point is assumed to be the reflection of
                    # the second control point on the previous command relative
                    # to the current point.
                    control1 = current_pos + current_pos - segments[-1].control2

                control2 = float(elements.pop()) + float(elements.pop()) * 1j
                end = float(elements.pop()) + float(elements.pop()) * 1j

                if not absolute:
                    control2 += current_pos
                    end += current_pos

                segments.append(CubicBezier(current_pos, control1, control2, end))
                current_pos = end

            elif command == 'Q':
                control = float(elements.pop()) + float(elements.pop()) * 1j
                end = float(elements.pop()) + float(elements.pop()) * 1j

                if not absolute:
                    control += current_pos
                    end += current_pos

                segments.append(QuadraticBezier(current_pos, control, end))
                current_pos = end

            elif command == 'T':
                # Smooth curve. Control point is the "reflection" of
                # the second control point in the previous path.

                if last_command not in 'QT':
                    # If there is no previous command or if the previous command
                    # was not an Q, q, T or t, assume the first control point is
                    # coincident with the current point.
                    control = current_pos
                else:
                    # The control point is assumed to be the reflection of
                    # the control point on the previous command relative
                    # to the current point.
                    control = current_pos + current_pos - segments[-1].control

                end = float(elements.pop()) + float(elements.pop()) * 1j

                if not absolute:
                    end += current_pos

                segments.append(QuadraticBezier(current_pos, control, end))
                current_pos = end

            elif command == 'A':

                radius = float(elements.pop()) + float(elements.pop()) * 1j
                rotation = float(elements.pop())
                arc = float(elements.pop())
                sweep = float(elements.pop())
                end = float(elements.pop()) + float(elements.pop()) * 1j

                if not absolute:
                    end += current_pos

                if radius.real == 0 or radius.imag == 0:
                    # Note: In browsers AFAIK, zero radius arcs are displayed
                    # as lines (see "examples/zero-radius-arcs.svg").
                    # Thus zero radius arcs are substituted for lines here.
                    warn('Replacing degenerate (zero radius) Arc with a Line: '
                         'Arc(start={}, radius={}, rotation={}, large_arc={}, '
                         'sweep={}, end={})'.format(
                        current_pos, radius, rotation, arc, sweep, end) +
                         ' --> Line(start={}, end={})'
                         ''.format(current_pos, end))
                    segments.append(Line(current_pos, end))
                else:
                    segments.append(
                        Arc(current_pos, radius, rotation, arc, sweep, end))
                current_pos = end

        return segments
