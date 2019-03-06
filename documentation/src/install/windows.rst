Windows
=======

While there is no known reason why Boxes.py should not run on Windows
there is no upstream experience with doing so. The tricky part is
getting the cairo library installed and to run with the Python version
used. Python version and the architecture (32 or 64 bit) must match.

Getting the Inkscape plugins to run will likely need manual
installation (see above). Note that Inkscape may come with its own
Python. If you run into trouble or have better installation
instructions please open a ticket on GitHub.

Native
------

Following steps are known to work under Windows 10 (64-bit):

1.  Go to https://www.python.org/downloads/windows/
    and download the "Windows x86-64 executable installer" for Python 3.7

    .. figure:: windows_browser_download_python.png
       :scale: 50%
       :alt: Screenshot of python.org with download of Python 3.7 (64-bit)
       :align: center

2.  Install Python 3.7 and make sure to check "Add Python 3.7 to PATH"
    while doing so

    .. figure:: windows_install_python_path.png
       :scale: 50%
       :alt: Screenshot of Python 3.7 (64-bit) installer with PATH checked
       :align: center

3.  Go to https://www.lfd.uci.edu/~gohlke/pythonlibs/#cairocffi
    and download :code:`cairocffi‑1.0.2‑cp37‑cp37m‑win_amd64.whl`

    .. figure:: windows_browser_download_pycairo.png
       :scale: 50%
       :alt: Screenshot of download for Python wheel of pycairo
       :align: center

4.  Go to https://www.lfd.uci.edu/~gohlke/pythonlibs/#pycairo
    and download `pycairo‑1.18.0‑cp37‑cp37m‑win_amd64.whl`

    .. figure:: windows_browser_download_cairocffi.png
       :scale: 50%
       :alt: Screenshot of download for Python wheel of cairocffi
       :align: center

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

    .. figure:: windows_cmd_pip_install_dependencies.png
       :scale: 50%
       :alt: Command Prompt with pip installing dependencies
       :align: center

8.  Download Boxes.py as ZIP archive from GitHub

    .. figure:: windows_browser_download_boxespy.png
       :scale: 50%
       :alt: Screenshot of download from Boxes.py project on GitHub
       :align: center

9.  Extract the ZIP archive
    (e.g. via the built-in Windows feature or other tools like 7-Zip)

    .. figure:: windows_boxespy_zip_extract.png
       :scale: 50%
       :alt: Screenshot of Windows tools to extract the ZIP archive
       :align: center

10. Change into the folder for Boxes.py,
    e.g. with the command :code:`cd \Users\[USERNAME]\Downloads\boxes-master`
11. Run the development server with the command
    :code:`python scripts\boxesserver`
    Note: You likely will be notified by your firewall that it blocked network
    access. If you want to use boxesserver you need to allow connections.

    .. figure:: windows_cmd_python_boxesserver_firewall.png
       :scale: 50%
       :alt: Screenshot of command for running boxesserver and firewall notice
       :align: center

12. Open the address http://localhost:8000/ in your browser and have fun :)

    .. figure:: windows_browser_boxespy.png
       :scale: 50%
       :alt: Screenshot of a browser window running Boxes.py locally
       :align: center


Additionally the command line version of Boxes.py can be used with
the command :code:`python scripts\boxes`.

Windows Subsystem for Linux
---------------------------

Another way of installing Boxes.py on Windows is to use the Windows Subsystem
for Linux (WSL). This requires newer versions of Windows 10. Once it is
installed (e.g. via the Ubuntu App from the Microsoft Store), the installation
is identical to the installation on Linux systems.
