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

setuptools
..........

Setup.py uses the setuptools library (package name may be
python*-setuptools). You only need it if you want to build the
package.



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

**As binary**

Boxes.py can be used as a set of Inkscape plugins. The package does
install the necessary .inx files to */usr/share/inkscape/extensions*
on unix operating systems. The .inx files assume that the *boxes*
executable is available in the path (which it is when installing the
binary package)

**git repository easy way**

After cloning it may be most convenient to generate the .inx files 
right in place by executing *scripts/boxes2inkscape* with the taget 
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
*/usr/share/inkscape/extensions/* and *~/.config/inkscape/extensions/* 
on a unix operating system. 
On non unix operating the target directories may differ. You can look 
up the directories *User extensions* and *Inkscape extensions* within 
the Inkscape preferences *Edit -> Preferences... -> System*.

As an alternative you can create a symlink to the inkex directory within 
the inkscape extension directory.


Boxes.py on Windows
-------------------

While there is no known reason why Boxes.py should not run on Windows
there is no upstream experience with doing so. The tricky part is
getting the cairo library installed and to run with the Python version
used. Python version and the architecture (32 or 64 bit) must match.

Getting the Inkscape plugins to run will likely need manual
installation (see above). Note that Inkscape may come with its own
Python. If you run into trouble or have better installation
instructions please open a ticket on Git Hub.
