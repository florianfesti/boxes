# Copyright (C) 2016-2017 Florian Festi
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
from __future__ import annotations
pass
class ColorsUIMixin:
    """Mixin that renders the /settings (Colors) page in touch style."""
    static_url: str
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
    def genHTMLColorsCSS(self) -> str:
        raise NotImplementedError
    def genHTMLTouchJS(self) -> str:
        raise NotImplementedError
    def _touch_header_html(self, lang: object, back_url: str = "", back_icon_only: bool = False) -> str:
        raise NotImplementedError
    def serveColors(self, environ: object, start_response: object, lang: object) -> list[bytes]:
        """Render the /settings page (touch style)."""
        _ = lang.gettext  # type: ignore[attr-defined]
        lang_name = lang.info().get("language", None)  # type: ignore[attr-defined]
        langparam = f"?language={lang_name}" if lang_name else ""
        from boxes.Color import Color
        named_colors: list[tuple[str, str]] = [
            (cname, Color.to_hex(getattr(Color, cname)))
            for cname in ("BLACK", "BLUE", "GREEN", "RED", "CYAN", "YELLOW", "MAGENTA", "WHITE")
        ]
        rows: list[str] = []
        for role, (label, desc) in Color.ROLE_LABELS.items():
            default_hex = Color.to_hex(getattr(Color, role))
            options = "\n".join(
                f'        <option value="{hex_val}"{" selected" if hex_val == default_hex else ""}>'
                f"{cname} ({hex_val})</option>"
                for cname, hex_val in named_colors
            )
            rows.append(
                f'  <div class="cs-row">\n'
                f'    <div class="cs-label"><label for="color_{role}">{label}</label></div>\n'
                f'    <select class="cs-select" id="color_{role}" data-role="{role}" onchange="onColorChange(this)">\n'
                f'{options}\n'
                f'    </select>\n'
                f'    <span class="cs-desc">{desc}</span>\n'
                f'  </div>'
            )
        rows_html = "\n".join(rows)
        touch_css = self.genHTMLTouchCSS()
        touch_js = self.genHTMLTouchJS()
        touch_header = self._touch_header_html(lang, back_url=f"TouchHub{langparam}", back_icon_only=True)
        page = (
            self.genHTMLStart(lang) + "\n"
            "<head>\n"
            f"  <title>{_('Colors')} \u2013 {_('Boxes.py')}</title>\n"
            f"  {self.genHTMLMeta()}\n"
            f"  {self.genHTMLCSS()}\n"
            f"  {touch_css}\n"
            f"  {self.genHTMLColorsCSS()}\n"
            f"  {self.genHTMLJS()}\n"
            f"  {touch_js}\n"
            "</head>\n"
            f'<body class="touch-colors" onload="initColorSettingsPage()">\n'
            f"\n{touch_header}\n\n"
            '<div class="cs-body">\n'
            f"  <h2>{_('Colors')}</h2>\n"
            f"  <p>{_('Choose the SVG stroke color for each laser operation. Changes are saved instantly in your browser.')}</p>\n"
            '  <div class="cs-grid">\n'
            f"{rows_html}\n"
            "  </div>\n"
            '  <div class="cs-actions">\n'
            f'    <button class="cs-btn" onclick="saveColorSettingsExplicit()">{_("Save")}</button>\n'
            f'    <button class="cs-btn secondary" onclick="exportColorSettings()">{_("Export JSON")}</button>\n'
            f'    <button class="cs-btn secondary" onclick="document.getElementById(\'import-file\').click()">{_("Import JSON")}</button>\n'
            f'    <input type="file" id="import-file" accept=".json,application/json" onchange="importColorSettings(this)">\n'
            f'    <button class="cs-btn secondary" onclick="resetColorSettings()">{_("Reset to defaults")}</button>\n'
            f'    <span id="color-settings-status" style="display:none">{_("Saved.")}</span>\n'
            "  </div>\n"
            "</div>\n\n</body>\n</html>\n"
        )
        start_response("200 OK", [("Content-type", "text/html; charset=utf-8")])  # type: ignore[operator]
        return [page.encode("utf-8")]
