#!/usr/bin/env python3
# Copyright (C) 2016-2017 Florian Festi
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
from __future__ import annotations

import argparse
import gettext
import glob
import html
import io
import mimetypes
import os.path
import re
import sys
import threading
import time
import traceback
from typing import Any, NoReturn
from urllib.parse import quote, unquote_plus
from wsgiref.simple_server import make_server

import markdown  # type: ignore
import qrcode

try:
    import boxes.generators
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../.."))
    import boxes.generators
import boxes


class FileChecker(threading.Thread):
    def __init__(self, files=[], checkmodules: bool = True) -> None:
        super().__init__()
        self.checkmodules = checkmodules
        self.timestamps = {}
        self._stopped = False
        for path in files:
            self.timestamps[path] = os.stat(path).st_mtime
        if checkmodules:
            self._addModules()

    def _addModules(self) -> None:
        for name, module in sys.modules.items():
            path = getattr(module, "__file__", None)
            if not path:
                continue
            if path not in self.timestamps:
                self.timestamps[path] = os.stat(path).st_mtime

    def filesOK(self) -> bool:
        if self.checkmodules:
            self._addModules()
        for path, timestamp in self.timestamps.items():
            try:
                if os.stat(path).st_mtime != timestamp:
                    return False
            except FileNotFoundError:
                return False
        return True

    def run(self) -> None:
        while not self._stopped:
            if not self.filesOK():
                os.execv(__file__, sys.argv)
            time.sleep(1)

    def stop(self) -> None:
        self._stopped = True


def filter_url(url, non_default_args):
    if len(url) == 0:
        return ''
    try:
        base, args = url.split('?')
    except ValueError:
        return ''
    args = args.split('&')
    new_args = []
    args_to_ignore = ["qr_code", "format"]
    for arg in args:
        a, b = arg.split('=')
        if a.strip() in args_to_ignore:
            continue
        if a in non_default_args:
            new_args.append(arg)
    if len(new_args):
        return f"{base}?{'&'.join(new_args)}"
    else:
        return f"{base}"


class ArgumentParserError(Exception): pass


class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message) -> NoReturn:
        raise ArgumentParserError(message)


# Evil hack
boxes.ArgumentParser = ThrowingArgumentParser  # type: ignore


