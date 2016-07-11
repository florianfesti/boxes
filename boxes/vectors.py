# Copyright (C) 2013-2014 Florian Festi
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

def normalize(v):
    "set lenght of vector to one"
    l = (v[0]**2+v[1]**2)**0.5
    return (v[0]/l, v[1]/l)

def vdiff(p1, p2):
    "vector from point1 to point2"
    return (p2[0]-p1[0], p2[1]-p1[1])

def vadd(v1, v2):
    "Sum of two vectors"
    return (v1[0]+ v2[0], v1[1]+v2[1])

def vorthogonal(v):
    "orthogonal vector"
    "Orthogonal vector"
    return (-v[1], v[0])

def vscalmul(v, a):
    "scale vector by a"
    return (a*v[0], a*v[1])

def dotproduct(v1, v2):
    "Dot product"
    return v1[0]*v2[0]+v1[1]*v2[1]

def kerf(points, k):
    """Outset points by k
    Assumes a closed loop of points
    """
    result = []
    lp = len(points)
    for i in range(len(points)):
        # get normalized orthogonals of both segments
        v1 = vorthogonal(normalize(vdiff(points[i-1], points[i])))
        v2 = vorthogonal(normalize(vdiff(points[i], points[(i+1) % lp])))
        # direction the point has to move
        d = normalize(vadd(v1, v2))
        # cos of the half the angle between the segments
        cos_alpha = dotproduct(v1, d)
        result.append(vadd(points[i], vscalmul(d, -k/cos_alpha)))
    return result
