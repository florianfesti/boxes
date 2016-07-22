
import subprocess
import tempfile
import os
import cairo
from boxes import svgutil

class Formats:

    pstoedit = "/usr/bin/pstoedit"

    formats = {
        "svg" : None,
        "ps" : None,
        "dxf" : "-flat 0.1 -f dxf:-mm".split(),
        "gcode" : "-f gcode".split(),
        "plt" : "-f plot-hpgl".split(),
        "ai" : "-f ps2ai".split(),
        "pdf" : "-f pdf".split(),
    }

    http_headers = {
        "svg" : [('Content-type', 'image/svg+xml; charset=utf-8')],
        "ps" : [('Content-type', 'application/postscript')],
        "dxf" : [('Content-type', 'image/vnd.dxf')],
        "plt" : [('Content-type', ' application/vnd.hp-hpgl')],
        "gcode" : [('Content-type', 'text/plain; charset=utf-8')],

        # "" : [('Content-type', '')],
    }
    
    def __init__(self):
        pass

    def getFormats(self):
        if os.path.isfile(self.pstoedit):
            return sorted(self.formats.keys())
        else:
            return ['svg', 'ps']

    def getSurface(self, fmt, filename):

        width = height = 10000 # mm

        if fmt == "svg":
            surface = cairo.SVGSurface(filename, width, height)
            mm2pt = 1.0
        else:
            mm2pt = 72 / 25.4
            width *= mm2pt
            height *= mm2pt #3.543307
            surface = cairo.PSSurface(filename, width, height)

        ctx = cairo.Context(surface)
        ctx.translate(0, height)
        ctx.scale(mm2pt, -mm2pt)

        ctx.set_source_rgb(0.0, 0.0, 0.0)

        return surface, ctx

    def convert(self, filename, fmt):

        if fmt == 'svg':
            svg = svgutil.SVGFile(filename)
            svg.getEnvelope()
            svg.rewriteViewPort()
        elif fmt == "ps":
            pass
        else:
            fd, tmpfile = tempfile.mkstemp()
            cmd = [self.pstoedit] + self.formats[fmt] + [filename, tmpfile]
            err = subprocess.call(cmd)
            if err:
                # XXX show stderr output
                raise ValueError("Conversion failed. pstoedit returned %i" % err)
            os.rename(tmpfile, filename)
