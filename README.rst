What is this?
=============

This is a small python library for generating SVG drawings used for
cutting out boxes or other structures using a laser cutter.

It also comes with a set of ready-to-use, fully parametrized generators:

* Various simple boxes
* Flex boxes with rounded corners and living hinges
* Type trays with and without walls and floors
* Book cover with flex spine
* Magazine file

And a few one trick ponies:

* A drill stand
* A castle tower
* A housing for a special kind of lamp
* A cutlery stand

Have a look into the examples/ directory to see how the results look like.

Features
========

Of course the library and the generators allow selecting the "thickness"
of the material used and automatically adjusts lengths and width of
joining fingers and other elements.

The "burn" parameter compensates for the material removed by the laser. This
allows fine tuning the gaps between joins up to the point where plywood
can be press fitted even without any glue.

Finger Joints are the work horse of the library. They allow 90° edges
and T connections. Their size is scaled up with the material
"thickness" to maintain the same appearance. The libray also allows
putting holes and slots for screws (bed bolts) into finger joints,
although this is currently not supported for the finished generators.

Dovetail joints can be used to join pieces in the same plane.

Flex allows bending and streching the material in one direction. This
is used for rounded edges and living hinges.

Usage
=====

There are two ways to use the available generators:

* Execute the scripts/boxes tool and pass the name of the generator together with the measurements on the command line
* Run scripts/boxesserver which provides an web interface on port 8000
