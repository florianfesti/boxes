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

import box, box2, box3, flexbox, flexbox2, flexbox3, flextest, folder
import magazinefile, trayinsert, typetray


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
            "FlexBox" : flexbox.FlexBox(),
            "FlexBox2" : flexbox2.FlexBox(),
            "FlexBox3" : flexbox3.FlexBox(),
            }

    def arg2html(self, a):
        name = a.option_strings[0].replace("-", "")
        if isinstance(a, argparse._HelpAction):
            return ""
        if isinstance(a, argparse._StoreTrueAction):
            return """<tr><td>%s</td><td><input name="%s" type="checkbox" value="%s"></td><td>%s</td></tr>\n""" % \
            (name, name, a.default or "", a.help)
        
        return """<tr><td>%s</td><td><input name="%s" type="text" value="%s"></td><td>%s</td></tr>\n""" % \
            (name, name, a.default or "", a.help)
    
    def args2html(self, args, msg=""):
        if msg:
            msg = str(msg).replace("--", "")
            msg = """\n<p><span style="color:red">%s</span></p>\n""" % msg
            
        result = ["""<html><head><title>Foo</title></head>
<body>%s
<form action="" method="POST" target="svg">
<table>
""" % msg ]
        #for a in args._actions:
        #    print(a.__class__.__name__, a.option_strings, repr(a))
        for a in args._actions:
            if a.dest == "output":
                continue
            result.append(self.arg2html(a))
            if a.dest == "burn":
                result.append("</table>\n<hr>\n<table>\n")
        result.append("""</table>
<button>Generate</button>
</form>
<iframe width=100% height=100% name="svg">
</iframe>
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

    def serve(self, environ, start_response):
        status = '200 OK'
        headers = [('Content-type', 'text/html; charset=utf-8')]
        #headers = [('Content-type', 'text/plain; charset=utf-8')]
        start_response(status, headers)
        
        d = cgi.parse_qs(environ['QUERY_STRING'])

        box = self.boxes.get(environ["PATH_INFO"][1:], None)
        if environ["REQUEST_METHOD"] == "GET":
            if box:
                return self.args2html(box.argparser)
            else:
                return self.menu()

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
                return self.args2html(box.argparser, e)
            fd, box.output = tempfile.mkstemp()
            box.render()
            result = open(box.output).readlines()
            os.remove(box.output)
            os.close(fd)
            return (l.encode("utf-8") for l in result)

        return [b"???"]

if __name__=="__main__":
    boxserver = BServer()
    httpd = make_server('', 8000, boxserver.serve)
    print("Serving on port 8000...")
    httpd.serve_forever()
