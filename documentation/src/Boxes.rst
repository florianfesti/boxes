
==========================
The boxes.Boxes main class
==========================

.. toctree::
      :maxdepth: 2
		 
There is basically one class that takes care of everything. You are
supposed to sub class it and implement the ``.__init__()`` and
``.render()`` method. This Boxes class keeps a cairo canvas object
(self.ctx) that all drawing is made on. In addition it keeps a couple
of global settings used for various drawing operations. See the
``.__init__()`` method for the details.

.. autoclass:: boxes.Boxes

And easier way to get started is using the
``boxes/generators/_template.py`` as a basis for your own generators.

Basic operation
---------------
.. automethod:: boxes.Boxes.__init__
		
.. automethod:: boxes.Boxes.parseArgs
.. automethod:: boxes.Boxes.render

.. automethod:: boxes.Boxes.open
.. automethod:: boxes.Boxes.close


Generating Parts
----------------

A couple of commands can create whole parts like walls. Typically the
sizes given are the inner dimmensions not including additional space
needed for burn compensation or joints.

Currently there are only three such parts:

.. automethod:: boxes.Boxes.rectangularWall
.. automethod:: boxes.Boxes.roundedPlate
.. automethod:: boxes.Boxes.surroundingWall

The callback parameter
......................

The callback parameter can take on of the following forms:

* A function (or bound method) that expects one parameter: the number of the side the callback is currently called for.
* A dict with some of the numbers of the sides as keys and functions without parameters as values.
* A list of functions without parameters. The list may contain None as place holder and be shorter than the number of sides. 

The callback functions are called with the side of the part at the
positive x and y axis. If the edge uses up space this space is below
the x axis. You do not have to restore the coordinate settings in the
callback.

Instead of functions it can be handy to use a lambda expression
calling the one building block funtion you need (e.g. fingerHolesAt).

For your own parts you can use this helper function:

.. automethod:: boxes.Boxes.cc

For finding the right piece to the *callback* parameter this function is used:

.. automethod:: boxes.Boxes.getEntry

		
The move parameter
..................

For placing the parts the ``move`` parameter can be used. It is string
with space separated words - at most one of each of those options: 

* left / right
* up / down
* only

If "only" is given the part is not drawn but only the move is
done. This can be useful to go in one direction after having placed
multiple parts in the other and have returned with ``.ctx.restore()``.

For implementing parts the following helper function can be used to
implement a ``move`` parameter:

.. automethod:: boxes.Boxes.move

It needs to be called before and after drawing the actual part with
the proper ``before`` paramter set.
		
The edges parameter
...................

The ``edges`` parameter needs to be an iterable of Edge instances to be
used as edges of the part. Instead of instances it is possible to pass
a single character that is looked up in the ``.edges`` dict. This
allows to pass a string with the desired characters per edge. By
default the following character are supported:

* e : straight edge
* E : as above but extended outside by one thickness
* f, F : finger joints
* h : edge with holes for finger joints
* d, D : dove tail joints

Generators can register their own Edges by putting them into the
``.edges`` dictionary.

Same applies to the parameters of ``.surroundingWall`` although they
denominate single edge (types) only.
  
Navigation
----------
.. automethod:: boxes.Boxes.moveTo
.. automethod:: boxes.Boxes.continueDirection

Boxes.ctx.save()
Boxes.ctx.restore()

Turtle Graphics commands
------------------------

These commands all move the coordinate system with them.

.. automethod:: boxes.Boxes.edge
.. automethod:: boxes.Boxes.corner
.. automethod:: boxes.Boxes.curveTo
.. automethod:: boxes.Boxes.polyline

Special Functions
.................

.. automethod:: boxes.Boxes.bedBoltHole

Latch and Grip
..............

These should probably be Edge classes. But right now they are still functions.

.. automethod:: boxes.Boxes.grip
.. automethod:: boxes.Boxes.latch
.. automethod:: boxes.Boxes.handle

Draw Commands
-------------

These commands do not change the coordinate system but get the
coordinates passed as parameters. All of them are either som sort of
hole or text. These artefacts are placed somewhere independently of
some continuous outline of the part their on.

.. automethod:: boxes.Boxes.hole
.. automethod:: boxes.Boxes.rectangularHole
.. automethod:: boxes.Boxes.text
.. automethod:: boxes.Boxes.NEMA

An instance of

.. autoclass:: boxes.edges.FingerHoles
	       :noindex:

is accessible as **Boxes.fingerHolesAt**.


Hexagonal Hole patterns
.......................

Hexagonal hole patterns are one way to have some ventilation for
housings maded with Boxes.py. Right now both ``.rectangularWall()``
and ``.roundedPlate()`` do supports this pattern directly by passing
the parameters to the calls. For other use cases these more low level
methods can be used.

For now this is the only supported pattern for ventilation slots. More
may be added in the future.

.. automethod:: boxes.Boxes.hexHolesRectangle
.. automethod:: boxes.Boxes.hexHolesCircle
.. automethod:: boxes.Boxes.hexHolesPlate
.. automethod:: boxes.Boxes.hexHolesHex
