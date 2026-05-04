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
import inspect
import io
import mimetypes
import os.path
import re
import sys
import threading
import time
import traceback
from pathlib import Path
from typing import Any, NoReturn
from urllib.parse import quote, unquote_plus
from wsgiref.simple_server import make_server

import qrcode

try:
    import boxes.generators
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../.."))
    import boxes.generators
import boxes

from boxes.scripts.ui_legacy import LegacyUIMixin
from boxes.scripts.ui_menu import MenuUIMixin
from boxes.scripts.ui_gallery import GalleryUIMixin
from boxes.scripts.ui_touch import TouchUIMixin
from boxes.scripts.pages.colors import ColorsUIMixin
from boxes.scripts.pages.categories import CategoriesUIMixin
from boxes.scripts.pages.generator import GeneratorUIMixin
from boxes.scripts.pages.machine import MachineUIMixin


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
                os.execl(sys.executable, "python", __file__, *sys.argv[1:])
            time.sleep(1)

    def stop(self) -> None:
        self._stopped = True


def filter_url(url: str, non_default_args: Any) -> str:
    if len(url) == 0:
        return ""
    try:
        base, args_str = url.split("?")
    except ValueError:
        return ""
    new_args = []
    args_to_ignore = {"qr_code", "format"}
    for arg in args_str.split("&"):
        a, *_ = arg.split("=")
        if a.strip() in args_to_ignore:
            continue
        if a in non_default_args:
            new_args.append(arg)
    return f"{base}?{'&'.join(new_args)}" if new_args else base


class ArgumentParserError(Exception):
    pass


