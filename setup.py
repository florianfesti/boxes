#!/usr/bin/env python3

import glob
import os
import sys
from subprocess import check_output, CalledProcessError
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py


class CustomBuildExtCommand(build_py):
    """Customized setuptools install command - prints a friendly greeting."""

    def buildInkscapeExt(self):
        os.system("%s %s %s" % (sys.executable,
                                os.path.join("scripts", "boxes2inkscape"),
                                "inkex"))

    def updatePOT(self):
        os.system("%s %s %s" % (
            sys.executable,
            os.path.join("scripts", "boxes2pot"),
            "po/boxes.py.pot"))
        os.system("%s %s" % (
            "xgettext -L Python -j --from-code=utf-8 -o po/boxes.py.pot",
            "boxes/*.py scripts/boxesserver scripts/boxes"))

    def generate_mo_files(self):
        pos = glob.glob("po/*.po")

        for po in pos:
            lang = po.split(os.sep)[1][:-3].replace("-", "_")
            try:
                os.makedirs(os.path.join("locale", lang, "LC_MESSAGES"))
            except FileExistsError:
                pass
            os.system("msgfmt %s -o locale/%s/LC_MESSAGES/boxes.py.mo" % (po, lang))
            self.distribution.data_files.append(
                (os.path.join("share", "locale", lang, "LC_MESSAGES"),
                 [os.path.join("locale", lang, "LC_MESSAGES", "boxes.py.mo")]))

    def run(self):
        if self.distribution.data_files is None:
            self.distribution.data_files = []
        self.execute(self.updatePOT, ())
        self.execute(self.generate_mo_files, ())
        self.execute(self.buildInkscapeExt, ())

        if 'CURRENTLY_PACKAGING' in os.environ:
            # we are most probably building a Debian package
            # let us define a simple path!
            path="/usr/share/inkscape/extensions"
            self.distribution.data_files.append(
                (path,
                 [i for i in glob.glob(os.path.join("inkex", "*.inx"))]))
            self.distribution.data_files.append((path, ['scripts/boxes']))
        else:
            # we are surely not building a Debian package
            # then here is the default behavior:
            try:
                path = check_output(["inkscape", "--system-data-directory"]).decode().strip()
                path = os.path.join(path, "extensions")
                if not os.access(path, os.W_OK): # Can we install globally
                    # Not tested on Windows and Mac
                    path = os.path.expanduser("~/.config/inkscape/extensions")
                self.distribution.data_files.append(
                    (path,
                     [i for i in glob.glob(os.path.join("inkex", "*.inx"))]))
                self.distribution.data_files.append((path, ['scripts/boxes']))
            except CalledProcessError:
                pass # Inkscape is not installed

        build_py.run(self)

setup(
    name='boxes',
    version='0.9',
    description='Boxes generator for laser cutters',
    author='Florian Festi',
    author_email='florian@festi.info',
    url='https://github.com/florianfesti/boxes',
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=['affine>=2.0', 'markdown', 'shapely>=1.8.2'],
    scripts=['scripts/boxes', 'scripts/boxesserver'],
    cmdclass={
        'build_py': CustomBuildExtCommand,
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Manufacturing",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Graphics :: Editors :: Vector-Based",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Computer Aided Design",
    ],
    keywords=["boxes", "box", "generator", "svg", "laser cutter"], )
