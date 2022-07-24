Contributing to Boxes.py
========================

You are thinking about contributing to Boxes.py? That's great!
Boxes.py is designed to be re-used and extended.

This document gives you some guidelines how your contribution is most
likely to impact the development and your changes are most likely to
be merged into the upstream repository.

Most of them should be just general best practises and not be
surprising. Don't worry if you find them too complicated. It is OK
leave the final touch to someone else.

Writing code for Boxes.py
-------------------------

You will often be compelled to just do a quick thing that will solve
your immediate needs. That's fine. But nevertheless it is often worth
doing things the right way and be able to submit your changes
upstream. For one to give something back to the community. But also
for purely selfish reasons like getting the code maintained. Also
Boxes.py is designed to make doing things properly the easy way.

Here are some guidelines that make this easier. Depending on what you
are up to they may apply to a varying degree. It's ok to submit
patches that are not quite ready yet. But please state in the pull
request message what you think the status is and whether you want help
or are going to finish it on your own.

* Please fork the repository at GitHub before getting started
* Start with creating separate branches for each of your new  generators or features

  * You can merge them into your master branch to have them all in one place
  * Please continue your work in the branches and repeatedly merge them to master

* Before submitting a pull request intended to go upstream have clean patches that are self contained and error free

  * Re-order and squash patches with *git rebase -i*
  * The patches should containing meaningful changes and not (necessarily) reflect how the code was created
  * Rebase your branch to the current master branch
  * Be prepared that your code may get reworked before being merged upstream

* Submit a pull request in GitHub based on your feature branch

  * Describe the status of the patch set and your intentions with it in the pull request message

If you want to discuss your idea open a ticket describing it and ask
questions there. This is encouraged even if you think you know what
you want to do. There are many short cuts in Boxes.py and pointing you
in the right direction may save you a lot of work.

If you want feed back on you code feel free to open a PR. State that
this is work in progress in the PR message. It's OK if it does not
follow the guidelines (yet).

Writing new Generators
......................

Writing new generators is the most straight forward thing to do with
Boxes.py. Here are some guidelines that make it easier to get them added:

* Start with a copy of another generator or *boxes/generators/_template.py*
* Commit changes to the library in separate patches
* Use parameters with sane defaults instead of hard coding dimensions
* Simple generators can end up as one single commit
* For more complicated generators there can be multiple patches -
  each adding another feature

Adding new Dependencies
.......................

Adding new dependencies should be considered thoroughly. If a new
depencendcy is added it needs to be added in all these places:

* *documentation/src/install.rst*
* RST files in *documentation/src/install/*
* *scripts/Dockerfile*
* *.travis.yml*

If it is a Python module it also needs to be added:
* *requirements.txt*
* *setup.py*

Improving the Documentation
---------------------------

Boxes.py comes with Sphinx based documentation that is in large parts
generated from the doc strings in the code. Nevertheless documentation
has a tendency to get outdated. If you encounter outdated pieces of
documentation feel free to submit a pull request or open a ticket
pointing out what should be changed or even suggesting a better text.

To check your changes docs need to be build with *make html* in
*documentation/src*. This places the compiled documentation in
*documentation/build/html*. You need to have *sphinx* installed for
this to work.

The online documentation gets build and updated automatically by the Travis CI
as soon as the changes makes it into the GitHub master branch.

Provide photos for generators
-----------------------------

Many generators still come without an example photo. If you are
creating such an item consider donating a good picture. You can
simply attach it to `ticket #140
<https://github.com/florianfesti/boxes/issues/140>`_. If you want you can
also create a proper pull request instead:

* Make sure you have sh, convert (ImageMagick), sed and sha256sum installed
* The picture needs to be an jpg file with the name of the generator
  (This is case sensitive. Use CamelCase.)
* The picture should be 1200 pixels wide and square or not too far
  from square (3:4 is fine).
* Place the file in *static/samples/*
* Check if the picture shows up at the bottom of the settings page of
  the generator when running *scripts/boxesserver*
* Change dir to *./scripts* and there execute *./gen_thumbnails.sh*
* Check if the thumbnail is seen in the main page when hovering over
  the generator entry
* Create a commit including *static/samples/$GeneratorName\*.jpg* and
  *static/samples/samples.sha256*
* Create a pull request from that

Improving the User Interface
----------------------------

Coming up with good names and good descriptions is hard. Often writing
a new generator is much easier than coming up with a good name for it
and its arguments. If you think something deserves a better name or
description and you can come up with one please don't hesitate to open
a ticket. It is this small things that make something like Boxes.py
easy or hard to use.

There is also an - often empty - space for a longer text for each
generator that could house assembling instructions, instructions for
use or just more detailed descriptions. If you are interested in
writing some please open a ticket. Your text does not have to be
perfect. We can work on it together.

Running the Code
----------------------------

To serve website, run `scripts/boxesserver` script

Reporting bugs
--------------

If you encounter issues with Boxes.py, please open a ticket at
GitHub. Please provide all information necessary to reproduce the
bug. Often this can be the URL of the broken result. If the issue is
easy to spot it may be sufficient to just give a brief
description. Otherwise it can be helpful to attach the resulting SVG,
a screen shot or the error message. Add a "bug" tag to draw additional
attention.

Suggesting new generators or features
-------------------------------------

If you have an idea for a new generator or feature please open a
ticket. Give some short rational how or where you would use such a
thing. Try to give a precise description how it should look like and
which features and details are important. The less is left open the
easier it is to implement. You can add an "enhancement" tag.
