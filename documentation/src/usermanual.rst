==============
Using Boxes.py
==============

.. toctree::
   :maxdepth: 2

Boxes.py is made of a library that is not visible to the user and
multiple generators -- each having its own set of parameters and
creating a drawing for it own type of object. These generators are
divided up into different groups to make it easier to find them:

* Boxes
* Boxes with flex
* Trays and Drawer Inserts
* Shelves
* Parts and Samples
* Misc
* Unstable

The parameters for each generators also come in groups.

Units of meassurement
---------------------

In general all measurements are in Millimeters (mm). There is no
option to change the units of measurement and there is no plan to add
such a option.

A second way to define lengths is as multiple of the material
thickness which is one of the standard parameters described
below. This allows features to retain their proportions even if some
parts depend on the material thickness.

The description texts should state the unit of each argument  -
please open a ticket if the units are missing somewhere.

.. _default-args:

Default arguments
-----------------
In the web interface this is the bottom group right before the
``Render`` button. These are basically all technical settings that
have little to do with the object being rendered but more with the
material used and the way the drawing and the material is processed.

The settings are

thickness
.........

The thickness of the material used. This value is used at many places
to define the sizes of features like finger joints, hinges, ... It is
very important to get the value right - especially if there are
fingers that need to fit into some holes. Be aware that many materials
may differ from their nominal value. You should **always measure the
thickness** for every sheet unless you have a very reliable supply
that is known to stick very closely to specifications. For (ply) wood
even a 100th of a millimeter makes a notable difference in how stiff
the fit is. Harder more brittle materials may be even more picky.

burn
....

The burn correction aka kerf is the distance the laser has to keep
from the edge of the parts. If the laser would cut right on the edge
it would cut away the outside perimeter of the part. So the burn value is
basically the radius of the laser - or half the width of the laser cut.

The value of the burn parameter depends on your laser cutter, the
material cut and the thickness of the material. In addition it depends
on whether you want the parts to be over or under sized. Materials
that are spongy like wood can be cut oversized (larger burn value) so
they can be press fitted with some force and may be assembled without
glue. Brittle materials (like Acrylic) need to be cut undersized to
leave a gap for the glue.

**Note:** The way the burn param works is a bit counter intuitive. Bigger
burn values make a tighter fit. Smaller values make a looser fit.

Small changes in the burn param can make a notable difference. Typical
steps for adjustment are 0.01 or even 0.005mm to choose between
different amounts of force needed to press plywood together.

To find the right burn value cut out a rectangle and then meassure how
much smaller it is than its nominal size. The burn value should be
around half of the difference. To test the fit for several values at
once you can use the **BurnTest** generator in the "Parts and Samples" section.

format
......

Boxes.py is able to create multiple formats. For most of them it
requires ``ps2edit``. Without ``ps2edit`` only ``SVG``
and ``postscript`` (ps) is supported. Otherwise you can also
select

* ai
* dxf
* gcode
* pdf
* plt

Other formats supported by ``ps2edit`` can be added easily. Please
open a ticket on GitHub if you need one.

tabs
....

Tabs are small bridges between the parts and surrounding material that
keep the part from falling out. In theory their width should be
affected by the burn parameter. But it is more practical to have both
independent so you can tune them separately. Most parts and generators
support this features but there may be some that don't.

For plywood values of 0.2 to 0.3mm still allow getting the parts out
by hand (Depending on you laser cutter and the exact material). With
little more you will need a knife to cut them loose. 

debug
.....

Most regular users won't need this option.

It adds some construction lines that are helpful for
developing new generators. Only few pieces actually support the
parameter. The most notable being finger holes that show the border of
the piece they belong to. This helps checking whether the finger holes
are placed correctly.

reference
.........

Converting vector graphics is error prone. Many formats have very
weird ideas how their internal units translates to real world
dimensions. If reference is set to non zero Boxes.py renders a rectangle of
the given length. It can be used to check if the drawing is still at
the right scale or may give clues on how to scale it back to the right
proportions.

Common Parameters and Types
---------------------------

Section parameters
..................

Some generators support an arbitrary number of sections. This can be used for rows or columns of compartments, staggered heights or otherwise dividing some length in multiple sub sections. The standard parameter making use of this are ``sx``, ``sy`` and ``sh`` (instead of ``x``, ``y`` and ``h``).

Most generators will add walls between the comparments, so the total size might be larger depending on the number of compartments (and additional walls).

The sizes of the sections are divided by a colon (``:``) e.g. ``30:25.5:70``. Instead of repeating the same value they can be replaced by ``value*numberofsections``  e.g. ``50*3`` meaning the same as ``50:50:50``. To equally divide a length into several sections ``overallwidth/numberofsections`` can be used - e.g. ``120/4`` being the same as ``30:30:30:30``. All these formats can be freely mixed.


outside
.......

Most messurements are internal sizes. If a generator offers this parameter it will re-calculate the inner sizes to fit walls and outside features within the given dimmensions. This can be a bit surprising for edge types that have protrusions like hinge eyes, handles, feet, etc as those are typically also taken into account. If the dimmensions are not sufficient to accommendate these features the box may not work properly. Most generators do not have checks for such issues (like negative height) and it is left in the responsibility of the user to check if the result still is sane.

For generators offering multiple compartments this will also fit-in the inner walls. It will sum up all sections then subtract the space needed for the walls and then scale all compartments so they will fill the remaining space.


Edge Type parameters
--------------------

All but the simplest edge types have a number of settings controlling
how exactly they should look. Generators are encouraged to offer these
settings to the user. In the web interface they are folded up. In the
command line interface they are grouped together. Users should be
aware that not all settings are practical to change. For now Boxes.py
does not allow hiding some settings.

Finger Joint Settings
.....................

.. glossary::

   finger
      width of the fingers in multiples of the thickness

   space
      width of the spaces between fingers in multiples of the thickness

   surroundingspaces
      minimal amount of space before the first and after the last finger. This is in multiples of regular space between fingers. Reduce this if there are no fingers fitting on short edges.

   style
      how finger joints should look like. There may be more styles to choose from in the future.

   extra_length
      Make the outset part of the finger joint longer to allow grinding off burn marks. Note that this may not be great for non 90° joints where the corner is butted against the opposing cutout.

Stackable Edge Settings
.......................

For boxes to actually stack they need to be the same width and depth and ``angle``, ``width`` and ``height`` of the feet need to be the same.

.. glossary::

   angle
      inside angle of the feet.

   height
      height of the feet

   holedistance
      distance from finger holes to bottom edge. May be reduced to save height by sacrificing stability of the connection to the bottom of the box.

   width
      width of the feet

Colors
------
The generated files uses the following color conventions:

.. glossary::

     Black 
        The outer edges of a part

     Blue
        Inner edges of a part

     Red
        Comments or help lines that are not ment to be cut or etched

     Green
        Etchings

Normaly you will cut things in the order: Green, Blue, Black. If other 
colors are present, the meaning should hopefully be obvious.
