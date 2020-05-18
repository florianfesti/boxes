Architecture
------------

Boxes.py it structured into several distinct tiers.

User Interfaces
...............

User interfaces allow users to render the different generators. They
handle the parameters of Generators and convert them to a readable
form. The user interfaces are located in `scripts/`. Currently there is

* scripts/boxes -- the command line interface
* scripts/boxesserver -- the web interface
* scripts/boxes2inx -- generates Inkscape extensions
* scripts/boxes_example.ipynb -- Jupyter notebook


Generators
..........

A (box) generator is an sub class of boxes.Boxes. It generates one
drawing. The sub classes over load .__init__() to set their parameters
and implement .render() that does the actual drawing.

Generators are found in ``boxes/generators/``. They are included into
the web UI and the CLI tool by the name of their class. So whenever
you copy either an existing generator or the sceleton in
``boxes/generators/_template.py`` you need to change the name of the
main class first.

Parts
.....

Parts are a single call that draws something according to a set of parameters.
There is a number of standard parts. Their typical params are
explained in the API docs.

Only real requirement for a part it supporting the move parameter for
placement.

Part Callbacks
++++++++++++++

Most parts support callbacks - either one in the middle for round
parts or one for each edge. They allow placing holes or other features
on the part.

Navigation and Turtle Graphics
..............................

Many drawing commands in Boxes.py are Turtle Graphics commands. They
start at the current position and in the current direction and move
the coordinate system with them. This way the absolute coordinates are
never used and placement and movement is always relative to the
current position.

There are a few functions to move the origin to a convenient position
or to return to a previously saved position.

Edges
.....

Edges are turtle graphic commands. But they have been elevated to
proper Classes to handle outsets. They can be passed as parameters to parts.
There is a set of standard edges found in ``.edges``. They are
associated with a single char which can be used instead of the
Edge object itself at most places. This allows passing the edge
description of a part as a string.

Turtle graphics
...............

There are a few turtle graphics commands that do the actual
drawing. Corners with an positive angle (going counter clockwise)
close the part while negative angles (going clockwise) create protrusions.
This is inversed for holes which need to be drawn clockwise.

Getting this directions right is important to make the burn correction
(aka kerf) work properly.

Simple drawing commands
.......................

These also are simple drawing commands. Some of them get ``x``, ``y`` and
``angle`` parameters to draw somewhere specific. Some just draw right
at the current coordinate origin. Often these commands create holes or
hole patterns.

Back end
........

Boxes.py used to use cairo as graphics library. It now uses its own -
pure Python - back end. It is not fully encapsulated
within the drawing methods of the Boxes class. Although this is the
long term goal. Boxes.ctx is the context all drawing is made on.
