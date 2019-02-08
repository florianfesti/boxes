Edges
=====

Edges are what makes Boxes.py work. They draw a -- more or less -- straight
border to the current piece. They are part of the turtle graphics part
of Boxes.py. This means they start at the current position and current
direction and move the current position to the end of the edge.

Edge instances have a Settings object associated with them that keeps
the details about how the edge should look like. Edges that are
supposed to work together share the same Settings object to ensure
they fit together - assuming they have the same length. Most edges are
symetrical to unsure they fit together even when drawn from different
directions. Although there are a few exception - mainly edges that
provide special features like hinges.

As edges started out as methods of the main Boxes class they still are
callables. It turned out that the edges need to provide a bit more
information to allow the surrounding code to handle them
properly. When drawing an Edge there is a virtual straight line that
is the border the shape of the part (e.g. an rectangle). But the
actual Edge has often to be drawn elsewhere. Best example if probably
the ``F`` Edge that matches the normal finger joints. It has to start
one material thickness outside of the virual border of the part so the
cutouts for the opposing fingers just touch the border. The Edge
classes have a number of methods to deal with these kind of offsets.

A set of instances are kept the ``.edges`` attribute of the
``Boxes`` class. It is a dict with strings of length one as keys:

* d : DoveTailJoint
* D : DoveTailJointCounterPart
* e : Edge
* E : OutSetEdge
* f : FingerJointEdge
* F : FingerJointEdgeCounterPart
* g : GrippingEdge
* h : FingerHoleEdge
* ijk : Hinge (start, end, both sides)
* IJK : HingePin (start, end, both sides)
* s : StackableEdge
* S : StackableEdgeTop

Edge base class
---------------

.. autoclass:: boxes.edges.BaseEdge
	       :members:

.. automethod:: boxes.edges.BaseEdge.__call__

Settings Class
--------------

.. autoclass:: boxes.edges.Settings
	       :members:


Straight Edges
--------------

.. autoclass:: boxes.edges.Edge
.. autoclass:: boxes.edges.OutSetEdge

Grip
----

.. autoclass:: boxes.edges.GripSettings
.. autoclass:: boxes.edges.GrippingEdge

Stackable Edges
---------------

.. autoclass:: boxes.edges.StackableEdge
.. autoclass:: boxes.edges.StackableEdgeTop

Stackable Edge Settings
.......................

.. autoclass:: boxes.edges.StackableSettings
	       :members:

Finger joints
-------------

Finger joints are a simple way of joining two sheets (e.g. of plywood). They
work best at an 90° angle. There are two different sides matching each
other. As a third alternative there are holes that the fingers of one
sheet can plug into. This allows stable T connections especially
useful for inner walls.

.. autoclass:: boxes.edges.FingerJointEdge
.. autoclass:: boxes.edges.FingerJointEdgeCounterPart
.. autoclass:: boxes.edges.FingerHoleEdge
.. autoclass:: boxes.edges.CrossingFingerHoleEdge

In addition there is

.. autoclass:: boxes.edges.FingerHoles

which is no Edge but fits ``FingerJointEdge``.

An instance of is accessible as **Boxes.fingerHolesAt**.

Finger Joint Settings
.....................

.. autoclass:: boxes.edges.FingerJointSettings
	       :members:

Bed Bolts
.........

.. autoclass:: boxes.edges.BoltPolicy

.. autoclass:: boxes.edges.Bolts

Dove Tail Joints
----------------
Dovetails joints can only be used to join two pieces flatly. This
limits their use to closing some round form created with flex areas or
for joining several parts to a bigger one. For this use case they are
much stronger than simple finger joints and can also bare pulling forces.

.. autoclass:: boxes.edges.DoveTailJoint
.. autoclass:: boxes.edges.DoveTailJointCounterPart

Dove Tail Settings
..................

.. autoclass:: boxes.edges.DoveTailSettings
	                      :members:
				 
Flex
----
.. autoclass:: boxes.edges.FlexEdge

Flex Settings
.............

.. autoclass:: boxes.edges.FlexSettings

Slots
-----
.. autoclass:: boxes.edges.Slot
.. autoclass:: boxes.edges.SlottedEdge

CompoundEdge
------------
.. autoclass:: boxes.edges.CompoundEdge
	       
Hinges
------

Hinge Settings
..............

.. autoclass:: boxes.edges.HingeSettings

Hinge
.....

.. autoclass:: boxes.edges.Hinge

HingePin
........

.. autoclass:: boxes.edges.HingePin
