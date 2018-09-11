Contributing to Boxes&#46;py
============================

You are thinking about contributing to Boxes&#46;py? That's great!
Boxes&#46;py is designed to be re-used and extended.

This document gives you some guidelines how your contribution is most
likely to impact the development and your changes are most likely to
be merged into the upstream repository.

Most of them should be just general best practises and not be
surprising. Don't worry if you find them too complicated. It is OK
leave the final touch to someone else.

Writing code for Boxes&#46;py
-----------------------------

You will often be compelled to just do a quick thing that will solve
your immediate needs. That's fine. But nevertheless it is often worth
doing things the right way and be able to submit your changes
upstream. For one to give something back to the community. But also
for purly selfish reasons like getting the code maintained. Also
Boxes&#46;py is designed to make doing things properly the easy way.

Here are some guidelines that make this easier. Depending on what you
are up to they may apply to a varying degree. It's ok to submit
patches that are not quite ready yet. But please state in the pull
request message what you think the status is and whether you want help
or are going to finish it on your own.

* Please fork the repository at GitHub before getting started
* Start with creating separate branches for each of your new  generators or features

  * You can merge them into your master branch to have them all in one place
  * Please continue your work in the branches and repeatedly merge them to master

* Before submitting a pull request intened to go upstream have clean patches that are self contained and error free

  * Re-order and squash patches with *git rebase -i*
  * The patches should contaning meaningful changes and not (nessesarily) reflect how the code was created 
  * Rebase your branch to the current master branch
  * Be prepared that you code may get reworked before being merged upstream

* Submit a pull request in GitHub based on your feature branch

  * Describe the status of the patch set and your intentions with it in the pull request message

If you want to discuss your idea open a ticket describing it and ask
questions there. This is encouraged even if you think you know what
you want to do. There are many short cuts in Boxes&#46;py and pointing you
in the right direction may save you a lot of work.

If you want feed back on you code feel free to open a PR. State that
this is work in progress in the PR message. It's OK if it does not
follow the guide lines (yet).

Writing new Generators
......................

Writing new generators is the most straight forward thing to do with
Boxes&#46;py. Here are some guidelines that make it easier to get them added:

* Start with a copy of another generator or *boxes/generators/_template.py*
* Commit changes to the library in separate patches
* Use arguments with sane defaults instead of hard coding measurements
* Simple generators can end up as one single commit
* For more complicated generators there can be multiple patches -
  each adding another feature

Improving the Documentation
---------------------------

Boxes&#46;py comes with Sphinx based documentation that is in large parts
generated from the doc strings in the code. Nevertheless documentation
has a tendency to get outdated. If you encounter outdated pieces of
documentation feel free to submit a pull request or open a ticket
pointing out what should be changed or even suggesting a better text.

To get the docs updated the docs need to be build with *make html* in
*documentation/src* and then the files need ot be updated in the *gh-pages*
branch. That's a bit tricky. Feel free to not even bother with this
and just submit the changes to the sources or just open a ticket.

Improving the User Interface
----------------------------

Coming up with good names and good descriptions is hard. Often writing
a new generator is much easier than coming up with a good name for it
and its arguments. If you think something deserves a better name or
description and you can come up with one please don't hesitate to open
a ticket. It is this small things that make something like Boxes&#46;py
easy or hard to use.

There is also an - often empty - space for a longer text for each
generator that could house assembling instructions, instructions for
use or just more detailed descriptions. If you are interested in
writing some please open a ticket. Your text does not have to be
perfect. We can work on it together.

Reporting bugs
--------------

If you encounter issues with Boxes&#46;py, please open a ticket at
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
