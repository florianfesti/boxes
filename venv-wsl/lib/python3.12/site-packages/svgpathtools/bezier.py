"""This submodule contains tools that deal with generic, degree n, Bezier
curves.
Note:  Bezier curves here are always represented by the tuple of their control
points given by their standard representation."""

# External dependencies:
from __future__ import division, absolute_import, print_function
from math import factorial as fac, ceil, log, sqrt
from numpy import poly1d

# Internal dependencies
from .polytools import real, imag, polyroots, polyroots01
from .constants import FLOAT_EPSILON


# Evaluation ##################################################################

def n_choose_k(n, k):
    return fac(n)//fac(k)//fac(n-k)


def bernstein(n, t):
    """returns a list of the Bernstein basis polynomials b_{i, n} evaluated at
    t, for i =0...n"""
    t1 = 1-t
    return [n_choose_k(n, k) * t1**(n-k) * t**k for k in range(n+1)]


def bezier_point(p, t):
    """Evaluates the Bezier curve given by it's control points, p, at t.
    Note: Uses Horner's rule for cubic and lower order Bezier curves.
    Warning:  Be concerned about numerical stability when using this function
    with high order curves."""

    # begin arc support block ########################
    try:
        p.large_arc
        return p.point(t)
    except:
        pass
    # end arc support block ##########################

    deg = len(p) - 1
    if deg == 3:
        return p[0] + t*(
            3*(p[1] - p[0]) + t*(
                3*(p[0] + p[2]) - 6*p[1] + t*(
                    -p[0] + 3*(p[1] - p[2]) + p[3])))
    elif deg == 2:
        return p[0] + t*(
            2*(p[1] - p[0]) + t*(
                p[0] - 2*p[1] + p[2]))
    elif deg == 1:
        return p[0] + t*(p[1] - p[0])
    elif deg == 0:
        return p[0]
    else:
        bern = bernstein(deg, t)
        return sum(bern[k]*p[k] for k in range(deg+1))


# Conversion ##################################################################

def bezier2polynomial(p, numpy_ordering=True, return_poly1d=False):
    """Converts a tuple of Bezier control points to a tuple of coefficients
    of the expanded polynomial.
    return_poly1d : returns a numpy.poly1d object.  This makes computations
    of derivatives/anti-derivatives and many other operations quite quick.
    numpy_ordering : By default (to accommodate numpy) the coefficients will
    be output in reverse standard order."""
    if len(p) == 4:
        coeffs = (-p[0] + 3*(p[1] - p[2]) + p[3],
                  3*(p[0] - 2*p[1] + p[2]),
                  3*(p[1]-p[0]),
                  p[0])
    elif len(p) == 3:
        coeffs = (p[0] - 2*p[1] + p[2],
                  2*(p[1] - p[0]),
                  p[0])
    elif len(p) == 2:
        coeffs = (p[1]-p[0],
                  p[0])
    elif len(p) == 1:
        coeffs = p
    else:
        # https://en.wikipedia.org/wiki/Bezier_curve#Polynomial_form
        n = len(p) - 1
        coeffs = [fac(n)//fac(n-j) * sum(
            (-1)**(i+j) * p[i] / (fac(i) * fac(j-i)) for i in range(j+1))
            for j in range(n+1)]
        coeffs.reverse()
    if not numpy_ordering:
        coeffs = coeffs[::-1]  # can't use .reverse() as might be tuple
    if return_poly1d:
        return poly1d(coeffs)
    return coeffs


def polynomial2bezier(poly):
    """Converts a cubic or lower order Polynomial object (or a sequence of
    coefficients) to a CubicBezier, QuadraticBezier, or Line object as
    appropriate."""
    if isinstance(poly, poly1d):
        c = poly.coeffs
    else:
        c = poly
    order = len(c)-1
    if order == 3:
        bpoints = (c[3], c[2]/3 + c[3], (c[1] + 2*c[2])/3 + c[3],
                   c[0] + c[1] + c[2] + c[3])
    elif order == 2:
        bpoints = (c[2], c[1]/2 + c[2], c[0] + c[1] + c[2])
    elif order == 1:
        bpoints = (c[1], c[0] + c[1])
    else:
        raise AssertionError("This function is only implemented for linear, "
                             "quadratic, and cubic polynomials.")
    return bpoints


# Curve Splitting #############################################################

def split_bezier(bpoints, t):
    """Uses deCasteljau's recursion to split the Bezier curve at t into two
    Bezier curves of the same order."""
    def split_bezier_recursion(bpoints_left_, bpoints_right_, bpoints_, t_):
        if len(bpoints_) == 1:
            bpoints_left_.append(bpoints_[0])
            bpoints_right_.append(bpoints_[0])
        else:
            new_points = [None]*(len(bpoints_) - 1)
            bpoints_left_.append(bpoints_[0])
            bpoints_right_.append(bpoints_[-1])
            for i in range(len(bpoints_) - 1):
                new_points[i] = (1 - t_)*bpoints_[i] + t_*bpoints_[i + 1]
            bpoints_left_, bpoints_right_ = split_bezier_recursion(
                bpoints_left_, bpoints_right_, new_points, t_)
        return bpoints_left_, bpoints_right_

    bpoints_left = []
    bpoints_right = []
    bpoints_left, bpoints_right = \
        split_bezier_recursion(bpoints_left, bpoints_right, bpoints, t)
    bpoints_right.reverse()
    return bpoints_left, bpoints_right


