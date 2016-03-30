
		 

==========================
The boxes.Boxes main class
==========================

.. toctree::
      :maxdepth: 2
		 
.. autoclass:: boxes.Boxes


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

.. automethod:: boxes.Boxes.cc
.. automethod:: boxes.Boxes.getEntry

The move parameter
..................

.. automethod:: boxes.Boxes.move

The edges parameter
...................
