Parts
-----




There are a few parameters shared by many of the parts:

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
calling the one building block function you need (e.g. fingerHolesAt).

For your own parts you can use this helper function:

.. automethod:: boxes.Boxes.cc

For finding the right piece to the *callback* parameter this function is used:

.. automethod:: boxes.Boxes.getEntry


The move parameter
..................

The ``move`` parameter helps when placing multiple parts. It controls the
location where the current and next part will be drawn. It's a string with
space separated words controlling the direction; see the documentation for
``where`` below for possible values.

This kind of direction controls the global placement and is unrelated to the
drawing direction which is important for burn correction (aka kerf).

For implementing parts the following helper function can be used to
implement a ``move`` parameter:

.. automethod:: boxes.Boxes.move

If "only" is given the part is not drawn but only the move is
done. This can be useful to go in one direction after having placed
multiple parts in the other and have returned with ``.ctx.restore()``.

The following example draws three walls: one on the left of the origin and two
on the right. The second draw with "right only" is necessary to prevent
"drawing over" the first wall. The last call needs no move as no more parts
get drawn afterwards.

.. code-block:: python

    self.rectangularWall(x, y, move="left")        # move left and draw
    self.rectangularWall(x, y, move="right only")  # move right
    self.rectangularWall(x, y, move="right")       # draw and move right
    self.rectangularWall(x, y)                     # draw


The edges parameter
...................

The ``edges`` parameter needs to be an iterable of Edge instances to be
used as edges of the part. Instead of instances it is possible to pass
a single character that is looked up in the ``.edges`` dict. This
allows to pass a string with the desired characters per edge. See
:ref:`api_edges` for a list of possible edges and their symbols.

Generators can register their own Edges by putting them into the
``.edges`` dictionary.

Same applies to the parameters of ``.surroundingWall`` although they
denominate single edge (types) only.

PartsMatrix
...........

To place a grid of identical parts, partMatrix can used:

.. automethod:: boxes.Boxes.partsMatrix

It creates one big block of parts. The move param treats this block like one big
part.
