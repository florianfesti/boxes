Navigation
----------

The back end can both move the origin and the current point from
which the next line is going to start. Boxes.py hides this by using
Turtle Graphics commands that also move the origin to the end of the
last line. Other drawing commands restore the current position after
they are finished.

Moving the origin like this allows ignoring the absolute coordinates
and do all movement and drawing to be relative to the current
position. The current positions does not only consist of a point on
the drawing canvas but also a direction.

To move the origin to a different location there are these to methods:

.. automethod:: boxes.Boxes.moveTo
.. automethod:: boxes.Boxes.moveArc

Often it is necessary to return to a position e.g. after placing a
row of parts. This can be done with the following context manager:

.. automethod:: boxes.Boxes.saved_context()

It can be used with the following code pattern:

.. code-block:: python

   with self.saved_context():
       self.rectangularWall(x, h, move="right")
       self.rectangularWall(y, h, move="right")
       self.rectangularWall(y, h, move="right")
       self.rectangularWall(x, h, move="right")
   self.rectangularWall(x, h, move="up only")

   # continue above the row

Parts of the code still directly use the back end primitives **Boxes.ctx.save()**
and **Boxes.ctx.restore()**. But this has several disadvantages and is
discouraged. For one it requires matchiung calls. It also does not
reset the starting point of the next line. This is "healed" by a
follow up **.moveTo()**. Use **.moveTo(0, 0)** if in doubt.
