"""This submodule contains tools for working with numpy.poly1d objects."""

# External Dependencies
from __future__ import division, absolute_import
from itertools import combinations
import numpy as np

# Internal Dependencies
from .misctools import isclose


def polyroots(p, realroots=False, condition=lambda r: True):
    """
    Returns the roots of a polynomial with coefficients given in p.
      p[0] * x**n + p[1] * x**(n-1) + ... + p[n-1]*x + p[n]
    INPUT:
    p - Rank-1 array-like object of polynomial coefficients.
    realroots - a boolean.  If true, only real roots will be returned  and the
        condition function can be written assuming all roots are real.
    condition - a boolean-valued function.  Only roots satisfying this will be
        returned.  If realroots==True, these conditions should assume the roots
        are real.
    OUTPUT:
    A list containing the roots of the polynomial.
    NOTE:  This uses np.isclose and np.roots"""
    roots = np.roots(p)
    if realroots:
        roots = [r.real for r in roots if isclose(r.imag, 0)]
    roots = [r for r in roots if condition(r)]

    duplicates = []
    for idx, (r1, r2) in enumerate(combinations(roots, 2)):
        if isclose(r1, r2):
            duplicates.append(idx)
    return [r for idx, r in enumerate(roots) if idx not in duplicates]


def polyroots01(p):
    """Returns the real roots between 0 and 1 of the polynomial with
    coefficients given in p,
      p[0] * x**n + p[1] * x**(n-1) + ... + p[n-1]*x + p[n]
    p can also be a np.poly1d object.  See polyroots for more information."""
    return polyroots(p, realroots=True, condition=lambda tval: 0 <= tval <= 1)


def rational_limit(f, g, t0):
    """Computes the limit of the rational function (f/g)(t)
    as t approaches t0."""
    assert isinstance(f, np.poly1d) and isinstance(g, np.poly1d)
    assert g != np.poly1d([0])
    if g(t0) != 0:
        return f(t0)/g(t0)
    elif f(t0) == 0:
        return rational_limit(f.deriv(), g.deriv(), t0)
    else:
        raise ValueError("Limit does not exist.")


def real(z):
    try:
        return np.poly1d(z.coeffs.real)
    except AttributeError:
        return z.real


def imag(z):
    try:
        return np.poly1d(z.coeffs.imag)
    except AttributeError:
        return z.imag


def poly_real_part(poly):
    """Deprecated."""
    return np.poly1d(poly.coeffs.real)


def poly_imag_part(poly):
    """Deprecated."""
    return np.poly1d(poly.coeffs.imag)
