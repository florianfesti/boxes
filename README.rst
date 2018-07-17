Boxes.py
========

Create boxes and more with a laser cutter!

Boxes.py is python library for generating drawings to be used with a laser
cutter. It comes with a growing set of ready-to-use, fully parametrized
generators:

* Boxes in various shapes and with various lids
* Boxes using flex cuts with rounded corners and living hinges
* Type trays with and without outer walls and floors
* Shelves
* Book covers with flex spine
* Magazine files
* Timing belt pulleys and gears
* and more

And a few one trick ponies:

* A desktop arcade cabinet
* A drill stand
* A castle tower
* A cutlery stand

Have a look into the  examples/  directory <https://github.com/florianfesti/boxes/tree/master/examples/>or the online generator <https://www.festi.info/boxes.py/index.html> to see how the results look like.

Features
--------

It generates SVG images that can be viewed directly in a web brower but also
postscript and - with pstoedit as external helper - other vector formats
including dxf, plt (aka hpgl) and gcode.

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
although this is currently not supported for the included generators.

Dovetail joints can be used to join pieces in the same plane.

Flex cuts allows bending and stretching the material in one direction. This
is used for rounded edges and living hinges.

Usage
-----

There are multiple ways to use the available generators:

* Try them out at <https://www.festi.info/boxes.py/index.html>
* Use them as Inkscape extensions under *Extensions->Boxes.py*
* Execute the scripts/boxes tool and pass the name of the generator together with the measurements on the command line.
* Run *scripts/boxesserver* which provides an web interface on port 8000.
* Add a *WSGIScriptAlias* to *scripts/boxesserver* in your httpd config.

You can also create your own generators using *boxes/generators/_template.py* or any of the generators in *boxes/generators* as a starting point.

Documentation
-------------

The module comes with Sphinx based documentation. The rendered version can be
viewed at <https://florianfesti.github.io/boxes/html/index.html>.
