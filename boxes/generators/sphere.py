# Copyright (C) 2025 Jolien and Josse Franke-Muller,
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

# A gore is term in globe-making that describes a lens-shaped figure (with a map usually) that is wrapped around a sphere to create a globe
# The coordinate system of the 3D object is x,y,z. As to not confuse it with the coordinate system of the gores, we use x,u (x is the same in both systems)
# Explanation of the math will be in a separate file

import math

import numpy
from boxes import *
from collections import namedtuple

class Sphere(Boxes):
    """Actually not a sphere, but a hosohedron. Also not actually a box, but a globe, lamp, ornament or whatever you want it to be."""

    description = """With Voronoi pattern added:\n![Voronoi patterned Lamp](static/samples/Sphere-2.jpg)"""

    ui_group = "Misc"

    def __init__(self) -> None:
        super().__init__()
        self.argparser.add_argument(
            "--sphere_radius",  action="store", type=float, default=100,
            help="The radius of the assembled sphere")
        self.argparser.add_argument(
            "--amount_gores",  action="store", type=int, default=6,
            help="The amount of gores/parts you want the sphere to have, has to be at least 3")
        self.argparser.add_argument(
            "--top_hole_radius",  action="store", type=float, default=30,
            help="The size of the circular hole at the top")
        self.argparser.add_argument(
            "--bottom_hole_radius", action="store", type=float, default=80,
            help="The size of the polygonal hole at the bottom")
        self.argparser.add_argument(
            "--scoring_lines", action="store", type=boolarg, default=False,
            help="Add scoring lines to easier fold tabs")
        self.argparser.add_argument(
            "--cable_hook", action="store", type=int, default=0,
            help="A hook to hang the sphere on a cable (for e.g. lamps), the amount of gores that have a hook")
        self.argparser.add_argument(
            "--cable_hook_radius", action="store", type=float, default=3,
            help="The radius of the cable for the cable hook")

        defaultgroup = self.argparser._action_groups[1]
        for action in defaultgroup._actions:
            if action.dest == 'tabs':
                action.type = int
                action.default = 6
                action.help = "The number of tabs. This has to be an even number"
            if action.dest == 'thickness':
                action.default = 1.0
        defaultgroup.add_argument( # I placed it here, hoping it would be grouped together with tabs, but this doesn't work (tips welcome)
            "--corner_tab", action="store", type=float, default=10.0,
            help="The length of the tabs on the corners (in mm)(not supported everywhere). Keep as small as your material strength allows for cleaner result")
        self.argparser.add_argument(
            "--tab_width", action="store", type=float, default=5.0,
            help="The width of the tabs (in mm)")

    Curve = namedtuple('Curve', ["degrees", "radius"])
    TurnToDirection = namedtuple('TurnToDirection', ["degrees"])

    def calculateXOfGore(self, u):
        return math.sin(u / self.sphere_radius) * self.halfBellyLens

    def coordinatesPartOfGore(self, u_start, u_stop, isRight, includeFinalTurn=False):
        N = self.resolution
        points = []

        direction = 1
        if (not isRight):
            direction = -1

        for i in numpy.linspace(u_start, u_stop, N + 1):
            u = i
            x = direction * self.calculateXOfGore(u)
            points.append((x, u))

        if includeFinalTurn:
            if(isRight):
                points.append(self.TurnToDirection(math.degrees(self.calculateTangentAngle(u_stop))))
            else:
                unmirroredTangentAngle = self.calculateTangentAngle(u_stop)
                heading = 90 - unmirroredTangentAngle + 180
                points.append(self.TurnToDirection(math.degrees(heading)))

        return(points)

    def coordinatesPartOfOffset(self, u_start, u_stop, normalDistance, isRight, includeFinalTurn=False):                           # see wiki of Parallel Curves x_d(t) = x(t) + d * n(t)
        N = self.resolution
        points = []

        direction = 1
        if (not isRight):
            direction = -1

        for i in numpy.linspace(u_start, u_stop, N + 1):
            u = i
            u_offset = u + normalDistance * math.sin(self.calculateNormalAngle(u))
            x_offset = direction * (self.calculateXOfGore(u) + normalDistance * math.cos(self.calculateNormalAngle(u)))
            points.append((x_offset, u_offset))
        if includeFinalTurn:
            if(isRight):
                points.append(self.TurnToDirection(math.degrees(self.calculateTangentAngle(u_stop))))
            else:
                unmirroredTangentAngle = self.calculateTangentAngle(u_stop)
                heading = 90 - unmirroredTangentAngle + 180
                points.append(self.TurnToDirection(math.degrees(heading)))

        return(points)

    @holeCol
    def scoringLines(self, u_start, u_stop, isRight):
        points = self.coordinatesPartOfGore(u_start, u_stop, isRight)
        self.drawPoints(points, kerfdir=0, close=False)

    def calculateNormalAngle(self, u):
        return self.calculateTangentAngle(u) - 90 * math.pi / 180

    def calculateTangentAngle(self, u):                                                                              #derivatives of u (goreHeigth) and x (cos(pi * i) * a * pi)
        return math.atan2(self.gore_heigth, math.cos(math.pi * (u / self.gore_heigth)) * math.pi * self.halfBellyLens) #atan2 to prevent division by 0 and quadrant (opposite sides not possible now)

    def normalCompensation(self, u): # So the offset can be drawn up to the same horizontal line as the equivalent u of the gore
        return math.sin(self.calculateNormalAngle(u)) * self.tab_width

    def calculateXofTopAndGoreIntersection(self):
        return math.sqrt(self.halfBellyLens**2 * self.top_hole_radius**2 / (self.halfBellyLens**2 + self.sphere_radius**2))

    def calculateXofOffsetGore(self, u):
        return self.calculateXOfGore(u) + math.cos(self.calculateNormalAngle(u)) * self.tab_width

    def calculateUpperUOfGore(self, x):
        return (math.pi - math.asin(x / self.halfBellyLens)) * self.sphere_radius

    def calculateUOfBottomHole(self):
        theta = math.asin(self.bottom_hole_radius / self.sphere_radius)
        return (theta / math.pi) * self.gore_heigth

    def calculateLengthGoreTab(self):
        N = self.resolution
        length = 0

        x1 = self.calculateXOfGore(self.u_tabPoints[0])
        for i in numpy.linspace(self.u_tabPoints[0], self.u_tabPoints[1], N + 1):
            u = i
            x2 = self.calculateXOfGore(u)
            dx = x2 - x1
            du = (self.u_tabPoints[0] - self.u_tabPoints[1]) / N
            length += math.sqrt((du**2) + dx**2)
            x1 = x2

        return(length)

    def coordinatesTopHole(self, x_start, x_stop):
        N = self.resolution
        points = []

        for i in range (N + 1):
            x = (x_stop - x_start) / N * i + x_start
            u = (math.pi - math.asin(math.sqrt(self.top_hole_radius**2 - x**2) / self.sphere_radius)) * self.sphere_radius
            points.append((x, u))

        return points

    def coordinatesCableHook(self):
        skewfactor = 0.8
        topWidth = 2 * self.x_rightGoreTop
        delta = (topWidth * (1 - skewfactor)) / 2
        outercurveRadius = (topWidth * skewfactor) / 2
        tipRadius = (outercurveRadius * 2 - self.cable_hook_radius * 2) / 4

        points = []
        points.append((self.x_rightGoreTop - delta, self.u_goreTop + topWidth))
        points.append(self.TurnToDirection(90))
        points.append(self.Curve(180, outercurveRadius))
        points.append(0)
        points.append(self.Curve(180, tipRadius))
        points.append(0)
        points.append(self.Curve(-180, self.cable_hook_radius))
        points.append(0)
        points.append(self.Curve(-90, outercurveRadius))
        points.append(0)
        points.append(((-self.x_rightGoreTop + delta + (tipRadius * 2 + (self.cable_hook_radius * 2) - outercurveRadius)),
                       self.u_goreTop + topWidth - outercurveRadius))

        return points

    def coordinatesToPolyline(self, points):
        polyPoints = [0]
        distance = 0
        previousWasCurve = False
        previousAngle = 0
        i = 1

        while i < len(points):
            if (isinstance(points[i], self.Curve)):
                polyPoints.extend([points[i], points[i + 1]])
                previousAngle += points[i].degrees
                previousWasCurve = True
                i += 2
            elif isinstance(points[i], self.TurnToDirection):
                relativeAngle = points[i].degrees - previousAngle
                relativeAngle = (relativeAngle + 180) % 360 - 180
                polyPoints.extend([relativeAngle, 0])
                previousAngle = points[i].degrees
                i += 1
            else:
                if (previousWasCurve):
                    previousWasCurve = False
                    i += 1
                    continue

                absoluteAngle = math.degrees(math.atan2(points[i][1] - points[i - 1][1], points[i][0] - points[i - 1][0]))
                relativeAngle = absoluteAngle - previousAngle
                relativeAngle = (relativeAngle + 180) % 360 - 180

                distance = math.dist(points[i], points[i - 1])

                if (distance > 0.0001):
                    polyPoints.append(relativeAngle)
                    polyPoints.append(distance)
                    previousWasCurve = False
                    previousAngle = absoluteAngle
                i += 1

        return(polyPoints)

        # Tabs
        # Surrounding spaces don't make much sense in this case, so I've left those out
        # I've changed tabs from mm to amount, because the first and last tab are very important to keep the shape nice
    def coordinatesTabStart(self):
        return [self.Curve(-180, self.thickness / 2), 0, self.Curve(180, (self.tab_width - self.thickness) / 2), 0]

    def coordinatesTabEnd(self):
        return [self.Curve(180, (self.tab_width - self.thickness) / 2), 0, self.Curve(-180, self.thickness / 2), 0]

        # This function divides the tabs over the length of u, not the length of the gore itself. Shortcuts were taken
    def divideGore(self, numberOfTabs, tinyTabLength):
        return numpy.linspace(self.u_goreBottom + tinyTabLength,
                              self.u_goreTop - tinyTabLength,
                              num=numberOfTabs + 1)

    def assemble(self, hook=False):
        coordinates = []
        coordinates.extend(self.coordinatesPartOfGore(self.u_goreBottom, self.u_tabPoints[0], True, True))

        for i in range(0, len(self.u_tabPoints) - 1, 2):
            coordinates.extend(self.coordinatesTabStart())
            coordinates.extend(self.coordinatesPartOfOffset(self.u_tabPoints[i], self.u_tabPoints[i + 1], self.tab_width, True, True))
            coordinates.extend(self.coordinatesTabEnd())
            coordinates.extend(self.coordinatesPartOfGore(self.u_tabPoints[i + 1], self.u_tabPoints[i + 2], True, True))

        lastTabPoint = self.u_tabPoints[-1]
        upperCornerU = lastTabPoint + self.normalCompensation(lastTabPoint)

        coordinates.extend(self.coordinatesTabStart())

        if (upperCornerU < self.u_goreTop):
            coordinates.extend(self.coordinatesPartOfOffset(lastTabPoint, self.u_goreTop - self.normalCompensation(self.u_goreTop), self.tab_width, True)) # line is not entirely straight, because te normalcompensation is simplified (should be at a bit lower u)
        else:
            coordinates.extend([(self.calculateXofOffsetGore(lastTabPoint), upperCornerU)])
        coordinates.extend([(self.x_rightGoreTop, self.u_goreTop)])

        if (hook):
            coordinates.extend(self.coordinatesCableHook())
        else:
            coordinates.extend(self.coordinatesTopHole(self.x_rightGoreTop, -self.x_rightGoreTop))

        #Left half
        coordinates.extend(self.coordinatesPartOfGore(self.u_goreTop, lastTabPoint, False))

        for i in range(len(self.u_tabPoints) - 1, 0, -2):
            coordinates.extend(self.coordinatesTabStart())
            coordinates.extend(self.coordinatesPartOfOffset(self.u_tabPoints[i], self.u_tabPoints[i - 1], self.tab_width, False))
            coordinates.extend(self.coordinatesTabEnd())
            coordinates.extend(self.coordinatesPartOfGore(self.u_tabPoints[i - 1], self.u_tabPoints[i - 2], False))

        firstTabPoint = self.u_tabPoints[0]
        lowerCornerU = firstTabPoint + self.normalCompensation(firstTabPoint)

        coordinates.extend(self.coordinatesTabStart())

        if (lowerCornerU > self.u_goreBottom):
            coordinates.extend(self.coordinatesPartOfOffset(firstTabPoint, self.u_goreBottom - self.normalCompensation(self.u_goreBottom), self.tab_width, False))
        else:
            coordinates.extend([(-self.calculateXofOffsetGore(firstTabPoint), lowerCornerU)])
        coordinates.extend([(-self.x_rightGoreBottom, self.u_goreBottom)])

        coordinates.extend([(self.x_rightGoreBottom, self.u_goreBottom)])

        return coordinates


    def render(self):
        if self.tabs % 2 == 1:
            raise ValueError("The number of tabs has to be even")
        if self.tab_width <= self.thickness:
            raise ValueError("The tab width has to be larger than the thickness of the material")
        if self.amount_gores < 3:
            raise ValueError("The amount of gores has to be at least 3")
        if self.top_hole_radius < 0:
            raise ValueError("The top hole radius cannot be negative")
        if self.top_hole_radius > self.sphere_radius:
            raise ValueError("The top hole radius cannot be larger than the sphere radius")
        if self.bottom_hole_radius < 0:
            raise ValueError("The bottom hole radius cannot be negative")
        if self.bottom_hole_radius > self.sphere_radius:
            raise ValueError("The bottom hole radius cannot be larger than the sphere radius")
        if self.corner_tab < 0:
            raise ValueError("The corner tab cannot be negative")
        if self.sphere_radius < 0:
            raise ValueError("The sphere radius cannot be negative")
        if self.thickness / 2 < self.burn:
            raise ValueError("The material thickness has to be at least twice the burn thickness")
        if self.cable_hook > self.amount_gores:
            raise ValueError("The amount of hooks cannot be larger than the amount of gores")


        self.resolution = int(self.sphere_radius / 10)  # This is arbitrary. I just want the resolution to be proportional to the total size
        self.gore_heigth = math.pi * self.sphere_radius  # the midline of the gore is the same as the line on the sphere, so half a circumference
        self.bellyLens = 2 * math.tan((2 * math.pi) / (2 * self.amount_gores)) * self.sphere_radius
        self.halfBellyLens = self.bellyLens / 2
        self.x_rightGoreTop = self.calculateXofTopAndGoreIntersection()

        if self.cable_hook_radius + 1 > 0.8 * self.x_rightGoreTop:
            raise ValueError("The cable hook radius is too big for this size top hole")

        self.u_goreTop = self.calculateUpperUOfGore(self.x_rightGoreTop)
        self.u_goreBottom = self.calculateUOfBottomHole()
        self.x_rightGoreBottom = self.calculateXOfGore(self.u_goreBottom)

        self.u_tabPoints = self.divideGore(self.tabs, self.corner_tab)

        if self.calculateLengthGoreTab() < (self.tab_width - self.thickness):
            raise ValueError("Too many tabs")

        self.moveTo(-self.halfBellyLens, 30)

        moveX = self.bellyLens + self.tab_width * 2 + 30

        drawHook = self.cable_hook
        for i in range(self.amount_gores):

            if (drawHook > 0):
                polyPoints = self.coordinatesToPolyline(self.assemble(True))
            else:
                polyPoints = self.coordinatesToPolyline(self.assemble())

            self.ctx.save()
            self.moveTo(0, -self.burn)
            self.polyline(*polyPoints)
            self.ctx.restore()

            if self.scoring_lines:
                self.ctx.save()
                self.moveTo(-self.calculateXOfGore(self.u_goreBottom), - self.u_goreBottom)

                for i in range(0, len(self.u_tabPoints) - 1, 2):
                    self.scoringLines(self.u_tabPoints[i], self.u_tabPoints[i + 1], True)
                self.scoringLines(self.u_tabPoints[-1], self.u_goreTop, True)
                for i in range(len(self.u_tabPoints) - 1, 0, -2):
                    self.scoringLines(self.u_tabPoints[i], self.u_tabPoints[i - 1], False)
                self.scoringLines(self.u_tabPoints[0], self.u_goreBottom, False)
                self.ctx.restore()

            drawHook -= 1

            self.moveTo(moveX, 0)
