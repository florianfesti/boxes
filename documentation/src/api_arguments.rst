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

