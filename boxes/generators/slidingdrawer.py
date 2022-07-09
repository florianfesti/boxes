from boxes import *

class SlidingDrawer(Boxes):
    """Sliding drawer box"""

    ui_group = "Box"

    def __init__(self):
        Boxes.__init__(self)
        self.buildArgParser(x=60, y=100, h=30, outside='true')
        self.addSettingsArgs(edges.FingerJointSettings, finger=2.0, space=2.0)
        self.addSettingsArgs(edges.GroovedSettings, width=0.4)

        self.argparser.add_argument(
            "--play",  action="store", type=float, default=0.15,
            help="play between the two parts as multipleof the wall thickness")

    def render(self):

        x, y, h = self.x, self.y, self.h
        x = self.adjustSize(x)
        y = self.adjustSize(y)
        h = self.adjustSize(h)

        t = self.thickness
        p = self.play * t

        y = y + t
        if not self.outside:
            x = x + 4*t+ 2*p
            y = y + 3*t+ 2*p
            h = h + 3*t+ 2*p

        x2 = x - (2*t + 2*p)
        y2 = y - (2*t + 2*p)
        h2 = h - (t + 2*p)

        self.rectangularWall(x2, h2, "FFzF", label="in box wall", move="right")
        self.rectangularWall(y2, h2, "ffef", label="in box wall", move="up")
        self.rectangularWall(y2, h2, "ffef", label="in box wall")
        self.rectangularWall(x2, h2, "FFeF", label="in box wall", move="left up")
        self.rectangularWall(y2, x2, "FfFf", label="in box bottom", move="up")

        self.rectangularWall(y, x, "FFFe", label="out box bottom", move="right")
        self.rectangularWall(y, x, "FFFe", label="out box top", move="up")
        self.rectangularWall(y, h, "fffe", label="out box wall")
        self.rectangularWall(y, h, "fffe", label="out box wall", move="up left")

        self.rectangularWall(x, h, "fFfF", label="out box wall")

