#!/usr/bin/python3

import boxes
import sys
import argparse
import cgi
import tempfile
import os

from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server
import wsgiref.util

import box, box2, box3, drillbox, flexbox, flexbox2, flexbox3, flextest, folder
import magazinefile, trayinsert, typetray, silverwarebox


class ArgumentParserError(Exception): pass

class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)
boxes.ArgumentParser = ThrowingArgumentParser # Evil hack

class BServer:
    def __init__(self):
        self.boxes = {
            "DemoBox" : boxes.DemoBox(),
            "Box" : box.Box(),
            "Box2" : box2.Box(),
            "Box3" : box3.Box(),
            "DrillBox" : drillbox.Box(),
            "FlexBox" : flexbox.FlexBox(),
            "FlexBox2" : flexbox2.FlexBox(),
            "FlexBox3" : flexbox3.FlexBox(),
            "FlexTest": flextest.FlexTest(),
            "Folder": folder.Folder(),
            "MagazinFile" : magazinefile.Box(),
            "TrayInsert" : trayinsert.TrayInsert(),
            "TypeTray" : typetray.TypeTray(),
            "SilverwareBox" : silverwarebox.Silverware(),
            }

    def arg2html(self, a):
        name = a.option_strings[0].replace("-", "")
        if isinstance(a, argparse._HelpAction):
            return ""
        if isinstance(a, argparse._StoreTrueAction):
            return """<tr><td>%s</td><td><input name="%s" type="checkbox" value="%s"></td><td>%s</td></tr>\n""" % \
            (name, name, a.default, a.help)
        
        return """<tr><td>%s</td><td><input name="%s" type="text" value="%s"></td><td>%s</td></tr>\n""" % \
            (name, name, a.default, a.help)
    
    def args2html(self, name, args):
        result = ["""<html><head><title>Boxes - """, name, """</title></head>
<body>
<form action="" method="POST" target="_blank">
<table>
"""]
        for a in args._actions:
            if a.dest == "output":
                continue
            result.append(self.arg2html(a))
            if a.dest == "burn":
                result.append("</table>\n<hr>\n<table>\n")
        result.append("""</table>
<button>Generate</button>
</form>
</body>
</html>
""")
        return (s.encode("utf-8") for s in result)
        
    def menu(self):
        result = ["""<html>
<head><title>Boxes for Laser Cutters</title></head>
<body>
Text
<ul>
""" ]
        for name in sorted(self.boxes):
            box = self.boxes[name]
            docs = ""
            if box.__doc__:
                docs = " - " + box.__doc__
            result.append("""  <li><a href="%s">%s</a>%s</li>""" % (
                name, name, docs))
        result.append("""</ul>
</body>
</html>
""")
        return (s.encode("utf-8") for s in result)


    def errorMessage(self, name, e):
        return [
            b"""<html><head><title>Error generating""", name.encode(),
            b"""</title><head>
<body>
<h1>An error occurred!</h1>
<p>""", str(e).encode(), b"""</p>
</body>
</html>
""" ]

    def serve(self, environ, start_response):
        status = '200 OK'
        headers = [('Content-type', 'text/html; charset=utf-8')]
        
        d = cgi.parse_qs(environ['QUERY_STRING'])
        name = environ["PATH_INFO"][1:]
        box = self.boxes.get(name, None)
        if not box:
            start_response(status, headers)
            return self.menu()

        if environ["REQUEST_METHOD"] == "GET":
            start_response(status, headers)
            return self.args2html(name, box.argparser)
        elif environ["REQUEST_METHOD"] == "POST":
            try:
                length = int(environ.get('CONTENT_LENGTH', '0'))
            except ValueError:
                length = 0
            body = environ['wsgi.input'].read(length).decode()
            args = ["--"+arg for arg in body.split("&")]
            try:
                box.parseArgs(args)
            except (ArgumentParserError) as e:
                start_response(status, headers)
                return self.errorMessage(name, e)
            start_response(status,
                           [('Content-type', 'image/svg+xml; charset=utf-8')])
            fd, box.output = tempfile.mkstemp()
            box.render()
            result = open(box.output).readlines()
            os.remove(box.output)
            os.close(fd)
            return (l.encode("utf-8") for l in result)

if __name__=="__main__":
    boxserver = BServer()
    httpd = make_server('', 8000, boxserver.serve)
    print("Serving on port 8000...")
    httpd.serve_forever()