def halve_bezier(p):

    # begin arc support block ########################
    try:
        p.large_arc
        return p.split(0.5)
    except:
        pass
    # end arc support block ##########################

    if len(p) == 4:
        return ([p[0], (p[0] + p[1])/2, (p[0] + 2*p[1] + p[2])/4,
                 (p[0] + 3*p[1] + 3*p[2] + p[3])/8],
                [(p[0] + 3*p[1] + 3*p[2] + p[3])/8,
                 (p[1] + 2*p[2] + p[3])/4, (p[2] + p[3])/2, p[3]])
    else:
        return split_bezier(p, 0.5)


# Bounding Boxes ##############################################################

def bezier_real_minmax(p):
    """returns the minimum and maximum for any real cubic bezier"""
    local_extremizers = [0, 1]
    if len(p) == 4:  # cubic case
        a = [p.real for p in p]
        denom = a[0] - 3*a[1] + 3*a[2] - a[3]
        if abs(denom) > FLOAT_EPSILON:  # check that denom != 0 accounting for floating point error
            delta = a[1]**2 - (a[0] + a[1])*a[2] + a[2]**2 + (a[0] - a[1])*a[3]
            if delta >= 0:  # otherwise no local extrema
                sqdelta = sqrt(delta)
                tau = a[0] - 2*a[1] + a[2]
                r1 = (tau + sqdelta)/denom
                r2 = (tau - sqdelta)/denom
                if 0 < r1 < 1:
                    local_extremizers.append(r1)
                if 0 < r2 < 1:
                    local_extremizers.append(r2)
            local_extrema = [bezier_point(a, t) for t in local_extremizers]
            return min(local_extrema), max(local_extrema)

    # find reverse standard coefficients of the derivative
    dcoeffs = bezier2polynomial(a, return_poly1d=True).deriv().coeffs

    # find real roots, r, such that 0 <= r <= 1
    local_extremizers += polyroots01(dcoeffs)
    local_extrema = [bezier_point(a, t) for t in local_extremizers]
    return min(local_extrema), max(local_extrema)


def bezier_bounding_box(bez):
    """returns the bounding box for the segment in the form
    (xmin, xmax, ymin, ymax).
    Warning: For the non-cubic case this is not particularly efficient."""

    # begin arc support block ########################
    try:
        bla = bez.large_arc
        return bez.bbox()  # added to support Arc objects
    except:
        pass
    # end arc support block ##########################

    if len(bez) == 4:
        xmin, xmax = bezier_real_minmax([p.real for p in bez])
        ymin, ymax = bezier_real_minmax([p.imag for p in bez])
        return xmin, xmax, ymin, ymax
    poly = bezier2polynomial(bez, return_poly1d=True)
    x = real(poly)
    y = imag(poly)
    dx = x.deriv()
    dy = y.deriv()
    x_extremizers = [0, 1] + polyroots(dx, realroots=True,
                                    condition=lambda r: 0 < r < 1)
    y_extremizers = [0, 1] + polyroots(dy, realroots=True,
                                    condition=lambda r: 0 < r < 1)
    x_extrema = [x(t) for t in x_extremizers]
    y_extrema = [y(t) for t in y_extremizers]
    return min(x_extrema), max(x_extrema), min(y_extrema), max(y_extrema)


def box_area(xmin, xmax, ymin, ymax):
    """
    INPUT: 2-tuple of cubics (given by control points)
    OUTPUT: boolean
    """
    return (xmax - xmin)*(ymax - ymin)


def interval_intersection_width(a, b, c, d):
    """returns the width of the intersection of intervals [a,b] and [c,d]
    (thinking of these as intervals on the real number line)"""
    return max(0, min(b, d) - max(a, c))


def boxes_intersect(box1, box2):
    """Determines if two rectangles, each input as a tuple
        (xmin, xmax, ymin, ymax), intersect."""
    xmin1, xmax1, ymin1, ymax1 = box1
    xmin2, xmax2, ymin2, ymax2 = box2
    if interval_intersection_width(xmin1, xmax1, xmin2, xmax2) and \
            interval_intersection_width(ymin1, ymax1, ymin2, ymax2):
        return True
    else:
        return False


# Intersections ###############################################################

class ApproxSolutionSet(list):
    """A class that behaves like a set but treats two elements , x and y, as
    equivalent if abs(x-y) < self.tol"""
    def __init__(self, tol):
        self.tol = tol

    def __contains__(self, x):
        for y in self:
            if abs(x - y) < self.tol:
                return True
        return False

    def appadd(self, pt):
        if pt not in self:
            self.append(pt)


