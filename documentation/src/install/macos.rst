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


2. Install required Python modules:

   .. code::

      pip3 install pycairo cairocffi Markdown lxml

3. Download Boxes.py via Git:

   .. code::

      git clone https://github.com/florianfesti/boxes.git

4. Run Boxes.py:

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

      brew cask install inkscape

2. From the root directory of the repository, run:

   .. code::

      ./setup.py install

3. Now :code:`boxes` and :code:`boxesserver` can be runned like other commands
   and the Inkscape extension should be available.
