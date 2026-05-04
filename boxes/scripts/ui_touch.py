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
import html

from boxes.scripts.ui_shared import gen_interface_select_html


class TouchUIMixin:
    """HTML generation for the touch / tablet interface.

    Designed as a mixin for BServer.  All methods use ``self`` attributes
    set by BServer.__init__ (static_url, groups, _cache, …).
    """

    # Stubs for attributes provided by BServer
    static_url: str
    groups: list
    _cache: dict
    legal_url: str
    deploy_fingerprint: str

    # Shared helpers expected from LegacyUIMixin / BServer
    def genHTMLStart(self, lang: object) -> str:
        raise NotImplementedError

    def genHTMLMeta(self) -> str:
        raise NotImplementedError

    def genHTMLMetaLanguageLink(self) -> str:
        raise NotImplementedError

    def genHTMLCSS(self) -> str:
        raise NotImplementedError

    def genHTMLJS(self) -> str:
        raise NotImplementedError

    def genHTMLLanguageSelection(self, lang: object) -> str:
        raise NotImplementedError

    def tag_badges_html(self, box: type) -> str:
        raise NotImplementedError

    def arg2html(
        self,
        a: argparse.Action,
        prefix: str | None,
        defaults: dict | None = None,
        _=lambda s: s,
    ) -> str:
        raise NotImplementedError

    # Touch-specific assets

    def genHTMLTouchCSS(self) -> str:
        return f'<link rel="stylesheet" href="{self.static_url}/touch.css">'

    def genHTMLGeneratorCSS(self) -> str:
        return f'<link rel="stylesheet" href="{self.static_url}/generator.css">'

    def genHTMLCategoriesCSS(self) -> str:
        return f'<link rel="stylesheet" href="{self.static_url}/categories.css">'

    def genHTMLColorsCSS(self) -> str:
        return f'<link rel="stylesheet" href="{self.static_url}/colors.css">'

    def genHTMLMachineCSS(self) -> str:
        return f'<link rel="stylesheet" href="{self.static_url}/machine.css">'

    def genHTMLTouchJS(self) -> str:
        return f'<script src="{self.static_url}/touch.js"></script>'

    # Shared header bar

    def _touch_header_html(self, lang: object, back_url: str = "", back_icon_only: bool = False, center_html: str = "") -> str:
        """Sticky header bar rendered on every touch page."""
        _ = lang.gettext  # type: ignore[attr-defined]
        lang_name = lang.info().get("language", None)  # type: ignore[attr-defined]
        langparam = f"?language={lang_name}" if lang_name else ""

        if back_url:
            if back_icon_only:
                back_btn = (
                    f'<a class="th-mode-btn th-back-icon" href="{html.escape(back_url)}" '
                    + 'aria-label="Back">&#8592;</a>'
                )
            else:
                back_btn = (
                    f'<a class="th-mode-btn" href="{html.escape(back_url)}" '
                    + f'aria-label="Back">&#8592; {_("Back")}</a>'
                )
        else:
            back_btn = ""

        center_section = f'<div class="th-header-center">{center_html}</div>' if center_html else ""

        # Build the â˜° dropdown menu (mirrors legacy genLinks dropdown)
        links: list[tuple[str, str]] = [
            ("https://florianfesti.github.io/boxes/html/usermanual.html", _("Help")),
            ("https://hackaday.io/project/10649-boxespy", _("Home Page")),
            ("https://florianfesti.github.io/boxes/html/index.html", _("Documentation")),
            ("https://github.com/florianfesti/boxes", _("Sources")),
        ]
        if self.legal_url:
            links.append((self.legal_url, _("Legal")))
        links.append(("https://florianfesti.github.io/boxes/html/give_back.html", _("Give Back")))

        dropdown_items: list[str] = [
            f'      <a href="{html.escape(url)}" target="_blank" rel="noopener">{txt}</a>'
            for url, txt in links
        ]
        # Interface switcher (Touch is always the current interface here)
        dropdown_items.append("      " + gen_interface_select_html("TouchHub", _))
        dropdown_items.append(f'      <a href="colors">\U0001f3a8 {_("Colors")}</a>')
        dropdown_items.append(f'      <a href="machine">\u2699 {_("Machine")}</a>')
        dropdown_items.append(f'      <a href="categories">\U0001f4c2 {_("Categories")}</a>')
        # Language selection inside the dropdown
        lang_sel = self.genHTMLLanguageSelection(lang)
        if "select" in lang_sel:
            dropdown_items.append(
                f'      <div class="dropdown-lang">\U0001f310 {_("Language:")} {lang_sel}</div>'
            )
        if self.deploy_fingerprint:
            tag = html.escape(self.deploy_fingerprint)
            dropdown_items.append(
                f'      <span style="padding:6px 12px;color:#aaa;font-size:0.8em;">Instance: {tag}</span>'
            )

        dropdown_html = "\n".join(dropdown_items)

        return f"""
  <header class="th-header">
    <a class="th-logo" href="TouchHub{langparam}">
      <img src="{self.static_url}/boxes-logo.svg" alt="Boxes.py" height="40">
      <span class="th-logo-text">{_("Boxes.py")}</span>
    </a>
    {center_section}
    <div class="th-header-actions">
      {back_btn}
      {f'<a class="th-mode-btn th-back-icon" href="TouchHub{langparam}" aria-label="Home">&#127968;</a>' if back_url else ""}
      <div class="dropdown th-dropdown">
        <button class="th-mode-btn th-back-icon dropdown-btn" onclick="toggleDropdown(event)" aria-label="Menu">&#9776;</button>
        <div class="dropdown-content th-dropdown-content" id="main-dropdown">
{dropdown_html}
        </div>
      </div>
    </div>
  </header>"""

    # Hub page

    def genTouchHub(self, lang: object) -> list[bytes]:
        """Generate the full tabbed touch-mode hub page."""
        _ = lang.gettext  # type: ignore[attr-defined]
        lang_name = lang.info().get("language", None)  # type: ignore[attr-defined]
        langparam = f"?language={lang_name}" if lang_name else ""

        tabs_html: list[str] = []
        options_html: list[str] = []
        panels_html: list[str] = []

        for nr, group in enumerate(self.groups):
            gen_count = len(group.generators)
            is_first = nr == 0
            active_cls = "active" if is_first else ""
            tabs_html.append(
                f'<button class="th-tab {active_cls}" role="tab" '
                f'aria-selected="{str(is_first).lower()}" '
                f'data-group="{nr}" onclick="thSwitchTab({nr})" '
                f'title="{html.escape(_(group.title))}">'
                f'<span class="th-tab-label">{html.escape(_(group.title))}</span>'
                f'<span class="th-tab-count">{gen_count}</span>'
                f"</button>"
            )
            selected_attr = " selected" if is_first else ""
            options_html.append(
                f'<option value="{nr}"{selected_attr}>'
                f'{html.escape(_(group.title))} ({gen_count})'
                f"</option>"
            )

            cards: list[str] = []
            for box in group.generators:
                bname = box.__name__
                doc = html.escape(_(box.__doc__) if box.__doc__ else "")
                thumb = f"{self.static_url}/samples/{bname}-thumb.jpg"
                badges = self.tag_badges_html(box)
                href = f"{bname}{langparam}"
                cards.append(
                    f'<a class="th-card" href="{html.escape(href)}" '
                    f'id="tc_{bname}" title="{html.escape(_(bname))}">'
                    f'<img class="th-card-thumb" src="{thumb}" '
                    f'alt="{html.escape(_(bname))}" loading="lazy" '
                    f"onerror=\"this.outerHTML='<div class=&quot;th-card-thumb-missing&quot;>ðŸ“¦</div>'\">"
                    f'<div class="th-card-info">'
                    f'<span class="th-card-name">{html.escape(_(bname))}{badges}</span>'
                    f'<span class="th-card-doc">{doc}</span>'
                    f"</div></a>"
                )

            display = "block" if is_first else "none"
            panels_html.append(
                f'<div class="th-panel {active_cls}" data-group="{nr}" '
                f'id="th-panel-{nr}" role="tabpanel" style="display:{display}">'
                f'<div class="th-grid">{"".join(cards)}</div>'
                f"</div>"
            )

        page = f"""{self.genHTMLStart(lang)}
<head>
  <title>{_("Boxes.py")}</title>
  {self.genHTMLMeta()}
{self.genHTMLMetaLanguageLink()}
  {self.genHTMLCSS()}
  {self.genHTMLTouchCSS()}
  {self.genHTMLJS()}
  {self.genHTMLTouchJS()}
</head>
<body class="touch-hub" onload="initTouchHub()">

{self._touch_header_html(lang)}

  <nav class="th-tabbar" role="tablist" aria-label="{_("Generator categories")}">
    <select id="th-tab-select" onchange="thSwitchTab(this.value)">
      {"".join(options_html)}
    </select>
    {"".join(tabs_html)}
  </nav>

  <main class="th-content" id="th-content">
    {"".join(panels_html)}
  </main>

</body>
</html>"""
        return [page.encode("utf-8")]

    # WSGI handler

    def serveTouchHub(self, environ: object, start_response: object, lang: object) -> list[bytes]:
        """Serve the touch-mode category hub page (with caching)."""
        lang_name = lang.info().get("language", None)  # type: ignore[attr-defined]
        cache_key = ("TouchHub", lang_name)

        start_response("200 OK", [  # type: ignore[operator]
            ("Content-type", "text/html; charset=utf-8"),
            ("X-XSS-Protection", "1; mode=block"),
            ("X-Content-Type-Options", "nosniff"),
            ("x-frame-options", "SAMEORIGIN"),
            ("Referrer-Policy", "no-referrer"),
        ])

        if cache_key not in self._cache:
            self._cache[cache_key] = self.genTouchHub(lang)
        return self._cache[cache_key]
