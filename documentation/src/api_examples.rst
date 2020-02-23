Examples
--------

Decide whether you want to start from scratch or want to rework an
existing generator.

You should go over the arguments first. Get at least the most basic
arguments done. For things you are still unsure you can just use a
attribute set in the .__init__() method and turn it into a proper
argument later on.

Depending on what you want to do you can work on the different levels
of the API. You can either use what is there and combine it into
something new or you can implements new things in the appropriate level.

Here are some examples:

Housing for some electronics
............................

You can use the ElectronicsBox or the ClosedBox as a basis. Write some
callbacks to place holes in the walls to allow accessing the ports of
the electronics boards. Place some holes to screw spacers into the
bottom to mount the PBC on.

NemaMount
.........

This is a good non box example to look at.

.. autoclass:: boxes.generators.nemamount.NemaMount

Note that although it produces a cube like object it uses separate
variables (``x``, ``y``, ``h``) for the different axis. Probably
because it started as a copy of another generator like ``ClosedBox``.

DisplayShelf
............

.. autoclass:: boxes.generators.displayshelf.DisplayShelf

The DisplayShelf is completely made out of rectangularWalls(). It uses
a callback to place all the fingerHolesAt() right places on the sides.
While the use of the Boxes.py API is pretty straight forward the
calculations needed are a bit more tricky. You can use the ``debug``
default param to check if you got things right when attempting
something like this yourself.

Note that the front walls and the shelfs form a 90° angle so they work
with the default FingerJoints.

BinTray
.......

.. autoclass:: boxes.generators.bintray.BinTray

The BinTray is based on the TypeTray generator:

.. autoclass:: boxes.generators.typetray.TypeTray

TypeTray is an already pretty complicated generator.

BinTray replaces the now vertical front (former top) edges with a
special purpose one that does add the triangles:

.. autoclass:: boxes.generators.bintray.BinFrontEdge

The ``hi`` (height of inner walls) argument was removed although the
variable is still used internally - out of laziness.

To complete the bin the front walls are added. Follow up patches then
switched the slots between the vertical and horizontal walls to have
better support for the now bottoms of the bins. Another patch adds
angled finger joints for connecting the front walls with the bottoms
of the bins.

The TrafficLight generator uses a similar technique implementing its
own Edge class. But it uses its own code to generate all the wall needed.

Stachel
.......

.. autoclass:: boxes.generators.stachel.Stachel

Stachel allows mounting a monopod to a bass recorder. It is basically
just one part repeated with different parameters. It can't really make
use of much of the Boxes.py library. It implements this one part
including the ``move`` parameter and draws everything using the
``.polyline()`` method. This is pretty painful as lots of angles and
distances need to be calculated by hand.

For symmetric sections it passes the parameters to ``.polyline`` twice
-- first in normal order and then reversed to get the mirrored section.

This generator is beyond what Boxes.py is designed for. If you need
something similar you may want to use another tool like OpenScad or a
traditional CAD program.
