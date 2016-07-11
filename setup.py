#!/usr/bin/python3

from setuptools import setup, find_packages

setup(name='boxes.py',
      version='0.1',
      description='Boxes generator for laser cutters',
      author='Florian Festi',
      author_email='florian@festi.info',
      url='https://github.com/florianfesti/boxes',
      packages=find_packages(),
      install_requires=['cairocffi'],
      scripts=['scripts/boxes', 'scripts/boxesserver'],
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
      keywords=["boxes", "box", "generator", "svg", "laser cutter"],
)
