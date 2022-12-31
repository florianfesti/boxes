#!/usr/bin/env python3
# Copyright (C) 2013-2014 Florian Festi
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import shutil
import subprocess
import tempfile

from boxes.drawing import SVGSurface, PSSurface, LBRN2Surface, Context


class Formats:

    pstoedit_candidates = ["/usr/bin/pstoedit", "pstoedit", "pstoedit.exe"]

    _BASE_FORMATS = ['svg', 'svg_Ponoko', 'ps', 'lbrn2']

    formats = {
        "svg": None,
        "svg_Ponoko": None,
        "ps": None,
        "lbrn2": None,
        "dxf": "-flat 0.1 -f dxf:-mm".split(),
        "gcode": "-f gcode".split(),
        "plt": "-f plot-hpgl".split(),
        "ai": "-f ps2ai".split(),
        "pdf": "-f pdf".split(),
    }

    http_headers = {
        "svg": [('Content-type', 'image/svg+xml; charset=utf-8')],
        "svg_Ponoko": [('Content-type', 'image/svg+xml; charset=utf-8')],
        "ps": [('Content-type', 'application/postscript')],
        "lbrn2": [('Content-type', 'application/lbrn2')],
        "dxf": [('Content-type', 'image/vnd.dxf')],
        "plt": [('Content-type', ' application/vnd.hp-hpgl')],
        "gcode": [('Content-type', 'text/plain; charset=utf-8')],

        # "" : [('Content-type', '')],
    }

    def __init__(self):
        for cmd in self.pstoedit_candidates:
            self.pstoedit = shutil.which(cmd)
            if self.pstoedit:
                break

    def getFormats(self):
        if self.pstoedit:
            return sorted(self.formats.keys())
        return self._BASE_FORMATS

    def getSurface(self, fmt, filename):
        if fmt in ("svg", "svg_Ponoko"):
            surface = SVGSurface(filename)
        elif fmt == "lbrn2":
            surface = LBRN2Surface(filename)
        else:
            surface = PSSurface(filename)

        ctx = Context(surface)
        return surface, ctx

    def convert(self, filename, fmt, metadata=None):

        if fmt not in self._BASE_FORMATS:
            fd, tmpfile = tempfile.mkstemp(dir=os.path.dirname(filename))
            cmd = [self.pstoedit] + self.formats[fmt] + [filename, tmpfile]
            err = subprocess.call(cmd)

            if err:
                # XXX show stderr output
                try:
                    os.unlink(tmpfile)
                except:
                    pass
                raise ValueError("Conversion failed. pstoedit returned %i" % err)

            os.rename(tmpfile, filename)
