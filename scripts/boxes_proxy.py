#!/usr/bin/env python3

"""
Extension for InkScape 1.0+

boxes.py wrapper script to make it work on Windows and Linux systems without duplicating .inx files

Author: Mario Voigt / FabLab Chemnitz
Mail: mario.voigt@stadtfabrikanten.org
Date: 27.04.2021
Last patch: 27.04.2021
License: GNU GPL v3

"""
import os
import subprocess
import sys
import tempfile
from shlex import quote

from inkex.extensions import GenerateExtension
from lxml import etree

import inkex


class boxesPyWrapper(GenerateExtension):
    def add_arguments(self, pars):
        args = sys.argv[1:]
        for arg in args:
            key = arg.split("=")[0]
            if key == "--id":
                continue
            if len(arg.split("=")) == 2:
                value = arg.split("=")[1]
                pars.add_argument(key, default=key)

    def generate(self):
        cmd = "boxes"  # boxes.exe in this local dir (or if present in %PATH%), or boxes from $PATH in linux
        for arg in vars(self.options):
            if arg in (
                    "output", "id", "ids", "selected_nodes",
                    "input_file", "tab"):
                continue
            # fix behaviour of "original" arg which does not correctly gets
            # interpreted if set to false
            if arg == "original" and str(getattr(self.options, arg)) == "false":
                continue
            cmd += f" --{arg} {quote(str(getattr(self.options, arg)))}"
        cmd += f" --output -"
        cmd = cmd.replace("boxes --generator", "boxes")

        # run boxes with the parameters provided
        result = subprocess.run(cmd.split(), capture_output=True)

        if result.returncode:
            inkex.utils.debug("Generating box svg failed.  Cannot continue. Command was:")
            inkex.utils.debug(str(cmd))
            inkex.utils.debug(str(result.stderr))
            exit(1)

        # write the generated SVG into Inkscape's canvas
        p = etree.XMLParser(huge_tree=True)
        doc = etree.fromstring(result.stdout, parser=etree.XMLParser(huge_tree=True))
        group = inkex.Group(id="boxes.py")
        for element in doc:
            group.append(element)
        return group


def main() -> None:
    boxesPyWrapper().run()


if __name__ == '__main__':
    main()
