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


import subprocess
import tempfile
import os
from boxes.drawing import SVGSurface, PSSurface, Context

class Formats:

    pstoedit = "/usr/bin/pstoedit"

    _BASE_FORMATS = ['svg', 'svg_Ponoko', 'ps']

    formats = {
        "svg": None,
        "svg_Ponoko": None,
        "ps": None,
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
        "dxf": [('Content-type', 'image/vnd.dxf')],
        "plt": [('Content-type', ' application/vnd.hp-hpgl')],
        "gcode": [('Content-type', 'text/plain; charset=utf-8')],

        # "" : [('Content-type', '')],
    }

    def __init__(self):
        pass

    def getFormats(self):
        if os.path.isfile(self.pstoedit):
            return sorted(self.formats.keys())
        else:
            return self._BASE_FORMATS

    def getSurface(self, fmt, filename):

        width = height = 10000  # mm 

        if fmt in ("svg", "svg_Ponoko"):
            surface = SVGSurface(filename, width, height)
            mm2pt = 1.0
        else:
            mm2pt = 72 / 25.4
            width *= mm2pt
            height *= mm2pt  # 3.543307
            surface = PSSurface(filename, width, height)

        ctx = Context(surface)
        if fmt in ("svg", "svg_Ponoko"):
            ctx.translate(0, height)
            ctx.scale(mm2pt, -mm2pt)
        else:
            ctx.scale(mm2pt, mm2pt)

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
