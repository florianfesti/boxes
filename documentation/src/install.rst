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

Boxes.py - while defaulting to Python3 - can also run on Python
2.7. If you encounter any compatibility issues please report them at the
`GitHub project <https://github.com/florianfesti/boxes>`__.

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
there is no upstream experience with doing so. The tricky part is
getting the cairo library installed and to run with the Python version
used. Python version and the architecture (32 or 64 bit) must match.

Getting the Inkscape plugins to run will likely need manual
installation (see above). Note that Inkscape may come with its own
Python. If you run into trouble or have better installation
instructions please open a ticket on GitHub.

Following steps are known to work under Windows 10 (64-bit):

1.  Go to https://www.python.org/downloads/windows/
    and download the "Windows x86-64 executable installer" for Python 3.7
2.  Install Python 3.7 and make sure to check "Add Python 3.7 to PATH"
    while doing so
3.  Go to https://www.lfd.uci.edu/~gohlke/pythonlibs/#cairocffi
    and download :code:`cairocffi‑1.0.2‑cp37‑cp37m‑win_amd64.whl`
4.  Go to https://www.lfd.uci.edu/~gohlke/pythonlibs/#pycairo
    and download `pycairo‑1.18.0‑cp37‑cp37m‑win_amd64.whl`
5.  Open the Command Prompt
    (i.e. via the shortcut Windows + R and then typing "cmd"
    and pressing Enter)
6.  Change to the folder where the .whl files from step 3 and 4 are located
    (e.g. with the command :code:`cd \Users\[USERNAME]\Downloads`
    where `[USERNAME]` is your username and `Downloads` the folder where
    the .whl files are located)
7.  Run the command :code:`pip install cairocffi‑1.0.2‑cp37‑cp37m‑win_amd64.whl
    pycairo‑1.18.0‑cp37‑cp37m‑win_amd64.whl Markdown lxml`
    (Note: If the command pip is not found, you probably forgot to add the
    Python installation to the PATH environment variable in step 2)
8.  Download Boxes.py as ZIP archive from GitHub
9.  Extract the ZIP archive
    (e.g. via the built-in Windows feature or other tools like 7-Zip)
10. Change into the folder for Boxes.py,
    e.g. with the command :code:`cd \Users\[USERNAME]\Downloads\boxes-master`
11. Run the development server with the command
    :code:`python scripts\boxesserver`
12. Open the address http://localhost:8000/ in your browser and have fun :)

Alternatively the command line version of Boxes.py can be used with
the command :code:`python scripts\boxes`.

Another way of installing Boxes.py on Windows is to use the Windows Subsystem
for Linux (WSL). This requires newer versions of Windows 10. Once it is
installed (e.g. via the Ubuntu App from the Microsoft Store), the installation
is identical to the installation on Linux systems.
