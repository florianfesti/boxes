macOS
=====

It is recommended to use Homebrew to install the dependencies for Boxes.py.
See `brew.sh <https://brew.sh>`__ on how to install Homebrew.

General
-------

1. Install Python 3 and other dependencies:

   .. code::

      brew install python3 git

   Optional:

   .. code::

      brew install pstoedit


2. Install cairio:

  .. code::

      brew install pkg-config


3. Install required Python modules:

   .. code::

      pip3 install Markdown affine shapely

4. Download Boxes.py via Git:

   .. code::

      git clone https://github.com/florianfesti/boxes.git

5. Run Boxes.py:

   Local web server on port 8000:

   .. code::

      ./scripts/boxesserver

   Command line variant (CLI):

   .. code::

      ./scripts/boxes


System-wide with Inkscape extension
-----------------------------------

To install Boxes.py system-wide with the Inkscape extension, following steps
are required:

1. Install Inkscape with Homebrew Cask
   (requires `XQuartz <https://www.xquartz.org/>`__):

   .. code::

      brew install inkscape

2. From the root directory of the repository, run:

   .. code::

      ./setup.py install

3. Now :code:`boxes` and :code:`boxesserver` can be executed like other commands
   and the Inkscape extension should be available.


Troubleshooting
...............

When using the Inkscape extension something like the following error
might occur:

::

  Traceback (most recent call last):
    File "/Users/martin/.config/inkscape/extensions/boxes", line 107, in <module>
      main()
    File "/Users/martin/.config/inkscape/extensions/boxes", line 47, in main
      run_generator(name, sys.argv[2:])
    File "/Users/martin/.config/inkscape/extensions/boxes", line 73, in run_generator
      box.close()
    File "/usr/local/lib/python3.7/site-packages/boxes-0.1-py3.7.egg/boxes/__init__.py", line 594, in close
      svgutil.svgMerge(self.output, self.inkscapefile, out)
    File "/usr/local/lib/python3.7/site-packages/boxes-0.1-py3.7.egg/boxes/svgutil.py", line 144, in svgMerge
      from lxml import etree as et
  ImportError: dlopen(/Applications/Inkscape.app/Contents/Resources/lib/python2.7/site-packages/lxml/etree.so, 2): Symbol not found: _PyBaseString_Type
    Referenced from: /Applications/Inkscape.app/Contents/Resources/lib/python2.7/site-packages/lxml/etree.so
    Expected in: flat namespace

This is because Inkscape on macOS ships its own version of Python 2.7 where
:code:`lxml` and other dependencies are missing.

A workaround is to edit the file at
:code:`/Applications/Inkscape.app/Contents/Resources/bin/inkscape`.
At line 79 there should be following code:

.. code::

   export PYTHONPATH="$TOP/lib/python$PYTHON_VERS/site-packages/"

which needs to be changed to

.. code::

   #export PYTHONPATH="$TOP/lib/python$PYTHON_VERS/site-packages/"

This forces Inkscape to use the Python version installed by Homebrew which
has all the necessary dependencies installed.

Note: This might break other extensions. In this case simply change the line
back and restart Inkscape.
