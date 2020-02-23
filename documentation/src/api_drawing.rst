Drawing commands
================


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

Tab support
...........

Tabs are small interuptions in the border of a part to keep it in
place. They are enabled with the **tabs** parameter. All
**Edges** automatically create about two tabs. So parts like
:py:meth:`boxes.Boxes.rectangularWall` will have 8 tabs holding them
in place. Because of this developers often don't need to be concerned
about tabs. But some part may be completely drawn by low level Turtle
Graphics commands. For those both :py:meth:`boxes.Boxes.edge` and
:py:meth:`boxes.Boxes.corner` do support a **tabs** parameter. In
addition the length of the line segments in :py:meth:`boxes.Boxes.polyline` can
be given as a tuple **(length, tabs)**.

Draw Commands
-------------

These commands do not change the coordinate system but get the
coordinates passed as parameters. All of them are either som sort of
hole or text. These artifacts are placed somewhere independently of
some continuous outline of the part their on.

.. automethod:: boxes.Boxes.hole
.. automethod:: boxes.Boxes.rectangularHole
.. automethod:: boxes.Boxes.dHole
.. automethod:: boxes.Boxes.flatHole
.. automethod:: boxes.Boxes.text
.. automethod:: boxes.Boxes.NEMA
.. automethod:: boxes.Boxes.TX
.. automethod:: boxes.Boxes.flex2D
.. py:class:: NutHole

An instance is available as **boxes.Boxes.nutHole()**

An instance of

.. autoclass:: boxes.edges.FingerHoles
	       :noindex:

is accessible as **Boxes.fingerHolesAt**.


Hexagonal Hole patterns
.......................

Hexagonal hole patterns are one way to have some ventilation for
housings made with Boxes.py. Right now both ``.rectangularWall()``
and ``.roundedPlate()`` do supports this pattern directly by passing
the parameters to the calls. For other use cases these more low level
methods can be used.

For now this is the only supported pattern for ventilation slots. More
may be added in the future.

There is a global Boxes.hexHolesSettings object that is used if no settings are
passed. It currently is just a tuple of (r, dist, style) defaulting to
(5, 3, 'circle') but might be replace by a Settings instance in the future.

.. automethod:: boxes.Boxes.hexHolesRectangle
.. automethod:: boxes.Boxes.hexHolesCircle
.. automethod:: boxes.Boxes.hexHolesPlate
.. automethod:: boxes.Boxes.hexHolesHex