class ThrowingArgumentParser(boxes.args.BoxesArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise ArgumentParserError(message)


# Evil hack
boxes.ArgumentParser = ThrowingArgumentParser  # type: ignore


class BServer(LegacyUIMixin, MenuUIMixin, GalleryUIMixin, TouchUIMixin, ColorsUIMixin, CategoriesUIMixin, GeneratorUIMixin, MachineUIMixin):
    """WSGI application that serves the Boxes.py web UI.

    HTML rendering is split across mixins:

    * :mod:`boxes.scripts.ui_legacy`          – classic desktop/browser interface
    * :mod:`boxes.scripts.ui_touch`           – tablet-optimised tabbed interface
    * :mod:`boxes.scripts.pages.settings`     – /settings color page
    * :mod:`boxes.scripts.pages.categories`   – /categories page

    The active interface is controlled by the ``--ui-mode`` CLI flag
    (``legacy`` | ``touch`` | ``auto``, default ``legacy``) or the
    ``BOXES_UI_MODE`` environment variable.
    """

    lang_re = re.compile(r"([a-z]{2,3}(-[-a-zA-Z0-9]*)?)\s*(;\s*q=(\d\.?\d*))?")

    # Special tags: tag → (emoji, tooltip)
    SPECIAL_TAGS: dict[str, tuple[str, str]] = {
        "unstable": ("⚠", "Unstable – may not work correctly"),
        "wip": ("🚧", "Work in progress"),
        "new": ("✨", "New generator"),
    }

    @staticmethod
    def tag_badges_html(box: type) -> str:
        """Return HTML badge span(s) for every tag declared on *box*."""
        tags: list[str] = getattr(box, "tags", [])
        if not tags:
            return ""
        parts: list[str] = []
        for tag in tags:
            if tag in BServer.SPECIAL_TAGS:
                icon, tip = BServer.SPECIAL_TAGS[tag]
                parts.append(
                    f'<span class="tag-badge tag-{html.escape(tag)}" title="{html.escape(tip)}">'
                    f"{icon}</span>"
                )
            else:
                parts.append(f'<span class="tag-badge">{html.escape(tag)}</span>')
        return " " + "".join(parts)

    def __init__(
        self,
        url_prefix: str = "",
        static_url: str = "static",
        static_path: str = "../static/",
        legal_url: str = "",
        deploy_fingerprint: str = "",
        ui_mode: str = "legacy",
    ) -> None:
        self.boxes = {
            b.__name__: b
            for b in boxes.generators.getAllBoxGenerators().values()
            if b.webinterface
        }
        self.groups = boxes.generators.ui_groups
        self.groups_by_name = boxes.generators.ui_groups_by_name

        for name, box in self.boxes.items():
            box.UI = "web"
            self.groups_by_name.get(box.ui_group, self.groups_by_name["Misc"]).add(box)

        # Build map: "ClassName.jpg" / "ClassName-thumb.jpg" → Path next to generator
        self._samples_map: dict[str, Path] = {}
        for cls_name, cls in self.boxes.items():
            try:
                gen_file = Path(inspect.getfile(cls))
            except TypeError:
                continue
            # New layout: source is xxx/__init__.py → images use the folder name
            if gen_file.name == "__init__.py":
                stem = gen_file.parent.name
                folder = gen_file.parent
            else:
                stem = gen_file.stem
                folder = gen_file.parent
            self._samples_map[f"{cls_name}.jpg"] = folder / f"{stem}.jpg"
            self._samples_map[f"{cls_name}-thumb.jpg"] = folder / f"{stem}-thumb.jpg"

        if os.path.isabs(static_path):
            self.staticdir = static_path
        else:
            self.staticdir = os.path.join(os.path.dirname(__file__), "../static/")
            if not os.path.isdir(self.staticdir):
                self.staticdir = os.path.join(
                    os.path.dirname(__file__), "..", "../static/"
                )

        self._languages: list[str] | None = None
        self._cache: dict[Any, Any] = {}
        self.url_prefix = url_prefix
        self.static_url = static_url
        self.legal_url = legal_url
        self.deploy_fingerprint = deploy_fingerprint
        self.ui_mode = ui_mode  # "legacy" | "touch" | "auto"

    #  Language helpers

    def getLanguages(self, domain: str | None = None, localedir: str | None = None) -> list[str]:
        if self._languages is not None:
            return self._languages
        self._languages = []
        domain = "boxes.py"
        for localedir in ["locale", gettext._default_localedir]:  # type: ignore[attr-defined]
            files = glob.glob(
                os.path.join(localedir, "*", "LC_MESSAGES", f"{domain}.mo")
            )
            self._languages.extend([f.split(os.path.sep)[-3] for f in files])
        self._languages.sort()
        return self._languages

    def getLanguage(self, args: list[str], accept_language: str) -> Any:
        lang = None
        langs: list[tuple[float, str]] = []

        for i, arg in enumerate(args):
            if arg.startswith("language="):
                lang = arg[len("language="):]
                del args[i]
                break
        # Ignore the literal string "None" that legacy forms could emit
        # when lang_name was Python None and got rendered into the hidden input.
        if lang == "None":
            lang = None
        if lang:
            for localedir in ["locale", None]:
                try:
                    kw: dict[str, Any] = {"languages": [lang]}
                    if localedir:
                        kw["localedir"] = localedir
                    return gettext.translation("boxes.py", **kw)
                except OSError:
                    pass

        for l in accept_language.split(","):
            m = self.lang_re.match(l.strip())
            if m:
                langs.append((float(m.group(4) or 1.0), m.group(1)))
        langs.sort(reverse=True)
        lang_list = [l[1].replace("-", "_") for l in langs]
        try:
            return gettext.translation("boxes.py", localedir="locale", languages=lang_list)
        except OSError:
            return gettext.translation("boxes.py", languages=lang_list, fallback=True)

    #  Static file serving

    def serveStatic(self, environ: dict, start_response: Any) -> Any:
        filename = environ["PATH_INFO"][len("/static/"):]

        if filename.startswith("samples/"):
            basename = filename[len("samples/"):]
            gen_path = self._samples_map.get(basename)
            if gen_path is not None and gen_path.exists():
                path = str(gen_path)
            else:
                path = os.path.join(self.staticdir, filename)
                if not os.path.exists(path):
                    if basename.endswith("-thumb.jpg"):
                        path = os.path.join(self.staticdir, "needs-image.png")
                    else:
                        start_response("404 Not Found", [("Content-type", "text/plain")])
                        return [b"Not found"]
        else:
            if not re.match(r"[a-zA-Z0-9_/-]+\.[a-zA-Z0-9]+", filename) or not os.path.exists(
                os.path.join(self.staticdir, filename)
            ):
                start_response("404 Not Found", [("Content-type", "text/plain")])
                return [b"Not found"]
            path = os.path.join(self.staticdir, filename)

        type_, encoding = mimetypes.guess_type(filename)
        if encoding is None:
            encoding = "utf-8"
        if type_ is not None and "image" in type_ and type_ != "image/svg+xml":
            start_response("200 OK", [("Content-type", type_)])
        else:
            start_response("200 OK", [("Content-type", f"{type_}; charset={encoding}")])
        return environ["wsgi.file_wrapper"](open(path, "rb"), 512 * 1024)

    def getURL(self, environ: dict) -> str:
        url = environ["wsgi.url_scheme"] + "://"
        if environ.get("HTTP_HOST"):
            url += environ["HTTP_HOST"]
        else:
            url += environ["SERVER_NAME"]
            scheme = environ["wsgi.url_scheme"]
            port = environ["SERVER_PORT"]
            if (scheme == "https" and port != "443") or (scheme == "http" and port != "80"):
                url += ":" + port
        url += quote(self.url_prefix)
        url += quote(environ.get("SCRIPT_NAME", ""))
        url += quote(environ.get("PATH_INFO", ""))
        if environ.get("QUERY_STRING"):
            url += "?" + environ["QUERY_STRING"]
        return url

    def serveFonts(self, environ: dict, start_response: Any) -> Any:
        """Serve font files from the boxes Python package fonts directory.

        fonts.css uses relative paths ``../boxes/fonts/…`` which browsers
        resolve as ``/boxes/fonts/…``.  This handler maps those requests to
        the actual ``boxes/fonts/`` directory inside the package.
        """
        rel = environ["PATH_INFO"][len("/boxes/fonts/"):]
        # Safety: no path traversal
        if not re.match(r"[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+$", rel):
            start_response("404 Not Found", [("Content-type", "text/plain")])
            return [b"Not found"]
        fonts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fonts")
        path = os.path.join(fonts_dir, rel)
        if not os.path.isfile(path):
            start_response("404 Not Found", [("Content-type", "text/plain")])
            return [b"Not found"]
        type_, encoding = mimetypes.guess_type(rel)
        ct = type_ or "application/octet-stream"
        start_response("200 OK", [
            ("Content-type", ct),
            ("Cache-Control", "public, max-age=86400"),
        ])
        return environ["wsgi.file_wrapper"](open(path, "rb"), 512 * 1024)

    #  Main WSGI dispatcher

    def serve(self, environ: dict, start_response: Any) -> Any:
        if environ["PATH_INFO"] == "favicon.ico":
            environ["PATH_INFO"] = "/static/favicon.ico"
        if environ["PATH_INFO"].startswith("/static/"):
            return self.serveStatic(environ, start_response)
        # fonts.css references ../boxes/fonts/… which browsers resolve as /boxes/fonts/…
        if environ["PATH_INFO"].startswith("/boxes/fonts/"):
            return self.serveFonts(environ, start_response)

        status = "200 OK"
        headers = [
            ("Content-type", "text/html; charset=utf-8"),
            ("X-XSS-Protection", "1; mode=block"),
            ("X-Content-Type-Options", "nosniff"),
            ("x-frame-options", "SAMEORIGIN"),
            ("Referrer-Policy", "no-referrer"),
        ]

        name = environ["PATH_INFO"][1:]
        args = [unquote_plus(arg) for arg in environ.get("QUERY_STRING", "").split("&")]
        render = "0"
        for arg in args:
            if arg.startswith("render="):
                render = arg[len("render="):]

        if not self.legal_url:
            host = environ.get("HTTP_HOST", "") or environ.get("SERVER_NAME", "")
            if host == "boxes.hackerspace-bamberg.de":
                self.legal_url = "https://www.hackerspace-bamberg.de/Datenschutz"

        lang = self.getLanguage(args, environ.get("HTTP_ACCEPT_LANGUAGE", ""))

        #  Route: hub / gallery
        if not name:
            return self.serveTouchHub(environ, start_response, lang)

        if name == "Gallery":
            return self.serveGallery(environ, start_response, lang)

        if name == "TouchHub":
            return self.serveTouchHub(environ, start_response, lang)

        if name == "colors":
            return self.serveColors(environ, start_response, lang)

        if name == "machine":
            return self.serveMachine(environ, start_response, lang)

        if name == "categories":
            return self.serveCategorySettings(environ, start_response, lang)

        #  Route: unknown name → legacy menu
        box_cls = self.boxes.get(name, None)
        if not box_cls:
            start_response(status, headers)
            lang_name = lang.info().get("language", None)
            if lang_name not in self._cache:
                self._cache[lang_name] = list(self.genPageMenu(lang))
            return self._cache[lang_name]

        #  Route: generator page
        box = box_cls()
        box.translations = lang

        if render == "0":
            defaults: dict[str, str] = {}
            for a in args:
                kv = a.split("=")
                if len(kv) == 2:
                    k, v = kv
                    defaults[k] = html.escape(v, True)
            start_response(status, headers)
            lang_name = lang.info().get("language", None)
            langparam = f"?language={lang_name}" if lang_name else ""
            referer = environ.get("HTTP_REFERER", "")
            if "Gallery" in referer:
                back_url = f"Gallery{langparam}"
            elif "/categories" in referer:
                back_url = f"categories{langparam}"
            else:
                back_url = f"TouchHub{langparam}"
            return self.genTouchArgs(name, box, lang, "./" + name, defaults=defaults, back_url=back_url)

        #  Render / download / QR
        args = [
            "--" + arg
            for arg in args
            if not arg.startswith("render=") and not arg.startswith("color_")
        ]
        raw_args_full = [unquote_plus(a) for a in environ.get("QUERY_STRING", "").split("&")]
        color_overrides: dict[str, str] = {}
        for arg in raw_args_full:
            if arg.startswith("color_"):
                role, _, hex_val = arg[len("color_"):].partition("=")
                role = role.upper()
                if role and hex_val:
                    color_overrides[role] = hex_val

        try:
            box.parseArgs(args)
        except ArgumentParserError as e:
            if render == "4":
                start_response(status, box.formats.http_headers["svg"])
                return self.genPageErrorSVG(name, e, lang)
            start_response(status, headers)
            return self.genPageError(name, e, lang)

        try:
            box.metadata["url"] = self.getURL(environ)
            box.metadata["url_short"] = filter_url(
                str(box.metadata["url"]), box.non_default_args
            )
            box.open()
            from boxes.Color import Color as _Color

            _saved_colors = {role: list(getattr(_Color, role)) for role in _Color.ROLE_LABELS}
            if color_overrides:
                _Color.apply_overrides(color_overrides)
            try:
                box.render()
            finally:
                for role, val in _saved_colors.items():
                    setattr(_Color, role, val)
            data = box.close()
        except Exception as e:
            if not isinstance(e, ValueError):
                print("Exception during rendering:")
                traceback.print_exc()
            if render == "4" and isinstance(e, ValueError):
                start_response(status, box.formats.http_headers["svg"])
                return self.genPageErrorSVG(name, e, lang)
            start_response("500 Internal Server Error", headers)
            return self.genPageError(name, e, lang)

        box_format: str = getattr(box, "format", "svg")
        http_headers = box.formats.http_headers.get(
            box_format, [("Content-type", "application/unknown; charset=utf-8")]
        )[:]
        http_headers.append(("X-Robots-Tag", "noindex,nofollow"))

        if render == "3":
            start_response(status, [("Content-type", "image/png"), ("X-Robots-Tag", "noindex,nofollow")])
            return (get_qrcode(str(box.metadata.get("url_short", "")), "png"),)

        if box_format != "svg" or render == "2":
            ext = box_format if box_format != "svg_Ponoko" else "svg"
            http_headers.append(
                ("Content-Disposition", f'attachment; filename="{box.__class__.__name__}.{ext}"')
            )
        start_response(status, http_headers)
        return environ["wsgi.file_wrapper"](data, 512 * 1024)


def get_qrcode(url: str, format: str) -> bytes:
    img = qrcode.make(url or "no url")
    image_bytes = io.BytesIO()
    img.save(image_bytes, format=format)
    return image_bytes.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--url_prefix", default="", help="URL path to Boxes.py instance")
    parser.add_argument("--static_url", default="static", help="URL of static content")
    parser.add_argument("--static_path", default="../static/", help="location of static content on disk")
    parser.add_argument("--legal_url", default="", help="URL of legal web page")
    parser.add_argument(
        "--ui-mode",
        dest="ui_mode",
        default=os.environ.get("BOXES_UI_MODE", "legacy"),
        choices=["legacy", "touch", "auto"],
        help="UI mode: legacy (default), touch (tablet), auto",
    )
    args = parser.parse_args()

    boxserver = BServer(
        url_prefix=args.url_prefix,
        static_url=args.static_url,
        static_path=args.static_path,
        deploy_fingerprint=os.environ.get("BOXES_DEPLOY_FINGERPRINT", ""),
        ui_mode=args.ui_mode,
    )

    fc = FileChecker()
    fc.start()

    httpd = make_server(args.host, args.port, boxserver.serve)
    print(f"BoxesServer serving on http://{args.host if args.host else '*'}:{args.port}/...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        fc.stop()
    httpd.server_close()
    print("BoxesServer stops.")


if __name__ == "__main__":
    main()
else:
    static_url = os.environ.get("STATIC_URL", "https://florianfesti.github.io/boxes/static")
    boxserver = BServer(
        static_url=static_url,
        deploy_fingerprint=os.environ.get("BOXES_DEPLOY_FINGERPRINT", ""),
        ui_mode=os.environ.get("BOXES_UI_MODE", "legacy"),
    )
    application = boxserver.serve
