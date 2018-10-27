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

    def run(self):
        self.execute(self.buildInkscapeExt, ())
        try:
            path = check_output(["inkscape", "-x"])
            if not os.access(path, os.W_OK): # Can we install globaly
                # Not tested on Windows and Mac
                path = os.path.expanduser("~/.config/inkscape/extensions")

            if self.distribution.data_files is None:
                self.distribution.data_files = []
            self.distribution.data_files.append(
                (path,
                 [i for i in glob.glob(os.path.join("inkex", "*.inx"))]))
            self.distribution.data_files.append((path, ['scripts/boxes']))
        except CalledProcessError:
            pass # Inkscape is not installed

        build_py.run(self)

setup(
    name='boxes',
    version='0.1',
    description='Boxes generator for laser cutters',
    author='Florian Festi',
    author_email='florian@festi.info',
    url='https://github.com/florianfesti/boxes',
    packages=find_packages(),
    install_requires=['cairocffi==0.8.0', 'markdown', 'lxml'],
    scripts=['scripts/boxes', 'scripts/boxesserver'],
    cmdclass={
        'build_py': CustomBuildExtCommand,
    },
    classifiers=[
        "Development Status :: 4 - Beta",
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
