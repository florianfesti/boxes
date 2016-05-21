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
"thickness" to maintain the same appearance. The library also allows
putting holes and slots for screws (bed bolts) into finger joints,
although this is currently not supported for the finished generators.

Dovetail joints can be used to join pieces in the same plane.

Flex allows bending and stretching the material in one direction. This
is used for rounded edges and living hinges.

Usage
=====

There are multiple ways to use the available generators:

* Try them out `<http://www.festi.info/boxes.py/index.html>online`_
* Execute the scripts/boxes tool and pass the name of the generator together with the measurements on the command line.
* Run *scripts/boxesserver* which provides an web interface on port 8000.
* Add a *WSGIScriptAlias* to *scripts/boxesserver* in your httpd config.

You can also create your own generators using `<https://github.com/florianfesti/boxes/blob/master/boxes/generators/_template.py>boxes/generators/_template.py`_ or any of the `<https://github.com/florianfesti/boxes/blob/master/boxes/generators>generators`_ as a starting point.

Documentation
=============

The module comes with Sphinx based documentation. The rendered version can be
viewed `<http://florianfesti.github.io/boxes/html/index.html>here`_.
