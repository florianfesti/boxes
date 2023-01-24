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
import inkex
import sys
import os
from lxml import etree

class boxesPyWrapper(inkex.GenerateExtension):

    def add_arguments(self, pars):
        args = sys.argv[1:] 
        for arg in args:
            key=arg.split("=")[0]
            if len(arg.split("=")) == 2:
                value=arg.split("=")[1]
                try:
                    pars.add_argument(key, default=key)
                except:
                    pass #ignore duplicate id arg

    def generate(self):
        box_file = "box.svg"
        if os.path.exists(box_file):
            os.remove(box_file) #remove previously generated box file at the beginning

        cmd = "boxes" #boxes.exe in this local dir (or if present in %PATH%), or boxes from $PATH in linux        
        for arg in vars(self.options):
            if arg != "output" and arg != "ids" and arg != "selected_nodes":
                #inkex.utils.debug(str(arg) + " = " + str(getattr(self.options, arg)))
                #fix behaviour of "original" arg which does not correctly gets interpreted if set to false
                if arg == "original" and str(getattr(self.options, arg)) == "false":
                    continue
                if arg in ("input_file", "tab"):
                    continue
                else:
                    cmd += " --" + arg + " " + str(getattr(self.options, arg))
        cmd += " --output " + box_file + " " + box_file #we need to add box_file string twice in a row. Otherwise program executable throws an error
        cmd = cmd.replace("boxes --generator", "boxes")
        
        # run boxes with the parameters provided
        with os.popen(cmd, "r") as boxes:
            result = boxes.read()
        
        # check output existence
        try:
            stream = open(box_file, 'r')
        except FileNotFoundError as e:
            inkex.utils.debug("There was no " + box_file + " output generated. Cannot continue. Command was:")
            inkex.utils.debug(str(cmd))
            exit(1)
            
        # write the generated SVG into Inkscape's canvas
        p = etree.XMLParser(huge_tree=True)
        doc = etree.parse(stream, parser=etree.XMLParser(huge_tree=True))
        stream.close()
        if os.path.exists(box_file):
            os.remove(box_file) #remove previously generated box file at the end too      
            
        group = inkex.Group(id="boxes.py")
        for element in doc.getroot():
            group.append(element)
        return group
        
if __name__ == '__main__':
    boxesPyWrapper().run()