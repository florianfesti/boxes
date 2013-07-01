#!/usr/bin/python
from boxes import *

class FlexTest(Boxes):


    def render(self, x, y):
        self.moveTo(5, 5)
        self.edge(10)
        self.flex(x, y)
        self.edge(10)
        self.corner(90)
        self.edge(y)
        self.corner(90)
        self.edge(x+20)
        self.corner(90)
        self.edge(y)
        self.corner(90)

        self.ctx.stroke()
        self.surface.flush()

x = 40
y = 100
f = FlexTest(x+30, y+10, thickness=5.0, burn=0.05)
# (1.5, 3.0, 15.0) # line distance, connects, width
f.flexSettings = (2, 4.0, 16.0)
f.render(x, y)

