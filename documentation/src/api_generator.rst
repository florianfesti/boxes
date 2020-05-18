
Generators
==========

Generators are sub classes of 

.. autoclass:: boxes.Boxes

Most code is directly in this class. Sub class are supposed to over
write the ``.__init__()`` and ``.render()`` method.

The Boxes class keeps a canvas object (self.ctx) that all
drawing is made on. In addition it keeps a couple of global settings
used for various drawing operations. See the ``.__init__()`` method
for the details. 

For implementing a new generator forking an existing one or using the
``boxes/generators/_template.py`` is probably easier than starting
from scratch.

Many methods and attributes are for use of the sub classes. These
methods are the interface for the user interfaces to interact with the
generators:

.. automethod:: boxes.Boxes.__init__
		
.. automethod:: boxes.Boxes.parseArgs
.. automethod:: boxes.Boxes.render

.. automethod:: boxes.Boxes.open
.. automethod:: boxes.Boxes.close

Handling Generators
-------------------
		
To handle the generators there is code in the ``boxes.generators``
package.

.. automodule:: boxes.generators
   :members:
   :undoc-members:

This adds generators to the user interfaces automatically. For this to
work it is important that the class names are unique. So whenever you
start a new generator please change the class name right away.
