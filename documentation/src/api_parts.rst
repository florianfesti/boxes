Parts
-----




There are a few parameter shared by many of those parts:

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
the proper ``before`` parameter set.

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

PartsMatrix
...........

To place many of the same part partMatrix can used:

.. automethod:: boxes.Boxes.partsMatrix

It creates one big block of parts. The move param treat this block like on big
part.
