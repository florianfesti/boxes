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


class MachineUIMixin:
    """Mixin that renders the /machine (laser engraving zone) settings page."""

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

    def genHTMLTouchJS(self) -> str:
        raise NotImplementedError

    def genHTMLMachineCSS(self) -> str:
        raise NotImplementedError

    def _touch_header_html(self, lang: object, back_url: str = "", back_icon_only: bool = False) -> str:
        raise NotImplementedError

    def serveMachine(self, environ: object, start_response: object, lang: object) -> list[bytes]:
        """Render the /machine settings page (touch style)."""
        _ = lang.gettext  # type: ignore[attr-defined]
        lang_name = lang.info().get("language", None)  # type: ignore[attr-defined]
        langparam = f"?language={lang_name}" if lang_name else ""

        touch_header = self._touch_header_html(lang, back_url=f"TouchHub{langparam}", back_icon_only=True)

        page = (
            self.genHTMLStart(lang) + "\n"
            "<head>\n"
            f"  <title>{_('Machine')} \u2013 {_('Boxes.py')}</title>\n"
            f"  {self.genHTMLMeta()}\n"
            f"  {self.genHTMLCSS()}\n"
            f"  {self.genHTMLTouchCSS()}\n"
            f"  {self.genHTMLMachineCSS()}\n"
            f"  {self.genHTMLJS()}\n"
            f"  {self.genHTMLTouchJS()}\n"
            "</head>\n"
            f'<body class="touch-machine" onload="initMachineConfigPanel()">\n'
            f"\n{touch_header}\n\n"
            '<div class="ms-body">\n'
            '  <div class="ms-title-row">\n'
            f"    <h2>\u2699 {_('Machine')}</h2>\n"
            '    <div class="ms-title-actions">\n'
            f'      <button class="ms-reset-btn" onclick="resetMachineSettingsPage()">{_("Reset to default")}</button>\n'
            f'      <button class="ms-save-btn" onclick="saveMachineSettingsPage()">{_("Save")}</button>\n'
            "    </div>\n"
            "  </div>\n"
            f"  <p>{_('Set your laser engraving zone size. Used on the generator page to check if the design fits.')}</p>\n"
            '  <div class="ms-section">\n'
            f"    <h3>{_('Custom size')}</h3>\n"
            '    <div class="ms-dims">\n'
            f'      <label>{_("Width (mm)")}<input type="number" id="machine-w" min="1" max="9999" step="1" value="300"></label>\n'
            f'      <label>{_("Height (mm)")}<input type="number" id="machine-h" min="1" max="9999" step="1" value="300"></label>\n'
            "    </div>\n"
            "  </div>\n"
            '  <div class="ms-section">\n'
            f"    <h3>{_('Machine presets')}</h3>\n"
            f'    <select id="machine-preset" class="ms-preset-select"></select>\n'
            "  </div>\n"
            '  <div class="ms-section">\n'
            f"    <h3>\U0001F4B6 {_('Material pricing')}</h3>\n"
            f"    <p style=\"font-size:.88em;color:#666;margin:0 0 10px\">{_('Select a material to get a cost estimate on the generator page.')}</p>\n"
            f'    <select id="machine-material" class="ms-mat-select"></select>\n'
            "  </div>\n"
            '  <div class="ms-section">\n'
            f"    <h3>\U0001F4CA {_('Margin coefficient')}</h3>\n"
            f"    <p style=\"font-size:.88em;color:#666;margin:0 0 10px\">{_('Multiply the material cost by this factor (e.g. 1.5 for a 50% margin).')}</p>\n"
            '    <div class="ms-coef-row">\n'
            f'      <label>{_("Coefficient")} : <input type="number" id="machine-margin-coef" min="1" max="100" step="0.1" value="2.0"></label>\n'
            "    </div>\n"
            "  </div>\n"
            "</div>\n\n"
            "<script>\n"
            f"const MS_HOME_URL = 'TouchHub{langparam}';\n"
            "function saveMachineSettingsPage() {\n"
            "    window.location.href = MS_HOME_URL;\n"
            "}\n"
            "function resetMachineSettingsPage() {\n"
            "    localStorage.removeItem('boxes-machine-config');\n"
            "    initMachineConfigPanel();\n"
            "    const btn = document.querySelector('.ms-reset-btn');\n"
            "    if (btn) { const t = btn.textContent; btn.textContent = '\u2713'; setTimeout(() => { btn.textContent = t; }, 1200); }\n"
            "}\n"
            "</script>\n"
            "</body>\n</html>\n"
        )
        start_response("200 OK", [("Content-type", "text/html; charset=utf-8")])  # type: ignore[operator]
        return [page.encode("utf-8")]
