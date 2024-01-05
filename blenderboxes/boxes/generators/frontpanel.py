# Copyright (C) 2013-2017 Florian Festi
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

from boxes import *
import io
import shlex

def str_to_bool(s):
    if (s.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']):
        return True
    else:
        return False

class FrontPanel(Boxes):
    """Mounting Holes and cutouts for all your holy needs."""

    description = f"""
<script type="module" src="https://md-block.verou.me/md-block.js"></script>
<md-block>


This will help you create font (and side and top) panels for your
boxes that are pre-configured for all the bits and bobs you'd like to
install

    The layout can create several types of holes including rectangles,
    circles and mounting holes.  The default shows an example layout with all
    currently supported objects.

#### 
`rect x y w h [cr=0] [cx=True] [cy=True]`

     x: x position
     y: y position
     w: width
     h: height
    cr: optional, Corner radius, default=0
    cx: optional, Center x.  the x position denotes the center of the rectangle.
        accepts t, T, 1, or other true-like values.
    cy: optional, Center y.  the y position denotes the center of the rectangle.

#### outline
`rect w h`

    w: width
    h: height

`outline` has a special meaning: You can create multiple panel outlines with one command.  
This has the effect of making it easy to manage all the holes on all the sides of
your boxes.

#### circle
`circle x y r`

    x: x position
    y: y position
    r: radius

#### mountinghole
mountinghole x y d_shaft [d_head=0] [angle=0]

          x: x position
          y: y position
    d_shaft: diameter of the shaft part of the mounting hole
     d_head: optional. diameter of the head
      angle: optional. angle of the mounting hole

#### text
`text x y size "some text" [angle=0] [align=bottom|left]`

        x: x position
        y: y position
     size: size, in mm
     text: text to render.  This *must* be in quotation marks
    angle: angle (in degrees)
    align: string with combinations of (top|middle|bottom) and (left|center|right),
           separated by '|'.  Default is 'bottom|left'



#### nema
`nema x y size [screwhole_size=0]`

        x: x position (center of shaft)
        y: y position (center of shaft)
     size: nema size.  One of [{', '.join([f'{x}' for x in Boxes.nema_sizes])}]
    screw: screw size, in mm.  Optional.  Default=0, which means the default size
</md-block>
    """

    ui_group = "Holes"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.argparser.add_argument(
            "--layout", action="store", type=str,
            default="""
outline 100 100
rect 50 60 80 30 3 True False
text 50 91 7 "Super Front Panel With Buttons!" 0 bottom|center
circle 10 45 3.5
circle 30 45 3.5
circle 50 45 3.5
circle 70 45 3.5
circle 90 45 3.5
text 10 40 3 "BTN_1" 0 top|center
text 35 45 3 "BTN_2" 90 top|center
text 50 50 3 "BTN_3" 180 top|center
text 65 45 3 "BTN_4" 270 top|center
text 90 45 3 "5" 0 middle|center
mountinghole 5 85 3 6 90
mountinghole 95 85 3 6 90

# Start another panel, 30x50
outline 30 50
rect 15 25 15 15 1 True True
text 15 25 3 "__Fun!"   0 bottom|left
text 15 25 3 "__Fun!"  45 bottom|left
text 15 25 3 "__Fun!"  90 bottom|left
text 15 25 3 "__Fun!" 135 bottom|left
text 15 25 3 "__Fun!" 180 bottom|left
text 15 25 3 "__Fun!" 225 bottom|left
text 15 25 3 "__Fun!" 270 bottom|left

text 3  10 2 "Another panel, for fun" 0 top|left


# Let's create another panel with a nema motor on it
outline 40 40
nema 20 20 17
""")

    def applyOffset(self, x, y):
        return (x+self.offset[0], y+self.offset[1])
    
    def drawRect(self, x, y, w, h, r=0, center_x="True", center_y="True"):
        x, y, w, h, r = (float(i) for i in [x, y, w, h, r])
        x, y = self.applyOffset(x, y)
        center_x = str_to_bool(center_x)
        center_y = str_to_bool(center_y)
        self.rectangularHole(x, y, w, h, r, center_x, center_y)
        return

    def drawCircle(self, x, y, r):
        x, y, r = (float(i) for i in [x, y, r])
        x, y = self.applyOffset(x, y)
        self.hole(x, y, r)
        return

    def drawMountingHole(self, x, y, d_shaft, d_head=0.0, angle=0):
        x, y, d_shaft, d_head, angle = (float(i) for i in [x, y, d_shaft, d_head, angle])
        x, y = self.applyOffset(x, y)
        self.mountingHole(x, y, d_shaft, d_head, angle)
        return

    def drawOutline(self, w, h):
        w, h = (float(i) for i in [w, h])
        if self.outline is not None:
            self.offset = self.applyOffset(self.outline[0]+10, 0)
        self.outline = (w, h) # store away for next time
        x = 0
        y = 0
        x, y = self.applyOffset(x, y)
        border = [(x, y), (x+w, y), (x+w, y+h), (x, y+h), (x, y)]
        self.showBorderPoly( border )
        return

    def drawText(self, x, y, size, text, angle=0, align='bottom|left'):
        x, y, size, angle = (float(i) for i in [x, y, size, angle])
        x, y = self.applyOffset(x, y)
        align = align.replace("|", " ")
        self.text(text=text, x=x, y=y, fontsize=size, angle=angle, align=align)
        
    def drawNema(self, x, y, size, screwhole_size=0):
        x, y, size, screwhole_size = (float(i) for i in [x, y, size, screwhole_size])
        if size in self.nema_sizes:
            x, y = self.applyOffset(x, y)
            self.NEMA(size, x, y, screwholes=screwhole_size)
        
    def parse_layout(self, layout):
        f = io.StringIO(layout)
        line = 0
        objects = {
            'outline': self.drawOutline,
            'rect': self.drawRect,
            'circle': self.drawCircle,
            'mountinghole': self.drawMountingHole,
            'text': self.drawText,
            'nema': self.drawNema,
        }

        for l in f.readlines():
            line += 1
            l = re.sub('#.*$', '', l) # remove comments
            l = l.strip()
            la = shlex.split(l, comments=True, posix=True)
            if len(la) > 0 and la[0].lower() in objects:
                objects[la[0]](*la[1:])
        return

    def render(self):
        self.offset = (0.0, 0.0)
        self.outline = None # No outline yet
        self.parse_layout(self.layout)
