Installation
============

Boxes.py is a pure Python project that does support the regular setuptools
method of shipping with *setup.py*. *setup.py --help-commands* and
*setup.py CMD --help* provide the necessary documentation for building,
installing or building binary formats.

Requirements
------------

Cairo
.....
Boxes.py is based on the cairo graphics library. It supports both the PyPi
version *cairocffi* and python-cairo that might be shipped with your
distribution.

Markdown
........
Markdown (package name may be python-markdown or python3-markdown) is
used to format the description texts.

LXML
....

lxml (package name may be python-lxml or python3-lxml) is needed for
the Inkscape plugin.

ps2edit
.......

While not a hard requirement Boxes.py uses ps2edit to offer formats that are
not supported by Cairo: DXF, gcode, PLT. Currently the location Boxes.py looks
for *ps2edit* is hard coded to */usr/bin/pstoedit* in the
*boxes.formats.Formats* class.

Python
......

Boxes.py - while defaulting to Python3 -  can also run on Python
2.7. If you encounter any compatibility issues please report them at the
[https://github.com/florianfesti/boxes Git Hub project]

Running from working dir
------------------------

Due to lazy developer(s) Boxes.py can also run from the git check
out. The scripts in *scripts/* are all suppossed to just work right
after *git clone*. The Inkscape needs a bit manual work to get
running. See below.

Inkscape
--------

Boxes.py can be used as a set of Inkscape plugins. The package does
install the necessary .inx files to */usr/share/inkscape/extensions*
on unix operating systems. The .inx files assume that the *boxes*
executable is available in the path (which it is when installing the
binary package)

On non unix operating systems or when running Boxes.py from git
checkout the .inx files need to be copied by hand. *setup.py build*
creares them in the *inkex/* directory. They then have to be copied in
either the global or the per user extension directory of
Inkscape. These are */usr/share/inkscape/extensions/* and
*~/.config/inkscape/extensions/* on Unix. On other Operating systems
you can look up *Edit -> Preferences... -> System* in the Inkscape
menu to look up *User extensions* and *Inkscape extensions*. It may be
more convenient to generate the .inx files right in place by executing
*scripts/boxes2inkscape* with the taget path as only parameter.

After placing the .inx files you need to make the *boxes* script
available in the path. One way is to create a symlink from a location
that is in the path or installing the package on the system.

Boxes.py on Windows
-------------------

While there is no known reason why Boxes.py should not run on Windows
there is no upstream experience with doing so. Getting the Inkscape
plugins to run will likely need manual installation (see above). If
you run into trouble or have better installation instructions please
open a ticket on Git Hub.
