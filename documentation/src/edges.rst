Edges
=====

As edges started out as methods of the main Boxes class they still are
callables. A set of instances are kept the ``.edges`` attribute of the
``Boxes`` class. It is a dict with strings of length one as keys:

* e : Edge
* E : OutSetEdge
* s : StackableEdge
* S : StackableEdgeTop
* f : FingerJointEdge
* F : FingerJointEdgeCounterPart
* h : FingerHoleEdge
* d : DoveTailJoint
* D : DoveTailJointCounterPart

Edges of the same type share a settings instance to make sure both
sides match (when the same length is given).

Edge base class
---------------

.. autoclass:: boxes.edges.Edge
	       :members:

.. automethod:: boxes.edges.Edge.__call__

Settings Class
--------------

.. autoclass:: boxes.edges.Settings
	       :members:


Straight Edges
--------------

.. autoclass:: boxes.edges.Edge
.. autoclass:: boxes.edges.OutSetEdge

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
	       
