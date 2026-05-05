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



class HomeTouchMixin:
    """HTML generation for the touch / tablet interface.

    Designed as a mixin for BServer.  All methods use ``self`` attributes
    set by BServer.__init__ (static_url, groups, _cache, ...).

    The hub page uses a persistent left sidebar for category navigation
    instead of the previous tab-bar + hamburger-dropdown layout.
    """

    # Stubs for attributes provided by BServer
    static_url: str
    groups: list
    _cache: dict
    legal_url: str
    deploy_fingerprint: str

    # Shared helpers expected from HomeLegacyMixin / BServer
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

    def _touch_header_html(
        self,
        lang: object,
        back_url: str = "",
        back_icon_only: bool = False,
        center_html: str = "",
        show_dropdown: bool = True,
    ) -> str:
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
                back_label = _("Back")
                back_btn = (
                    f'<a class="th-mode-btn" href="{html.escape(back_url)}" '
                    + f'aria-label="Back">&#8592; {back_label}</a>'
                )
        else:
            back_btn = ""

        center_section = f'<div class="th-header-center">{center_html}</div>' if center_html else ""

        # On sub-pages (non-hub) keep a compact dropdown for links
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
        dropdown_items.append('      <hr style="border:none;border-top:1px solid #e8e0d0;margin:4px 0">')
        dropdown_items.append(f'      <a href="TouchHub">\U0001f4f1 {_("Touch")}</a>')
        dropdown_items.append(f'      <a href="Gallery">\U0001f5bc\ufe0f {_("Gallery")}</a>')
        dropdown_items.append(f'      <a href="Menu">\U0001f4cb {_("Menu")}</a>')
        dropdown_items.append('      <hr style="border:none;border-top:1px solid #e8e0d0;margin:4px 0">')
        dropdown_items.append(f'      <a href="colors">\U0001f3a8 {_("Colors")}</a>')
        dropdown_items.append(f'      <a href="machine">\u2699 {_("Machine")}</a>')
        dropdown_items.append(f'      <a href="categories">\U0001f4c2 {_("Categories")}</a>')
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

        # sidebar-toggle is shown only on mobile via CSS (.th-sidebar-toggle)
        sidebar_toggle = (
            '<button class="th-mode-btn th-back-icon th-sidebar-toggle" '
            'onclick="thOpenSidebar()" aria-label="Menu">&#9776;</button>'
        )

        home_btn = (
            f'<a class="th-mode-btn th-back-icon" href="TouchHub{langparam}" aria-label="Home">&#127968;</a>'
            if back_url else ""
        )

        dropdown_block = ""
        if show_dropdown:
            dropdown_block = (
                '      <div class="dropdown th-dropdown">\n'
                '        <button class="th-mode-btn th-back-icon dropdown-btn" '
                'onclick="toggleDropdown(event)" aria-label="Menu">&#9776;</button>\n'
                '        <div class="dropdown-content th-dropdown-content" id="main-dropdown">\n'
                f"{dropdown_html}\n"
                "        </div>\n"
                "      </div>\n"
            )

        return (
            "\n  <header class=\"th-header\">\n"
            f"    {sidebar_toggle}\n"
            f'    <a class="th-logo" href="TouchHub{langparam}">\n'
            f'      <img src="{self.static_url}/boxes-logo.svg" alt="Boxes.py" height="40">\n'
            f'      <span class="th-logo-text">{_("Boxes.py")}</span>\n'
            "    </a>\n"
            f"    {center_section}\n"
            '    <div class="th-header-actions">\n'
            f"      {back_btn}\n"
            f"      {home_btn}\n"
            f"{dropdown_block}"
            "    </div>\n"
            "  </header>"
        )

    # Hub page

    def genTouchHub(self, lang: object) -> list[bytes]:
        """Generate the touch-mode hub page with a left sidebar for categories."""
        _ = lang.gettext  # type: ignore[attr-defined]
        lang_name = lang.info().get("language", None)  # type: ignore[attr-defined]
        langparam = f"?language={lang_name}" if lang_name else ""

        # ── Left sidebar: category nav items ────────────────────────────────
        sidebar_nav_items: list[str] = []
        panels_html: list[str] = []

        for nr, group in enumerate(self.groups):
            gen_count = len(group.generators)
            is_first = nr == 0
            active_cls = "active" if is_first else ""
            sidebar_nav_items.append(
                f'<button class="th-sidenav-item {active_cls}" role="tab" '
                f'aria-selected="{str(is_first).lower()}" '
                f'data-group="{nr}" onclick="thSwitchTab({nr})" '
                f'title="{html.escape(_(group.title))}">'
                f'<span class="th-sidenav-label">{html.escape(_(group.title))}</span>'
                f'<span class="th-sidenav-count">{gen_count}</span>'
                f"</button>"
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
                    "onerror=\"this.outerHTML='<div class=&quot;th-card-thumb-missing&quot;>&#128230;</div>'\">"
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

        # ── Left sidebar: footer links ───────────────────────────────────────
        links: list[tuple[str, str]] = [
            ("https://florianfesti.github.io/boxes/html/usermanual.html", _("Help")),
            ("https://hackaday.io/project/10649-boxespy", _("Home Page")),
            ("https://florianfesti.github.io/boxes/html/index.html", _("Documentation")),
            ("https://github.com/florianfesti/boxes", _("Sources")),
        ]
        if self.legal_url:
            links.append((self.legal_url, _("Legal")))
        links.append(("https://florianfesti.github.io/boxes/html/give_back.html", _("Give Back")))

        sidebar_links_html = "\n".join(
            f'    <a class="th-sidenav-link" href="{html.escape(url)}" target="_blank" rel="noopener">{txt}</a>'
            for url, txt in links
        )
        sidebar_links_html += (
            f'\n    <a class="th-sidenav-link" href="colors{langparam}">\U0001f3a8 {_("Colors")}</a>'
            f'\n    <a class="th-sidenav-link" href="machine{langparam}">\u2699\ufe0f {_("Machine")}</a>'
            f'\n    <a class="th-sidenav-link" href="categories{langparam}">\U0001f4c2 {_("Categories")}</a>'
        )
        sidebar_links_html += '\n    <hr class="th-sidenav-sep">'
        sidebar_links_html += (
            f'\n    <a class="th-sidenav-link" href="Gallery{langparam}">\U0001f5bc\ufe0f {_("Gallery")}</a>'
            f'\n    <a class="th-sidenav-link" href="Menu{langparam}">\U0001f4cb {_("Menu")}</a>'
        )
        lang_sel = self.genHTMLLanguageSelection(lang)
        if "select" in lang_sel:
            sidebar_links_html += '\n    <hr class="th-sidenav-sep">'
            sidebar_links_html += (
                f'\n    <div class="th-sidenav-lang">\U0001f310 {_("Language:")} {lang_sel}</div>'
            )
        if self.deploy_fingerprint:
            tag = html.escape(self.deploy_fingerprint)
            sidebar_links_html += (
                f'\n    <span class="th-sidenav-fingerprint">Instance: {tag}</span>'
            )

        sidebar_nav_html = "\n".join(sidebar_nav_items)
        header_html = self._touch_header_html(lang, show_dropdown=False)

        page = (
            f"{self.genHTMLStart(lang)}\n"
            "<head>\n"
            f"  <title>{_('Boxes.py')}</title>\n"
            f"  {self.genHTMLMeta()}\n"
            f"{self.genHTMLMetaLanguageLink()}"
            f"  {self.genHTMLCSS()}\n"
            f"  {self.genHTMLTouchCSS()}\n"
            f"  {self.genHTMLJS()}\n"
            f"  {self.genHTMLTouchJS()}\n"
            "</head>\n"
            f'<body class="touch-hub" onload="initTouchHub()">\n'
            f"\n{header_html}\n\n"
            '<div class="th-shell">\n\n'
            "  <!-- Left sidebar -->\n"
            f'  <nav class="th-sidebar" id="th-sidebar" role="navigation" aria-label="{_("Generator categories")}">\n'
            '    <div class="th-sidenav-categories" role="tablist">\n'
            f"{sidebar_nav_html}\n"
            "    </div>\n"
            '    <div class="th-sidenav-footer">\n'
            f"{sidebar_links_html}\n"
            "    </div>\n"
            "  </nav>\n\n"
            "  <!-- Mobile overlay to close sidebar -->\n"
            '  <div class="th-sidebar-overlay" id="th-sidebar-overlay" '
            'onclick="thCloseSidebar()" aria-hidden="true"></div>\n\n'
            "  <!-- Content area -->\n"
            '  <main class="th-content" id="th-content">\n'
            f'    {"".join(panels_html)}\n'
            "  </main>\n\n"
            "</div>\n\n"
            "</body>\n"
            "</html>"
        )
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
