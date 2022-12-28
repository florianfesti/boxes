==========================
Frequently Asked Questions
==========================

.. toctree::
   :maxdepth: 1

Can I sell boxes I created with Boxes.py
----------------------------------------

Yes. Boxes.py is under the GPLv3 license (see https://www.gnu.org/licenses/gpl-3.0.html). This license grants you far reaching rights on what you can do with the software including using it and the drawings it produces to any means. The license also puts some obligations on you. But those are about changing and distributing the software itself. The resulting drawings do not fall under the GPL license.

Why do my parts not fit together?
---------------------------------

Well, this could be a bug in Boxes.py but there are a few more likely causes to check for:

* The material you use does not have the thickness you think. Measure it with at least a caliper. Even a few hundredth of a millimeter will make the difference between a loose fit, a light or a heavy pressfit or no fit at all.

* You might have chosen the "burn" value too big. As it compensates for the material cut away by the laser smaller values make a looser fit, bigger values make a tighter fit. The right value may be different for different materials and different thicknesses.

Why is my box a bit too big?
----------------------------

By default all sizes are inner sizes. So on the outside the box is bigger as the walls need to go somewhere. Some generators offer an "outside" param that includes the walls in the measurements. In general you should check the generated parts for plausibility before hitting the start button on your laser cutter.

Why is my box a bit too small?
------------------------------

See above.

Why are my parts in the totally wrong size?
-------------------------------------------

Unfortunately some formats do not save the units of measurement or don't do so properly. DXF and SVG fall into this category. So different tools may see the same file in different sizes. You can use the "reference" param to get a rectangle of a defined size to check if the size is still right at the end of your tool chain.

Why are there tiny, weird loops in the corners?
-----------------------------------------------

These are called dog bones and make sure the corner is completely cut out. As lasers and milling tools are round they can't cut sharp inner corners. Have a look at :doc:`burn correction details <api_burn>` for details.

I really don't want those weird, tiny loops?
--------------------------------------------

You can set the ``inner_corners`` default setting to ``corner``

What settings were used to generate a drawing?
----------------------------------------------

If you do have a SVG or PostScript you can look into the meta data of the file. Most document viewers will have a ``Document properties`` window. You can also just open the file with a text editor and find the details at the first few lines.

Note that you can just use the URL in there to get back to the settings page to change some values. The difference between the settings and the rendered drawing is just ``render=0`` or ``render=1`` at the end of the URL.

For other formats you are currently out of luck.
