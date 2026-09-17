"""This submodule contains functions related to smoothing paths of Bezier
curves."""

# External Dependencies
from __future__ import division, absolute_import, print_function

# Internal Dependencies
from .path import Path, CubicBezier, Line
from .misctools import isclose
from .paths2svg import disvg


def is_differentiable(path, tol=1e-8):
    for idx in range(len(path)):
        u = path[(idx-1) % len(path)].unit_tangent(1)
        v = path[idx].unit_tangent(0)
        u_dot_v = u.real*v.real + u.imag*v.imag
        if abs(u_dot_v - 1) > tol:
            return False
    return True


def kinks(path, tol=1e-8):
    """returns indices of segments that start on a non-differentiable joint."""
    kink_list = []
    for idx in range(len(path)):
        if idx == 0 and not path.isclosed():
            continue
        try:
            u = path[(idx - 1) % len(path)].unit_tangent(1)
            v = path[idx].unit_tangent(0)
            u_dot_v = u.real*v.real + u.imag*v.imag
            flag = False
        except ValueError:
            flag = True

        if flag or abs(u_dot_v - 1) > tol:
            kink_list.append(idx)
    return kink_list


def _report_unfixable_kinks(_path, _kink_list):
    mes = ("\n%s kinks have been detected at that cannot be smoothed.\n"
           "To ignore these kinks and fix all others, run this function "
           "again with the second argument 'ignore_unfixable_kinks=True' "
           "The locations of the unfixable kinks are at the beginnings of "
           "segments: %s" % (len(_kink_list), _kink_list))
    disvg(_path, nodes=[_path[idx].start for idx in _kink_list])
    raise Exception(mes)


def smoothed_joint(seg0, seg1, maxjointsize=3, tightness=1.99):
    """ See Andy's notes on
    Smoothing Bezier Paths for an explanation of the method.
    Input: two segments seg0, seg1 such that seg0.end==seg1.start, and
    jointsize, a positive number

    Output: seg0_trimmed, elbow, seg1_trimmed, where elbow is a cubic bezier
        object that smoothly connects seg0_trimmed and seg1_trimmed.

    """
    assert seg0.end == seg1.start
    assert 0 < maxjointsize
    assert 0 < tightness < 2
#    sgn = lambda x:x/abs(x)
    q = seg0.end

    try: v = seg0.unit_tangent(1)
    except: v = seg0.unit_tangent(1 - 1e-4)
    try: w = seg1.unit_tangent(0)
    except: w = seg1.unit_tangent(1e-4)

    max_a = maxjointsize / 2
    a = min(max_a, min(seg1.length(), seg0.length()) / 20)
    if isinstance(seg0, Line) and isinstance(seg1, Line):
        '''
        Note: Letting
            c(t) = elbow.point(t), v= the unit tangent of seg0 at 1, w = the
            unit tangent vector of seg1 at 0,
            Q = seg0.point(1) = seg1.point(0), and a,b>0 some constants.
            The elbow will be the unique CubicBezier, c, such that
            c(0)= Q-av, c(1)=Q+aw, c'(0) = bv, and c'(1) = bw
            where a and b are derived above/below from tightness and
            maxjointsize.
        '''
#        det = v.imag*w.real-v.real*w.imag
        # Note:
        # If det is negative, the curvature of elbow is negative for all
        # real t if and only if b/a > 6
        # If det is positive, the curvature of elbow is negative for all
        # real t if and only if b/a < 2

#        if det < 0:
#            b = (6+tightness)*a
#        elif det > 0:
#            b = (2-tightness)*a
#        else:
#            raise Exception("seg0 and seg1 are parallel lines.")
        b = (2 - tightness)*a
        elbow = CubicBezier(q - a*v, q - (a - b/3)*v, q + (a - b/3)*w, q + a*w)
        seg0_trimmed = Line(seg0.start, elbow.start)
        seg1_trimmed = Line(elbow.end, seg1.end)
        return seg0_trimmed, [elbow], seg1_trimmed
    elif isinstance(seg0, Line):
        '''
        Note: Letting
            c(t) = elbow.point(t), v= the unit tangent of seg0 at 1,
            w = the unit tangent vector of seg1 at 0,
            Q = seg0.point(1) = seg1.point(0), and a,b>0 some constants.
            The elbow will be the unique CubicBezier, c, such that
            c(0)= Q-av, c(1)=Q, c'(0) = bv, and c'(1) = bw
            where a and b are derived above/below from tightness and
            maxjointsize.
        '''
