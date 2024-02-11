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
import io

from boxes.drawing import SVGSurface, PSSurface, LBRN2Surface, Context


class Formats:

    pstoedit_candidates = ["/usr/bin/pstoedit", "pstoedit", "pstoedit.exe"]
    ps2pdf_candidates = ["/usr/bin/ps2pdf", "ps2pdf", "ps2pdf.exe"]

    _BASE_FORMATS = ['svg', 'svg_Ponoko', 'ps', 'lbrn2']

    formats = {
        "svg": None,
        "svg_Ponoko": None,
        "ps": None,
        "lbrn2": None,
        "dxf": "{pstoedit} -flat 0.1 -f dxf:-mm",
        "gcode": "{pstoedit} -f gcode",
        "plt": "{pstoedit} -f hpgl",
        # "ai": "{pstoedit} -f ps2ai",
        "pdf": "{ps2pdf} -dEPSCrop - -",
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

    def __init__(self) -> None:
        for cmd in self.pstoedit_candidates:
            self.pstoedit = shutil.which(cmd)
            if self.pstoedit:
                break
        for cmd in self.ps2pdf_candidates:
            self.ps2pdf = shutil.which(cmd)
            if self.ps2pdf:
                break

    def getFormats(self):
        if self.pstoedit:
            return sorted(self.formats.keys())
        return self._BASE_FORMATS

    def getSurface(self, fmt):
        if fmt in ("svg", "svg_Ponoko"):
            surface = SVGSurface()
        elif fmt == "lbrn2":
            surface = LBRN2Surface()
        else:
            surface = PSSurface()

        ctx = Context(surface)
        return surface, ctx

    def convert(self, data, fmt):

        if fmt not in self._BASE_FORMATS:
            cmd = self.formats[fmt].format(
                pstoedit=self.pstoedit,
                ps2pdf=self.ps2pdf).split()

            result = subprocess.run(cmd, input=data.getvalue(), capture_output=True)
            if result.returncode:
                # XXX show stderr output
                raise ValueError("Conversion failed. pstoedit returned %i\n\n %s" % (result.returncode, result.stderr))
            data = io.BytesIO(result.stdout)

        return data
