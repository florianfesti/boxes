# Copyright (C) 2016-2017 Florian Festi
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
from __future__ import annotations
import html


class CategoriesUIMixin:
    """Mixin that renders the /categories (Selection) page in touch style."""

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

    def _touch_header_html(self, lang: object, back_url: str = "", back_icon_only: bool = False, center_html: str = "", show_dropdown: bool = True) -> str:
        raise NotImplementedError

    def serveCategorySettings(self, environ: object, start_response: object, lang: object) -> list[bytes]:
        """Render the /categories (Selection) page."""
        _ = lang.gettext  # type: ignore[attr-defined]
        lang_name = lang.info().get("language", None)  # type: ignore[attr-defined]
        langparam = f"?language={lang_name}" if lang_name else ""

        # ── Categories checklist ─────────────────────────────────────────────
        cat_items: list[str] = []
        for nr, group in enumerate(self.groups):
            gen_count = len(group.generators)
            cat_items.append(
                f'    <li class="sel-item">'
                f'<label class="sel-row">'
                f'<input type="checkbox" data-cat-id="{nr}" onchange="onCategoryCheckboxChange(this)" checked>'
                f'<span class="sel-count">{gen_count}</span>'
                f'<span class="sel-label">{html.escape(_(group.title))}</span>'
                f'</label></li>'
            )

        # ── Labels checklist (dynamic) ────────────────────────────────────────
        all_tags: set[str] = set()
        label_counts: dict[str, int] = {}
        no_label_count: int = 0
        for group in self.groups:
            for gen in group.generators:
                tags: list[str] = getattr(gen, "tags", [])
                if not tags:
                    no_label_count += 1
                for tag in tags:
                    all_tags.add(tag)
                    label_counts[tag] = label_counts.get(tag, 0) + 1
        sorted_tags = sorted(all_tags)

        label_items: list[str] = []
        for tag in sorted_tags:
            count = label_counts.get(tag, 0)
            label_items.append(
                f'    <li class="sel-item">'
                f'<label class="sel-row">'
                f'<input type="checkbox" data-label-id="{html.escape(tag)}" onchange="onLabelCheckboxChange(this)" checked>'
                f'<span class="sel-count">{count}</span>'
                f'<span class="sel-label">{html.escape(tag)}</span>'
                f'</label></li>'
            )
        # Special "No label" entry for generators with no tags at all
        label_items.append(
            f'    <li class="sel-item">'
            f'<label class="sel-row">'
            f'<input type="checkbox" data-label-id="__no_label__" onchange="onLabelCheckboxChange(this)" checked>'
            f'<span class="sel-count">{no_label_count}</span>'
            f'<span class="sel-label sel-nolabel">{_("No label")}</span>'
            f'</label></li>'
        )

        cats_html  = "\n".join(cat_items)
        labels_html = "\n".join(label_items)

        touch_header = self._touch_header_html(lang, back_url=f"TouchHub{langparam}", back_icon_only=True)
        page = (
            self.genHTMLStart(lang) + "\n"
            "<head>\n"
            f"  <title>{_('Selection')} \u2013 {_('Boxes.py')}</title>\n"
            f"  {self.genHTMLMeta()}\n"
            f"  {self.genHTMLCSS()}\n"
            f"  {self.genHTMLTouchCSS()}\n"
            f"  {self.genHTMLCategoriesCSS()}\n"
            f"  {self.genHTMLJS()}\n"
            f"  {self.genHTMLTouchJS()}\n"
            "</head>\n"
            f'<body class="touch-cat" onload="initCategorySettingsPage()">\n'
            f"\n{touch_header}\n\n"
            '<div class="cat-body">\n'
            '  <div class="cat-title-row">\n'
            f"    <h2>{_('Selection')}</h2>\n"
            '    <div class="cat-title-actions">\n'
            f'      <span id="sel-settings-status" style="display:none">\u2713</span>\n'
            f'      <button class="cat-btn secondary" onclick="resetAllSelectionSettings()">{_("Show all")}</button>\n'
            f'      <button class="cat-btn" onclick="saveCategorySettingsExplicit()">{_("Save &amp; back")}</button>\n'
            "    </div>\n"
            "  </div>\n"
            f"  <p>{_('Uncheck categories or labels to hide generators from the interface.')}</p>\n"
            '\n'
            f'  <h3 class="sel-section-title">{_("Categories")}</h3>\n'
            '  <ul class="sel-list">\n'
            f"{cats_html}\n"
            "  </ul>\n"
            '\n'
            f'  <h3 class="sel-section-title">{_("Labels")}</h3>\n'
            '  <ul class="sel-list">\n'
            f"{labels_html}\n"
            "  </ul>\n"
            f"<script>const CAT_HOME_URL = 'TouchHub{langparam}';</script>\n"
            f'  <p class="sel-help-note">'
            f'<strong>{_("How filtering works:")}</strong> '
            f'{_("Categories are applied first — only generators from checked categories are shown. "
               "Labels then refine the result: a generator is visible if at least one of its labels is checked. "
               "Generators with no label are controlled by the \"No label\" toggle.")}'
            f'</p>\n'
            "</div>\n\n</body>\n</html>\n"
        )
        start_response("200 OK", [("Content-type", "text/html; charset=utf-8")])  # type: ignore[operator]
        return [page.encode("utf-8")]
