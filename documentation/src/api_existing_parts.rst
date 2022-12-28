Existing Parts
--------------

A couple of commands can create whole parts like walls. Typically the
sizes given are the inner dimension not including additional space
needed for burn compensation or joints.

Currently there are the following parts:

.. automethod:: boxes.Boxes.rectangularWall
.. automethod:: boxes.Boxes.flangedWall
.. automethod:: boxes.Boxes.rectangularTriangle
.. automethod:: boxes.Boxes.regularPolygonWall
.. automethod:: boxes.Boxes.polygonWall
.. automethod:: boxes.Boxes.roundedPlate
.. automethod:: boxes.Boxes.surroundingWall

Parts Class
...........

More parts are available in a separate class. An instance is available as
**Boxes.parts**

.. automethod:: boxes.parts.Parts.disc
.. automethod:: boxes.parts.Parts.waivyKnob
.. automethod:: boxes.parts.Parts.concaveKnob
.. automethod:: boxes.parts.Parts.ringSegment
