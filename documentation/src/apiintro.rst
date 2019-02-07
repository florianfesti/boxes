==========================
Using the Boxes.py library
==========================

If there is no generator fitting your needs you can either adjust an
existing one (may be by copying it to another name first) or writing a
new one from scratch.

Generators are found in ``boxes/generators/``. They are included into
the web UI and the CLI tool by the name of their class. So whenever
you copy either an existing generator or the sceleton in
``boxes/generators/_template.py`` you need to change the name of the
main class first.

Generator Arguments
-------------------

Boxes.py uses the ``argparse`` standard library for handling the
arguments for the generators. It is used directly for the ``boxes``
command line tool. But it also handles -- with some additional code --
the web interface and the Inkscape extensions. To make this work one
has to limit the kind of parameters used. Boxes.py supports the
following types:

 * ``int``
 * ``float``
 * ``str``
 * ``boxes.boolarg`` -- an alternative to ``bool`` that works with the
   web interface
 * ``boxes.argparseSections`` -- multiple lengths e.g. for dividing up
   a box in one direction

and

.. autoclass:: boxes.ArgparseEdgeType

For the standard types there is code to create HTML and Inkscape
extensions. The other types can have ``.html()`` and ``.inx()``
methods.

The argument parser need to be built in the ``.__init__()`` method
after calling the method of the super class. Have a look at

.. automethod:: boxes.generators._template.BOX.__init__

As many arguments are used over and over there is a function that can
add the most common ones:

.. automethod:: boxes.Boxes.buildArgParser

Check the source for details about the single arguments.

Other arguments can be added with the normal argparser API - namely

.. automethod:: argparse.ArgumentParser.add_argument

of the ``Boxes.argparser`` attribute.

Edge style arguments
....................

Edges that work together share a Settings class (and object). These
classes can create ``argparse`` groups:

.. automethod:: boxes.edges.Settings.parserArguments

See

.. automethod:: boxes.generators._template.BOX.__init__

for a list of possible edge settings. These regular settings are used
in the standard edge instances used everywhere. For special edge
instances you can call them with a ``prefix`` parameter. But you then
need to deal with the results on your own.

Default Arguments
.................

The :ref:`default-args` get added automatically by the super class's
constructor.

Accessing the Arguments
.......................

For convenience content of the arguments are written to attributes of
the Boxes instance before ``.render()`` is called. This is done by
``Boxes.parseArgs``. But most people won't need to care as this is
handled by the frame work.  Be careful to **not overwrite important
methods or attributes by using conflicting argument names**.

API Levels
----------

For actual drawing there are multiple levels of abscractions thta can
be used. From the simplest to the more powerful they are the following:

Simple drawing commands
.......................

These are simple drawing commands. Some of them get ``x``, ``y`` and
``angle`` parameters to draw somewhere specific. Some just draw right
at the current coordinate origin. Often these commands create holes or
hole patterns.

Moving the coordinate system
............................

Boxes.py moves the coordinate system around a lot. You basically never have to
deal with the global position on the sheet but only with coordnates
relative to where you are. There are a few functions to move the
origin to a convenient position.

Turtle graphics
...............

To draw parts turtle graphic commands are used. The always start at
the current origin following the X axis. The move the origin with
them. The inside of the part is above the X axis and the outside
below. Corners with an positive angle (going counter clockwise) close
the part while negative angles (going clockwise) create protrusions.
This is inversed for holes which need to be drawn clockwise.

Getting this directions right is important to make the burn correction
(aka kerf) work properly. The burn correction is implemented by
increasing the radius of positive corners and decresing the radius of
negative corners. (TODO: nice pictures)

Edges
.....

Edges are also turtle graphic commands. But they have been elevated to
proper Classes. 

Parts
.....

There are a couple of standard parts that can be drawn with a single
command. Their typical params are explained in the API docs.


Part Callbacks
..............

Most parts support callbacks - either one in the middle for round
parts or one for each edge. They allow placing holes or other features
on the part.


How to get things done
----------------------

Decide whether you want to start from scratch or want to rework an
existing generator.

You should go over the arguments first. Get at least the most basic
arguments done. For things you are still unsure you can just use a
attribute set in the .__init__() method and turn it into a proper
argument later on.

Depending on what you want to do you can work on the different levels
of the API. You can either use what is there and combine it into
something new or you can implements new things in the appropriate level.

Here are some examples:

Housing for some electronics
............................

You can use the ElectronicsBox or the ClosedBox as a basis. Write some
callbacks to place holes in the walls to allow accessing the ports of
the electronics boards. Place some holes to screw spacers into the
bottom to mount the PBC on.

NemaMount
.........

This is a good non box example to look at.

.. autoclass:: boxes.generators.nemamount.NemaMount

Note that although it produces a cube like object it uses separate
variables (``x``, ``y``, ``h``) for the different axis. Probably
because it started as a copy of another generator like ``ClosedBox``.

DisplayShelf
............

.. autoclass:: boxes.generators.displayshelf.DisplayShelf

The DisplayShelf is completely made out of rectangularWalls(). It uses
a callback to place all the fingerHolesAt() right places on the sides.
While the use of the Boxes.py API is pretty straight forward the
calculations needed are a bit more tricky. You can use the ``debug``
default param to check if you got things right when attempting
something like this yourself.

Note that the front walls and the shelfs form a 90° angle so they work
with the default FingerJoints.

BinTray
.......

.. autoclass:: boxes.generators.bintray.BinTray

The BinTray is based on the TypeTray generator:

.. autoclass:: boxes.generators.typetray.TypeTray

TypeTray is an already pretty complicated generator.

BinTray replaces the now vertical front (former top) edges with a
special purpose one that does add the triangles:

.. autoclass:: boxes.generators.bintray.BinFrontEdge

The ``hi`` (height of inner walls) argument was removed although the
variable is still used internally - out of lazyness.

To complete the bin the front walls are added. Follow up patches then
switched the slots between the vertical and horizontal walls to have
better support for the now bottoms of the bins. Another patch adds
angled finger joints for connecting the front walls with the bottoms
of the bins.

The TrafficLight generator uses a similar technique implementing its
own Edge class. But it uses its own code to generate all the wall needed.

Stachel
.......

.. autoclass:: boxes.generators.stachel.Stachel

Stachel allows mounting a monopod to a bass recorder. It is basically
just one part repeated with different parameters. It can't really make
use of much of the Boxes.py library. It implements this one part
including the ``move`` parameter and draws everything using the
``.polyline()`` method. This is pretty painful as lots of angles and
distances need to be calculated by hand.

For symmetric sections it passes the parameters to ``.polyline`` twice
-- first in normal order and then reversed to get the mirrored section.

This generator is beyond what Boxes.py is designed for. If you need
something similar you may want to use another tool like OpenScad or a
traditional CAD program.