class BServer:
    lang_re = re.compile(r"([a-z]{2,3}(-[-a-zA-Z0-9]*)?)\s*(;\s*q=(\d\.?\d*))?")

    def __init__(self, url_prefix="", static_url="static", static_path="../static/", legal_url="") -> None:
        self.boxes = {b.__name__: b for b in boxes.generators.getAllBoxGenerators().values() if b.webinterface}
        self.groups = boxes.generators.ui_groups
        self.groups_by_name = boxes.generators.ui_groups_by_name

        for name, box in self.boxes.items():
            box.UI = "web"
            self.groups_by_name.get(box.ui_group,
                                    self.groups_by_name["Misc"]).add(box)

        if os.path.isabs(static_path):
            self.staticdir = static_path
        else:
            self.staticdir = os.path.join(os.path.dirname(__file__), '../static/')
            if not os.path.isdir(self.staticdir):
                self.staticdir = os.path.join(os.path.dirname(__file__), '..', '../static/')
        self._languages = None
        self._cache: dict[Any, Any] = {}
        self.url_prefix = url_prefix
        self.static_url = static_url
        self.legal_url = legal_url

    def getLanguages(self, domain=None, localedir=None):
        if self._languages is not None:
            return self._languages
        self._languages = []
        domain = "boxes.py"
        for localedir in ["locale", gettext._default_localedir]:
            files = glob.glob(os.path.join(localedir, '*', 'LC_MESSAGES', '%s.mo' % domain))
            self._languages.extend([file.split(os.path.sep)[-3] for file in files])
        self._languages.sort()
        return self._languages

    def getLanguage(self, args, accept_language):
        lang = None
        langs = []

        for i, arg in enumerate(args):
            if arg.startswith("language="):
                lang = arg[len("language="):]
                del args[i]
                break
        if lang:
            try:
                return gettext.translation('boxes.py', localedir='locale', languages=[lang])
            except OSError:
                pass
            try:
                return gettext.translation('boxes.py', languages=[lang])
            except OSError:
                pass

        # selected language not found try browser default
        languages = accept_language.split(",")
        for l in languages:
            m = self.lang_re.match(l.strip())
            if m:
                langs.append((float(m.group(4) or 1.0), m.group(1)))

        langs.sort(reverse=True)
        langs = [l[1].replace("-", "_") for l in langs]

        try:
            return gettext.translation('boxes.py', localedir='locale', languages=langs)
        except OSError:
            return gettext.translation('boxes.py', languages=langs, fallback=True)

    def arg2html(self, a, prefix, defaults={}, _=lambda s: s):
        name = a.option_strings[0].replace("-", "")
        if isinstance(a, argparse._HelpAction):
            return ""
        viewname = name
        if prefix and name.startswith(prefix + '_'):
            viewname = name[len(prefix) + 1:]

        default = defaults.get(name, None)
        row = """<tr><td id="%s"><label for="%s">%s</label></td><td>%%s</td><td id="%s">%s</td></tr>\n""" % \
              (name + "_id", name, _(viewname), name + "_description", "" if not a.help else markdown.markdown(_(a.help)))
        if (isinstance(a, argparse._StoreAction) and
                hasattr(a.type, "html")):
            input = a.type.html(name, default or a.default, _)
        elif a.type == str and "\n" in a.default:
            val = (default or a.default).split("\n")
            input = """<textarea name="%s" id="%s" aria-labeledby="%s %s" cols="%s" rows="%s">%s</textarea>""" % \
                    (name, name, name + "_id", name + "_description", max(len(l) for l in val) + 10, len(val) + 1, default or a.default)
        elif a.choices:
            options = "\n".join(
                """    <option value="%s"%s>%s</option>""" %
                (e, ' selected="selected"' if (e == (default or a.default)) or (str(e) == str(default or a.default)) else "",
                 _(e)) for e in a.choices)
            input = """<select name="{}" id="{}" aria-labeledby="{} {}" size="1">\n{}</select>\n""".format(name, name, name + "_id", name + "_description", options)
        else:
            input = """<input name="%s" id="%s" aria-labeledby="%s %s" type="text" value="%s">""" % \
                    (name, name, name + "_id", name + "_description", default or a.default)

        return row % input

    def args2html_cached(self, name, box, lang, action="", defaults={}):
        if defaults == {}:
            key = (name, lang.info().get('language', None), action)
            if key not in self._cache:
                self._cache[key] = list(self.args2html(name, box, lang, action, defaults))
            return self._cache[key]

        return self.args2html(name, box, lang, action, defaults)

    def args2html(self, name, box, lang, action="", defaults={}):
        _ = lang.gettext
        lang_name = lang.info().get('language', None)

        langparam = ""
        if lang_name:
            langparam = "?language=" + lang_name

        result = [f"""{self.genHTMLStart(lang)}
<head>
    <title>{_("%s - Boxes") % _(name)}</title>
    {self.genHTMLMeta()}
{self.genHTMLMetaLanguageLink()}
    {self.genHTMLCSS()}
    {self.genHTMLJS()}
</head>
<body onload="initArgsPage({len(box.argparser._action_groups) - 3})">

<div class="argumentcontainer">
<div style="float: left;">
<a href="./{langparam}"><h1>{_("Boxes.py")}</h1></a>
</div>
<div style="width: 120px; float: right;">
<img alt="self-Logo" src="{self.static_url}/boxes-logo.svg" width="120">
</div>
<div>
<div class="clear"></div>
<hr>
<div class="linkbar">
<ul>
{self.genLinks(lang, True)}
</ul>
</div>
<hr>

<h2 style="margin: 0px 0px 0px 20px;">{_(name)}</h2>
        <p>{_(box.__doc__) if box.__doc__ else ""}</p>
<form id="arguments" action="{action}" method="GET" rel="nofollow">
        """]
        groupid = 0
        for group in box.argparser._action_groups[3:] + box.argparser._action_groups[:3]:
            if not group._group_actions:
                continue
            if len(group._group_actions) == 1 and isinstance(group._group_actions[0], argparse._HelpAction):
                continue
            prefix = getattr(group, "prefix", None)
            result.append(f'''<h3 id="h-{groupid}" data-id="{groupid}" role="button" aria-expanded="true" tabindex="0" class="toggle open">{_(group.title)}</h3>\n<table role="presentation" id="{groupid}">\n''')

            for a in group._group_actions:
                if a.dest in ("input", "output"):
                    continue
                result.append(self.arg2html(a, prefix, defaults, _))
            result.append("</table>")
            groupid += 1

        result.append(f"""
<input type="hidden" name="language" id="language" value="{lang_name}">

<p>
    <button name="render" value="1" formtarget="_blank">{_("Generate")}</button>
    <button name="render" value="2" formtarget="_self">{_("Download")}</button>
    <button name="render" value="0" formtarget="_self">{_("Save to URL")}</button>
    <button name="render" value="3" formtarget="_blank">{_("QR Code")}</button>
</p>
</form>
</div>

<div class="clear"></div>
<hr>
<div class="description">
""")
        no_img_msg = _('There is no image yet. Please donate an image of your project on <a href=&quot;https://github.com/florianfesti/boxes/issues/628&quot; target=&quot;_blank&quot; rel=&quot;noopener&quot;>GitHub</a>!')

        if box.description:
            result.append(
                markdown.markdown(_(box.description), extensions=["extra"])
                .replace('src="static/', f'src="{self.static_url}/'))

        result.append(f'''<div>
<img style="width:100%;" src="{self.static_url}/samples/{box.__class__.__name__}.jpg" onerror="this.parentElement.innerHTML = '{no_img_msg}';" alt="Picture of box.">
</div>
</div>
</div>
<div id="preview">
  <div id="preview_buttons">
    {_("Zoom: ")}
    <button type="button" onclick="preview_scale/=1.2; document.getElementById('preview_img').style.width = preview_scale + '%';">-</button>
    <button type="button" onclick="preview_scale*= 1.2; document.getElementById('preview_img').style.width = preview_scale + '%';" >+</button>
    <button type="button" onclick="preview_scale=100; document.getElementById('preview_img').style.width = preview_scale + '%';" >{_("Reset")}</button>
  </div>
<div style="overflow: auto;">
<figure id="preview_figure" style="width: max-content;">
<img id="preview_img" style="width:100%" src="{self.static_url}/nothing.png">
</figure>
</div>
</div>
</body>
</html>
        ''')
        return (s.encode("utf-8") for s in result)

    def genPageMenu(self, lang):
        _ = lang.gettext
        lang_name = lang.info().get('language', None)

        langparam = ""
        if lang_name:
            langparam = "?language=" + lang_name

        result = [f"""{self.genHTMLStart(lang)}
<head>
    <title>{_("Boxes.py")}</title>
    {self.genHTMLMeta()}
{self.genHTMLMetaLanguageLink()}
    {self.genHTMLCSS()}
    {self.genHTMLJS()}
</head>
<body onload="initPage()">
<div class="container">
<div style="width: 75%; float: left;">
{self.genPagePartHeader(lang)}
<div class="modenav">
<span class="modebutton"><a href="Gallery">{_("Gallery")}</a></span>
<span class="modebutton modeactive">{_("Menu")}</span>
</div>
<br>
<div class="menu" style="width: 100%">
<img style="width: 200px;" id="sample-preview" src="{self.static_url}/nothing.png" alt="">
"""]
        for nr, group in enumerate(self.groups):
            result.append(f'''
<h3 id="h-{nr}"
    data-id="{nr}"
    data-thumbnail="{self.static_url}/samples/{group.thumbnail}"
    role="button"
    aria-expanded="false"
    class="toggle thumbnail open"
    tabindex="0"
>
    {_(group.title)}
</h3>
  <div id="{nr}">\n   <ul>\n''')
            for box in group.generators:
                name = box.__name__
                docs = ""
                if box.__doc__:
                    docs = " - " + _(box.__doc__)
                result.append(f"""     <li class="thumbnail" data-thumbnail="{self.static_url}/samples/{name}-thumb.jpg" id="search_id_{name}"><a href="{name}{langparam}">{_(name)}</a>{docs}</li>\n""")
            result.append("   </ul>\n  </div>\n")
        result.append(f"""
</div>

<div style="width: 5%; float: left;"></div>
<div class="clear"></div>
<hr>
</div>
</div>
</body>
</html>
""")
        return (s.encode("utf-8") for s in result)

    def genHTMLStart(self, lang) -> str:
        lang_attr = lang.info().get("language", "")

        if lang_attr != "":
            return f"""<!DOCTYPE html><html lang="{lang_attr.replace('_', '-')}">"""

        return "<!DOCTYPE html><html>"

    def genHTMLMeta(self) -> str:
        return f'''
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" type="image/svg+xml" href="{self.static_url}/boxes-logo.svg" sizes="any">
    <link rel="icon" type="image/x-icon" href="{self.static_url}/favicon.ico">
'''

    def genHTMLMetaLanguageLink(self) -> str:
        """Generates meta language list for search engines."""
        languages = self.getLanguages()

        s = ""
        for language in languages:
            s += f'    <link rel="alternate" hreflang="{language.replace("_", "-")}" href="https://boxes.hackerspace-bamberg.de/?language={language}">\n'
        return s

    def genHTMLCSS(self) -> str:
        return f'<link rel="stylesheet" href="{self.static_url}/self.css">'

    def genHTMLJS(self) -> str:
        return f'<script src="{self.static_url}/self.js"></script>'

    def genHTMLLanguageSelection(self, lang) -> str:
        """Generates a dropdown selection for the language change."""
        current_language = lang.info().get('language', '')
        languages = self.getLanguages()

        if len(languages) < 2:
            return "<!-- No other languages to select found. -->"

        html_option = ""
        for language in languages:
            html_option += f"\t\t\t\t<option value='{language}'{' selected' if language == current_language else ''}>{language}</option>\n"

        return """
        <form>
            <select name="language" onchange='if(this.value != \"""" + current_language + """\") { this.form.submit(); }'>
""" + html_option + """
            </select>
        </form>
"""

    def genPagePartHeader(self, lang) -> str:
        _ = lang.gettext
        lang_name = lang.info().get('language', None)

        langparam = ""
        if lang_name:
            langparam = "?language=" + lang_name

        return f"""
<h1><a href="./{langparam}">{_("Boxes.py")}</a></h1>
<p>{_("Create boxes and more with a laser cutter!")}</p>
<p>
{_('''
        <a href="https://hackaday.io/project/10649-boxespy">Boxes.py</a> is an <a href="https://www.gnu.org/licenses/gpl-3.0.en.html">Open Source</a> box generator written in <a href="https://www.python.org/">Python</a>. It features both finished parametrized generators as well as a Python API for writing your own. It features finger and (flat) dovetail joints, flex cuts, holes and slots for screws, hinges, gears, pulleys and much more.''')}
</p>
</div>

<div style="width: 25%; float: left;">
<img alt="self-Logo" src="{self.static_url}/boxes-logo.svg" width="250">
</div>

<div>

<div class="clear"></div>
<hr/>
<div class="linkbar">
<ul>
{self.genLinks(lang)}
  <li class="right">\U0001f50d <input autocomplete="off" type="search" oninput="filterSearchItems();" name="search" id="search" placeholder="Search"></li>
</ul>
</div>
<hr/>
"""

    def genLinks(self, lang, preview=False):
        _ = lang.gettext
        links = [("https://florianfesti.github.io/boxes/html/usermanual.html", _("Help")),
                 ("https://hackaday.io/project/10649-boxespy", _("Home Page")),
                 ("https://florianfesti.github.io/boxes/html/index.html", _("Documentation")),
                 ("https://github.com/florianfesti/boxes", _("Sources"))]
        if self.legal_url:
            links.append((self.legal_url, _("Legal")))
        links.append(("https://florianfesti.github.io/boxes/html/give_back.html", _("Give Back")))

        result = [f'  <li><a href="{url}" target="_blank" rel="noopener">{txt}</a></li>\n' for url, txt in links]

        if preview:
            result.append(f'    <li class="right">{_("Preview")} <input id="preview_chk" type="checkbox" checked="checked"> </li>\n')

        result.append(f'  <li class="right">{self.genHTMLLanguageSelection(lang)}  </li>\n')
        return "".join(result)

    def genPageError(self, name, e, lang) -> list[bytes]:
        """Generates a error page."""
        _ = lang.gettext

        h = f"""{self.genHTMLStart(lang)}
<head>
  <title>{_("Error generating %s") % _(name)}</title>
  {self.genHTMLMeta()}
  <meta name="robots" content="noindex">
</head>
<body>
<h1>{_("An error occurred!")}</h1>
"""
        for s in str(e).split("\n"):
            h += f"<p>{html.escape(s)}</p>\n"
        h += "</body></html>"
        return [h.encode("utf-8")]

    def genPageErrorSVG(self, name, e, lang) -> list[bytes]:
        """Generates a error page."""
        _ = lang.gettext

        box = boxes.Boxes()
        box.parseArgs(["--reference=0.0"])
        box.open()
        box.text(_("An error occurred!"))
        box.text(str(e), y=-20, fontsize=7)
        return box.close()

    def serveStatic(self, environ, start_response):
        filename = environ["PATH_INFO"][len("/static/"):]
        path = os.path.join(self.staticdir, filename)
        if (not re.match(r"[a-zA-Z0-9_/-]+\.[a-zA-Z0-9]+", filename) or
                not os.path.exists(path)):
            if re.match(r"samples/.*-thumb.jpg", filename):
                path = os.path.join(self.staticdir, "nothing.png")
            else:
                start_response("404 Not Found", [('Content-type', 'text/plain')])
                return [b"Not found"]

        type_, encoding = mimetypes.guess_type(filename)
        if encoding is None:
            encoding = "utf-8"

        # Images do not have charset. Just bytes. Except text based svg.
        # Todo: fallback if type_ is None?
        if type_ is not None and "image" in type_ and type_ != "image/svg+xml":
            start_response("200 OK", [('Content-type', "%s" % type_)])
        else:
            start_response("200 OK", [('Content-type', f"{type_}; charset={encoding}")])

        f = open(path, 'rb')
        return environ['wsgi.file_wrapper'](f, 512 * 1024)

    def getURL(self, environ) -> str:
        url = environ['wsgi.url_scheme'] + '://'

        if environ.get('HTTP_HOST'):
            url += environ['HTTP_HOST']
        else:
            url += environ['SERVER_NAME']

            if environ['wsgi.url_scheme'] == 'https':
                if environ['SERVER_PORT'] != '443':
                    url += ':' + environ['SERVER_PORT']
                else:
                    if environ['SERVER_PORT'] != '80':
                        url += ':' + environ['SERVER_PORT']
        url += quote(self.url_prefix)
        url += quote(environ.get('SCRIPT_NAME', ''))
        url += quote(environ.get('PATH_INFO', ''))
        if environ.get('QUERY_STRING'):
            url += '?' + environ['QUERY_STRING']

        return url

    def serveGallery(self, environ, start_response, lang):
        _ = lang.gettext
        lang_name = lang.info().get('language', None)

        start_response("200 OK", [('Content-type', "text/html; charset=utf-8")])

        if ("Gallery", lang_name) in self._cache:
            return self._cache[("Gallery", lang_name)]

        langparam = ""
        if lang_name:
            langparam = "?language=" + lang_name

        result = [f"""
{self.genHTMLStart(lang)}
<head>
    <title>{_("Gallery")} - {_("Boxes.py")}</title>
    {self.genHTMLMeta()}
{self.genHTMLMetaLanguageLink()}
    {self.genHTMLCSS()}
    {self.genHTMLJS()}
</head>
<body onload="initPage()">
<div class="container">
<div style="width: 75%; float: left;">
{self.genPagePartHeader(lang)}
<div class="modenav">
<span class="modebutton modeactive">{_("Gallery")}</span>
<span class="modebutton"><a href="Menu">{_("Menu")}</a></span>
</div>
"""]
        for nr, group in enumerate(self.groups):
            result.append(f"<h2>{_(group.title)}</h2>\n")
            for box in group.generators:
                name = box.__name__
                fn = f"samples/{name}-thumb.jpg"
                thumbnail = f"{self.static_url}/{fn}"
                static_filename = os.path.join(self.staticdir, fn)
                alt = f"{_(name)}"
                href = f"{name}{langparam}"
                if not os.path.exists(static_filename):
                    result.append(f"""  <span class="gallery_missing" id="search_id_{name}"><a href="{href}">{_(box.__doc__)}<br><br>{_(name)}</a></span>\n""")
                else:
                    result.append(f"""  <span class="gallery" id="search_id_{name}"><a title="{_(name)} - {html.escape(_(box.__doc__))}" href="{href}"><img alt="{alt}" src="{thumbnail}"><br>{_(name)}</a></span>\n""")

        result.append(f"""
</div><div style="width: 5%; float: left;"></div>
        <div class="clear"></div><hr></div>
</body>
</html>
"""
                      )
        self._cache[("Gallery", lang_name)] = [s.encode("utf-8") for s in result]
        return self._cache[("Gallery", lang_name)]

    def serve(self, environ, start_response):
        # serve favicon from static for generated SVGs
        if environ["PATH_INFO"] == "favicon.ico":
            environ["PATH_INFO"] = "/static/favicon.ico"
        if environ["PATH_INFO"].startswith("/static/"):
            return self.serveStatic(environ, start_response)

        status = '200 OK'
        headers = [('Content-type', 'text/html; charset=utf-8'), ('X-XSS-Protection', '1; mode=block'), ('X-Content-Type-Options', 'nosniff'), ('x-frame-options', 'SAMEORIGIN'), ('Referrer-Policy', 'no-referrer')]

        name = environ["PATH_INFO"][1:]
        args = [unquote_plus(arg) for arg in environ.get('QUERY_STRING', '').split("&")]
        render = "0"
        for arg in args:
            if arg.startswith("render="):
                render = arg[len("render="):]

        if not self.legal_url:
            if (environ.get('HTTP_HOST', '') == "boxes.hackerspace-bamberg.de" or
                environ.get('SERVER_NAME', '') == "boxes.hackerspace-bamberg.de"):
                self.legal_url = "https://www.hackerspace-bamberg.de/Datenschutz"

        lang = self.getLanguage(args, environ.get("HTTP_ACCEPT_LANGUAGE", ""))
        _ = lang.gettext

        if not name or name == "Gallery":
            return self.serveGallery(environ, start_response, lang)

        box_cls = self.boxes.get(name, None)
        if not box_cls:
            start_response(status, headers)

            lang_name = lang.info().get('language', None)
            if lang_name not in self._cache:
                self._cache[lang_name] = list(self.genPageMenu(lang))
            return self._cache[lang_name]

        box = box_cls()

        box.translations = lang

        if render == "0":
            defaults = {}
            for a in args:
                kv = a.split('=')
                if len(kv) == 2:
                    k, v = kv
                    defaults[k] = html.escape(v, True)
            start_response(status, headers)
            return self.args2html_cached(name, box, lang, "./" + name, defaults=defaults)

        args = ["--" + arg for arg in args if not arg.startswith("render=")]
        try:
            box.parseArgs(args)
        except ArgumentParserError as e:
            if render == "4":
                start_response(status, box.formats.http_headers["svg"])
                return self.genPageErrorSVG(name, e, lang)
            else:
                start_response(status, headers)
                return self.genPageError(name, e, lang)

        try:
            box.metadata["url"] = self.getURL(environ)
            box.metadata["url_short"] = filter_url(box.metadata["url"],
                                                   box.non_default_args)
            box.open()
            box.render()
            data = box.close()
        except Exception as e:
            if not isinstance(e, ValueError):
                print("Exception during rendering:")
                traceback.print_exc()
            start_response("500 Internal Server Error", headers)
            return self.genPageError(name, e, lang)

        http_headers = box.formats.http_headers.get(box.format, [('Content-type', 'application/unknown; charset=utf-8')])[:]
        # Prevent crawlers.
        http_headers.append(('X-Robots-Tag', 'noindex,nofollow'))

        if render == "3":
            http_headers = [('Content-type', 'image/png')]
            http_headers.append(('X-Robots-Tag', 'noindex,nofollow'))
            qr_format = "png"
            fn = box.__class__.__name__
            start_response(status, http_headers)
            qrcode = get_qrcode(box.metadata["url_short"], qr_format)
            return (qrcode,)

        if box.format != "svg" or render == "2":
            extension = box.format
            if extension == "svg_Ponoko":
                extension = "svg"
            http_headers.append(('Content-Disposition', f'attachment; filename="{box.__class__.__name__}.{extension}"'))
        start_response(status, http_headers)
        return environ['wsgi.file_wrapper'](data, 512 * 1024)


def get_qrcode(url, format):
    if url is None:
        url = "no url"
    img = qrcode.make(url)
    image_bytes = io.BytesIO()
    img.save(image_bytes, format=format)
    return image_bytes.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--host", default="")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--url_prefix", default="",
                        help="URL path to Boxes.py instance")
    parser.add_argument("--static_url", default="static",
                        help="URL of static content")
    parser.add_argument("--static_path", default="../static/",
                        help="location of static content on disk")
    parser.add_argument("--legal_url", default="",
                        help="URL of legal web page")
    args = parser.parse_args()

    boxserver = BServer(url_prefix=args.url_prefix, static_url=args.static_url,
                        static_path=args.static_path)

    fc = FileChecker()
    fc.start()

    httpd = make_server(args.host, args.port, boxserver.serve)
    print(f"BoxesServer serving on {args.host}:{args.port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        fc.stop()
    httpd.server_close()
    print("BoxesServer stops.")


if __name__ == "__main__":
    main()
else:
    boxserver = BServer(static_url="https://florianfesti.github.io/boxes/static")
    application = boxserver.serve
