Installation
============

Boxes.py is a pure Python project that does support the regular setuptools
method of shipping with :code:`setup.py`. :code:`setup.py --help-commands` and
:code:`setup.py CMD --help` provide the necessary documentation for building,
installing or building binary formats.

Requirements
------------

Cairo
.....
Boxes.py is based on the cairo graphics library. It supports both the PyPi
version :code:`cairocffi` and :code:`python-cairo` that might be shipped with
your distribution.

Markdown
........
:code:`Markdown` (package name may be :code:`python-markdown` or
:code:`python3-markdown`) is used to format the description texts.

LXML
....

:code:`lxml` (package name may be :code:`python-lxml` or :code:`python3-lxml`)
is needed for the Inkscape plugin.

setuptools
..........

Setup.py uses the :code:`setuptools` library (package name may be
:code:`python*-setuptools`). You only need it if you want to build the
package.

ps2edit
.......

While not a hard requirement Boxes.py uses :code:`ps2edit` to offer formats
that are not supported by Cairo: DXF, gcode, PLT. Currently the location
Boxes.py looks for :code:`ps2edit` is hard coded to :code:`/usr/bin/pstoedit`
in the :code:`boxes.formats.Formats` class.

Python
......

Boxes.py - while defaulting to Python 3 - can also run on Python 2.7.
If you encounter any compatibility issues please report them at the
`GitHub project <https://github.com/florianfesti/boxes>`__.

Running from working dir
------------------------

Due to lazy developer(s) Boxes.py can also run from the Git checkout.
The scripts in :code:`scripts/` are all suppossed to just work right
after :code:`git clone`. The Inkscape needs a bit manual work to get
running. See below.

Inkscape
--------

**As binary**

Boxes.py can be used as a set of Inkscape plugins. The package does
install the necessary .inx files to :code:`*/usr/share/inkscape/extensions*`
on unix operating systems. The .inx files assume that the *boxes*
executable is available in the path (which it is when installing the
binary package)

**git repository easy way**

After cloning it may be most convenient to generate the .inx files 
right in place by executing :code:`*scripts/boxes2inkscape*` with the taget 
path as only parameter.

global installation requires root access:

.. code::
   scripts/boxes2inkscape /usr/share/inkscape/extensions/

user installation

.. code::
   scripts/boxes2inkscape ~/.config/inkscape/extensions/

On non unix operating the target directories may differ. You can look 
up the directories *User extensions* and *Inkscape extensions* within 
the Inkscape preferences *Edit -> Preferences... -> System*.

**git repository manual way**

*setup.py build* creates the *.inx files in the *inkex/* directory. 

They then have to be copied in either the global or the per user 
extension directory of Inkscape. These are 
:code:`*/usr/share/inkscape/extensions/*` and 
:code:`*~/.config/inkscape/extensions/*` on a unix operating system. 
On non unix operating the target directories may differ. You can look 
up the directories *User extensions* and *Inkscape extensions* within 
the Inkscape preferences *Edit -> Preferences... -> System*.

As an alternative you can create a symlink to the inkex directory within 
the inkscape extension directory.


Platform specific instructions
------------------------------

.. toctree::
   :maxdepth: 2
   :glob:

   install/*

