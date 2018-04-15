#!/usr/bin/env python3

import glob
import os
import sys
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
        if os.name == "posix":
            if self.distribution.data_files is None:
                self.distribution.data_files = []
            self.distribution.data_files.append(
                ("/usr/share/inkscape/extensions/",
                 [i for i in glob.glob(os.path.join("inkex", "*.inx"))]))
        build_py.run(self)

setup(
    name='boxes',
    version='0.1',
    description='Boxes generator for laser cutters',
    author='Florian Festi',
    author_email='florian@festi.info',
    url='https://github.com/florianfesti/boxes',
    packages=find_packages(),
    install_requires=['cairocffi==0.8.0', 'markdown'],
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
