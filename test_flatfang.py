#!/usr/bin/env python3

from boxes import Boxes

class TestFlatFang(Boxes):
    """Simple test box to verify flatfang lid generation"""
    ui_group = "Box"

    def __init__(self):
        super().__init__()
        self.buildArgParser(x=80, y=60, h=40)

    def render(self):
        self.rectangularWall(self.x, self.y, "ffff", move="up", label="bottom")
        self.rectangularWall(self.x, self.y, "FFFF", move="up", label="front")
        self.rectangularWall(self.x, self.y, "FFFF", move="up", label="back")
        self.rectangularWall(self.y, self.h, "FfFf", move="up", label="left")
        self.rectangularWall(self.y, self.h, "FfFf", move="up", label="right")
        self.lid(self.x, self.y)

if __name__ == "__main__":
    t = TestFlatFang()
    t.parseArgs(["--help"])
    t.parseArgs(["--lid_style", "flatfang"])
    t.render()