#        det = v.imag*w.real-v.real*w.imag
        # Note: If g has the same sign as det, then the curvature of elbow is
        # negative for all real t if and only if b/a < 4
        b = (4 - tightness)*a
#        g = sgn(det)*b
        elbow = CubicBezier(q - a*v, q + (b/3 - a)*v, q - b/3*w, q)
        seg0_trimmed = Line(seg0.start, elbow.start)
        return seg0_trimmed, [elbow], seg1
    elif isinstance(seg1, Line):
        args = (seg1.reversed(), seg0.reversed(), maxjointsize, tightness)
        rseg1_trimmed, relbow, rseg0 = smoothed_joint(*args)
        elbow = relbow[0].reversed()
        return seg0, [elbow], rseg1_trimmed.reversed()
    else:
        # find a point on each seg that is about a/2 away from joint.  Make
        # line between them.
        t0 = seg0.ilength(seg0.length() - a/2)
        t1 = seg1.ilength(a/2)
        seg0_trimmed = seg0.cropped(0, t0)
        seg1_trimmed = seg1.cropped(t1, 1)
        seg0_line = Line(seg0_trimmed.end, q)
        seg1_line = Line(q, seg1_trimmed.start)

        args = (seg0_trimmed, seg0_line, maxjointsize, tightness)
        dummy, elbow0, seg0_line_trimmed = smoothed_joint(*args)

        args = (seg1_line, seg1_trimmed, maxjointsize, tightness)
        seg1_line_trimmed, elbow1, dummy = smoothed_joint(*args)

        args = (seg0_line_trimmed, seg1_line_trimmed, maxjointsize, tightness)
        seg0_line_trimmed, elbowq, seg1_line_trimmed = smoothed_joint(*args)

        elbow = elbow0 + [seg0_line_trimmed] + elbowq + [seg1_line_trimmed] + elbow1
        return seg0_trimmed, elbow, seg1_trimmed


def smoothed_path(path, maxjointsize=3, tightness=1.99, ignore_unfixable_kinks=False):
    """returns a path with no non-differentiable joints."""
    if len(path) == 1:
        return path

    assert path.iscontinuous()

    sharp_kinks = []
    new_path = [path[0]]
    for idx in range(len(path)):
        if idx == len(path)-1:
            if not path.isclosed():
                continue
            else:
                seg1 = new_path[0]
        else:
            seg1 = path[idx + 1]
        seg0 = new_path[-1]

        try:
            unit_tangent0 = seg0.unit_tangent(1)
            unit_tangent1 = seg1.unit_tangent(0)
            flag = False
        except ValueError:
            flag = True  # unit tangent not well-defined

        if not flag and isclose(unit_tangent0, unit_tangent1):  # joint is already smooth
            if idx != len(path)-1:
                new_path.append(seg1)
            continue
        else:
            kink_idx = (idx + 1) % len(path)  # kink at start of this seg
            if not flag and isclose(-unit_tangent0, unit_tangent1):
                # joint is sharp 180 deg (must be fixed manually)
                new_path.append(seg1)
                sharp_kinks.append(kink_idx)
            else:  # joint is not smooth, let's  smooth it.
                args = (seg0, seg1, maxjointsize, tightness)
                new_seg0, elbow_segs, new_seg1 = smoothed_joint(*args)
                new_path[-1] = new_seg0
                new_path += elbow_segs
                if idx == len(path) - 1:
                    new_path[0] = new_seg1
                else:
                    new_path.append(new_seg1)

    # If unfixable kinks were found, let the user know
    if sharp_kinks and not ignore_unfixable_kinks:
        _report_unfixable_kinks(path, sharp_kinks)

    return Path(*new_path)
