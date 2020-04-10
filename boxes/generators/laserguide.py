"""Generator for a Laserguide."""

from copy import deepcopy

from boxes import Boxes
from boxes.edges import FingerJointSettings
from boxes import Color


class LaserGuide(Boxes):
    """A guide for easier lasering."""
    ui_group = "Box"
    length = 880
    height = 580
    x = 47
    y = 64
    h = 15

    def __init__(self):
        super().__init__()

    def render(self):
        x, y = self.x + 13, self.y + 13
        
        self.hole(0, 0, d=3)
        self.polyline(x, 90, self.height - y, -90, self.length - x, 90,
                      y, 90, self.length, 90, self.height)
        self.hole(0, 0, d=3)

        for start in range(-10, -self.height, -100):
            self.fingerHolesAt(start, 10, 30, 180)

        for start in range(10, self.length, 100):
            self.fingerHolesAt(-(self.height - 10), start, 30, 90)
            
        self.set_source_color(Color.RED)
        self.moveTo(-(self.height - y) + 1, self.x + self.h - 1) 
        for i in range(0, 11):
            self.rectangularWall(30, self.h, 'eefe', move='right')

