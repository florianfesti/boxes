# Copyright (C) 2016-2017 Florian Festi
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
from __future__ import annotations
import html
class CategoriesUIMixin:
    """Mixin that renders the /categories (Categories) page in touch style."""
    static_url: str
    groups: list
    def genHTMLStart(self, lang: object) -> str:
        raise NotImplementedError
    def genHTMLMeta(self) -> str:
        raise NotImplementedError
    def genHTMLCSS(self) -> str:
        raise NotImplementedError
    def genHTMLJS(self) -> str:
        raise NotImplementedError
    def genHTMLTouchCSS(self) -> str:
        raise NotImplementedError
    def genHTMLCategoriesCSS(self) -> str:
        raise NotImplementedError
    def genHTMLTouchJS(self) -> str:
        raise NotImplementedError
    def _touch_header_html(self, lang: object, back_url: str = "", back_icon_only: bool = False) -> str:
        raise NotImplementedError
    def serveCategorySettings(self, environ: object, start_response: object, lang: object) -> list[bytes]:
        """Render the /categories page."""
        _ = lang.gettext  # type: ignore[attr-defined]
        lang_name = lang.info().get("language", None)  # type: ignore[attr-defined]
        langparam = f"?language={lang_name}" if lang_name else ""
        cards: list[str] = []
        for nr, group in enumerate(self.groups):
            gen_count = len(group.generators)
            first_thumb = (
                f"{self.static_url}/samples/{group.generators[0].__name__}-thumb.jpg"
                if group.generators else f"{self.static_url}/nothing.png"
            )
            cards.append(
                f'  <label class="cat-card" for="cat_{nr}" '
                f'style="background-image:url(\'{html.escape(first_thumb)}\')">\n'
                f'    <div class="cat-card-overlay">\n'
                f'      <input type="checkbox" id="cat_{nr}" data-cat-id="{nr}"\n'
                f'             onchange="onCategoryCheckboxChange(this)" checked>\n'
                f'      <span class="cat-card-title">{html.escape(_(group.title))}</span>\n'
                f'      <span class="cat-card-count">{gen_count}</span>\n'
                f'    </div>\n'
                f'  </label>'
            )
        cards_html = "\n".join(cards)
        touch_css = self.genHTMLTouchCSS()
        touch_js = self.genHTMLTouchJS()
        touch_header = self._touch_header_html(lang, back_url=f"TouchHub{langparam}", back_icon_only=True)
        page = (
            self.genHTMLStart(lang) + "\n"
            "<head>\n"
            f"  <title>{_('Categories')} \u2013 {_('Boxes.py')}</title>\n"
            f"  {self.genHTMLMeta()}\n"
            f"  {self.genHTMLCSS()}\n"
            f"  {touch_css}\n"
            f"  {self.genHTMLCategoriesCSS()}\n"
            f"  {self.genHTMLJS()}\n"
            f"  {touch_js}\n"
            "</head>\n"
            f'<body class="touch-cat" onload="initCategorySettingsPage()">\n'
            f"\n{touch_header}\n\n"
            '<div class="cat-body">\n'
            '  <div class="cat-title-row">\n'
            f"    <h2>{_('Categories')}</h2>\n"
            '    <div class="cat-title-actions">\n'
            f'      <button class="cat-btn secondary" onclick="resetCategorySettings()">{_("Show all categories")}</button>\n'
            f'      <button class="cat-btn" onclick="saveCategorySettingsExplicit()">{_("Save")}</button>\n'
            "    </div>\n"
            "  </div>\n"
            f"  <p>{_('Uncheck categories to hide them from the menu, gallery and touch interface.')}</p>\n"
            '  <div class="cat-grid">\n'
            f"{cards_html}\n"
            "  </div>\n"
            f"<script>const CAT_HOME_URL = 'TouchHub{langparam}';</script>\n"
            "</div>\n\n</body>\n</html>\n"
        )
        start_response("200 OK", [("Content-type", "text/html; charset=utf-8")])  # type: ignore[operator]
        return [page.encode("utf-8")]
