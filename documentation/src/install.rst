Installation
============

Boxes.py is a pure Python project that does support the regular setuptools
method of shipping with :code:`setup.py`. :code:`setup.py --help-commands` and
:code:`setup.py CMD --help` provide the necessary documentation for building,
installing or building binary formats.

Requirements
------------

Python
......

Boxes.py is implemented in Python 3. For supported minor version see :code:`setup.py`.

Python modules
..............

Boxes.py need a set of Python modules:

.. include:: ../../requirements.txt

When using a distribution the packages will typically be name be :code:`python-MODULE` or :code:`python3-MODULE`

pstoedit
........

While not a hard requirement Boxes.py uses :code:`pstoedit` (sometimes :code:`ps2edit`) to offer formats
that are not supported by directly by the graphics backend: DXF, gcode, PLT. Currently the location
Boxes.py looks for :code:`pstoedit` is hard coded to :code:`/usr/bin/pstoedit`
in the :code:`boxes.formats.Formats` class.

Python modules for development
..............................

For development (e.g. running the test suite and generating the documentation) the following modules are also needed:

.. include:: ../../requirements_dev.txt


Sphinx
......

For building the documentation locally you need the *Sphinx* documentation
generator (package name may be python-sphinx or python3-sphinx). It is
not needed for anything else. Boxes.py can be run and changed just
fine without.

Running from working dir
------------------------

Due to lazy developer(s) Boxes.py can also run from the Git checkout.
The scripts in :code:`scripts/` are all supposed to just work right
after :code:`git clone`. The Inkscape needs a bit manual work to get
running. See below.

Inkscape
--------

**As binary**

Boxes.py can be used as a set of Inkscape plugins. The package does
install the necessary .inx files to :code:`/usr/share/inkscape/extensions`
on unix operating systems. The .inx files assume that the :code:`boxes`
executable is available in the path (which it is when installing the
binary package)

**git repository easy way**

After cloning it may be most convenient to generate the .inx files
right in place by executing :code:`scripts/boxes2inkscape` with the target
path as only parameter.

- global: :code:`scripts/boxes2inkscape /usr/share/inkscape/extensions/`
- userspace: :code:`scripts/boxes2inkscape ~/.config/inkscape/extensions/`

On non unix operating the target directories may differ. You can look
up the directories *"User extensions"* and *"Inkscape extensions"* within
the Inkscape preferences *Edit -> Preferences... -> System*.

**git repository manual way**

:code:`setup.py build` creates the :code:`*.inx` files in the :code:`inkex/` directory.

They then have to be copied in either the global or the per user
extension directory of Inkscape. These are
:code:`/usr/share/inkscape/extensions/` and
:code:`~/.config/inkscape/extensions/` on a unix operating system.
On non unix operating the target directories may differ. You can look
up the directories *"User extensions"* and *"Inkscape extensions"* within
the Inkscape preferences *Edit -> Preferences... -> System*.

As an alternative you can create a symlink to the :code:`inkex/` directory
within the desired inkscape extension directory.


Platform specific instructions
------------------------------

.. toctree::
   :maxdepth: 2
   :glob:

   install/*
