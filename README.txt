What is this?
=============

This is a small python library for generating SVG drawings used for
cutting out boxes or other structures from plywood using a laser cutter.

While there are a couple of other box generators they are all very
limited in what they can do. This library aims for supporting
complicated shapes while offering easy way to do simple things. To
achieve this there are several levels of abstactions. 

Basic Concepts
==============

There is basically only one class that takes care of everything. You
are supposed to sub class it and implement the render() method
(actually just any method that does anything). This Boxes class keeps
a cairo canvas object (self.ctx) that all drawing is made on. In
addition it keeps a couple of global settings used for various drawing
operations. See the __init__ method for the details.

Building blocks and coordinates
-------------------------------

To avoid too much coordinate calculations the coordinate system is
continuously moved to the current point. The most basic functions just
do drawings relative to the current coordinate system - withou
changing the coordinate system. Those are found in the Builing block section.

Turtle graphics commands
------------------------

These start at the current positions and move the coordinate system to
their end. It is assumed that you are always drawing into the
direction of the x axis, with the inside of the part being above the
line. You need to turn counter clockwise (mathematically positive) to
get a closed shape. These are typically some sort of edges.

Finger joints
.............

Finger joints are a smple way of joining two sheets of plywood. They
wor best at an 90° angle. There are two different sides matching each
other. As a third alternative there are holes that the fingers of one
sheet can plug into. This allows stable T connections especially
useful for inner walls.

Dovetail joints
...............

Dovetails joints can only be used to join two pieces flatly. This
limits their use to closing some round form created with flex areas or
for joining several parts to a bigger one. For this use case they are
much stronger than simple finger joints and can also bare pulling forces.


Whole parts
===========

A couple of command can create whole parts like walls. Typically the
sizes given are the inner dimmensions not including additional space
needed for burn compensation or joints.


Callback parameter
..................

The callback parameter can take on of the following forms:

 * A function (or bound method) that expects one parameter: the number
   of the side the callback is currently called for. 
 * A dict with some of the numbers of the sides as keys and functions
   without parameters as values.
 * A list of functions without parameters. The list may contain None
   as place holder and be shorter than the number of sides. 

The callback functions are called with the side of the part at the
positive x and y axis. If the edge uses up space this space is below
the x axis. You do not have to restore the coordinate settings in the
callback.

Instead of functions it can be handy to use a lambda expression
calling the one building block funtion you need (e.g. fingerHolesAt).

Edge description
................

Some part building functions take a edges param or have other params
describing some edges. These descriptions are one or several character
strings. With the following meanings: 

 e : straight edge
 E : as above but extended outside by one thickness
 f, F : finger joints
 h : edge with holes for finger joints
 d, D : dove tail joints