class BPair(object):
    def __init__(self, bez1, bez2, t1, t2):
        self.bez1 = bez1
        self.bez2 = bez2
        self.t1 = t1  # t value to get the mid point of this curve from cub1
        self.t2 = t2  # t value to get the mid point of this curve from cub2


def bezier_intersections(bez1, bez2, longer_length, tol=1e-8, tol_deC=1e-8):
    """INPUT:
    bez1, bez2 = [P0,P1,P2,...PN], [Q0,Q1,Q2,...,PN] defining the two
    Bezier curves to check for intersections between.
    longer_length - the length (or an upper bound) on the longer of the two
    Bezier curves.  Determines the maximum iterations needed together with tol.
    tol - is the smallest distance that two solutions can differ by and still
    be considered distinct solutions.
    OUTPUT: a list of tuples (t,s) in [0,1]x[0,1] such that
        abs(bezier_point(bez1[0],t) - bezier_point(bez2[1],s)) < tol_deC
    Note: This will return exactly one such tuple for each intersection
    (assuming tol_deC is small enough)."""
    maxits = int(ceil(1-log(tol_deC/longer_length)/log(2)))
    pair_list = [BPair(bez1, bez2, 0.5, 0.5)]
    intersection_list = []
    k = 0
    approx_point_set = ApproxSolutionSet(tol)
    while pair_list and k < maxits:
        new_pairs = []
        delta = 0.5**(k + 2)
        for pair in pair_list:
            bbox1 = bezier_bounding_box(pair.bez1)
            bbox2 = bezier_bounding_box(pair.bez2)
            if boxes_intersect(bbox1, bbox2):
                if box_area(*bbox1) < tol_deC and box_area(*bbox2) < tol_deC:
                    point = bezier_point(bez1, pair.t1)
                    if point not in approx_point_set:
                        approx_point_set.append(point)
                        # this is the point in the middle of the pair
                        intersection_list.append((pair.t1, pair.t2))

                    # this prevents the output of redundant intersection points
                    for otherPair in pair_list:
                        if pair.bez1 == otherPair.bez1 or \
                                pair.bez2 == otherPair.bez2 or \
                                pair.bez1 == otherPair.bez2 or \
                                pair.bez2 == otherPair.bez1:
                            pair_list.remove(otherPair)
                else:
                    (c11, c12) = halve_bezier(pair.bez1)
                    (t11, t12) = (pair.t1 - delta, pair.t1 + delta)
                    (c21, c22) = halve_bezier(pair.bez2)
                    (t21, t22) = (pair.t2 - delta, pair.t2 + delta)
                    new_pairs += [BPair(c11, c21, t11, t21),
                                  BPair(c11, c22, t11, t22),
                                  BPair(c12, c21, t12, t21),
                                  BPair(c12, c22, t12, t22)]
        pair_list = new_pairs
        k += 1
    if k >= maxits:
        raise Exception("bezier_intersections has reached maximum "
                        "iterations without terminating... "
                        "either there's a problem/bug or you can fix by "
                        "raising the max iterations or lowering tol_deC")
    return intersection_list


def bezier_by_line_intersections(bezier, line):
    """Returns tuples (t1,t2) such that bezier.point(t1) ~= line.point(t2)."""
    # The method here is to translate (shift) then rotate the complex plane so
    # that line starts at the origin and proceeds along the positive real axis.
    # After this transformation, the intersection points are the real roots of
    # the imaginary component of the bezier for which the real component is
    # between 0 and abs(line[1]-line[0])].
    assert len(line[:]) == 2
    assert line[0] != line[1]
    if not any(p != bezier[0] for p in bezier):
        raise ValueError("bezier is nodal, use "
                         "bezier_by_line_intersection(bezier[0], line) "
                         "instead for a bool to be returned.")

    # First let's shift the complex plane so that line starts at the origin
    shifted_bezier = [z - line[0] for z in bezier]
    shifted_line_end = line[1] - line[0]
    line_length = abs(shifted_line_end)

    # Now let's rotate the complex plane so that line falls on the x-axis
    rotation_matrix = line_length/shifted_line_end
    transformed_bezier = [rotation_matrix*z for z in shifted_bezier]

    # Now all intersections should be roots of the imaginary component of
    # the transformed bezier
    transformed_bezier_imag = [p.imag for p in transformed_bezier]
    coeffs_y = bezier2polynomial(transformed_bezier_imag)
    roots_y = list(polyroots01(coeffs_y))  # returns real roots 0 <= r <= 1

    transformed_bezier_real = [p.real for p in transformed_bezier]
    intersection_list = []
    for bez_t in set(roots_y):
        xval = bezier_point(transformed_bezier_real, bez_t)
        if 0 <= xval <= line_length:
            line_t = xval/line_length
            intersection_list.append((bez_t, line_t))
    return intersection_list

