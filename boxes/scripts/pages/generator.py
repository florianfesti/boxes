# Copyright (C) 2016-2017 Florian Festi
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
from __future__ import annotations

import argparse
import html as _html
import inspect
import json
from pathlib import Path

import markdown

from boxes.generators import ui_groups_by_name


class GeneratorUIMixin:
    """Mixin that renders the touch-mode generator configuration page (/GeneratorName)."""

    static_url: str

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

    def genHTMLTouchCSS(self) -> str:
        raise NotImplementedError

    def genHTMLGeneratorCSS(self) -> str:
        raise NotImplementedError

    def genHTMLTouchJS(self) -> str:
        raise NotImplementedError

    def _touch_header_html(
        self,
        lang: object,
        back_url: str = "",
        back_icon_only: bool = False,
        center_html: str = "",
        show_dropdown: bool = True,
    ) -> str:
        raise NotImplementedError

    def arg2html(
        self,
        a: argparse.Action,
        prefix: str | None,
        defaults: dict | None = None,
        _=lambda s: s,
    ) -> str:
        raise NotImplementedError

    def tag_badges_html(self, box: type) -> str:
        raise NotImplementedError

    def _gen_breadcrumb_html(self, box: object, name: str, _=lambda s: s) -> str:
        """Return the «Category › GeneratorName» breadcrumb HTML."""
        ui_group_name: str = getattr(box, "ui_group", "")
        group = ui_groups_by_name.get(ui_group_name)
        category_title: str = group.title if group else ui_group_name
        if not category_title:
            return ""
        cat = _html.escape(_(category_title))
        gen = _html.escape(name)
        return (
            f'<div class="gen-category-breadcrumb">'
            f'<span class="gen-bc-cat">{cat}</span>'
            f'<span class="gen-bc-sep"> › </span>'
            f'<span class="gen-bc-name">{gen}</span>'
            f'</div>'
        )

    # Generator config page
    def genTouchArgs(
        self,
        name: str,
        box: object,
        lang: object,
        action: str = "",
        defaults: dict | None = None,
        back_url: str = "",
    ) -> list[bytes]:
        """Touch-mode generator configuration page."""
        _ = lang.gettext  # type: ignore[attr-defined]
        lang_name = lang.info().get("language", None)  # type: ignore[attr-defined]
        langparam = f"?language={lang_name}" if lang_name else ""
        resolved_back = back_url if back_url else f"TouchHub{langparam}"
        no_img_msg = _(
            "There is no image yet. Please donate an image of your project on "
            '<a href=&quot;https://github.com/florianfesti/boxes/issues/628&quot; '
            'target=&quot;_blank&quot; rel=&quot;noopener&quot;>GitHub</a>!'
        )
        desc_html = (
            markdown.markdown(_(box.description), extensions=["extra"])  # type: ignore[attr-defined]
            .replace('src="static/', f'src="{self.static_url}/')
        ) if box.description else ""  # type: ignore[attr-defined]
        form_rows: list[str] = []
        groupid = 0
        for group in box.argparser._action_groups[3:] + box.argparser._action_groups[:3]:  # type: ignore[attr-defined]
            if not group._group_actions:
                continue
            if len(group._group_actions) == 1 and isinstance(
                group._group_actions[0], argparse._HelpAction
            ):
                continue
            prefix = getattr(group, "prefix", None)
            # Groups added via addSettingsArgs (prefix is not None) start collapsed;
            # only the generator's own params group (prefix=None) starts expanded.
            start_collapsed = prefix is not None
            h3_cls      = "toggle" if start_collapsed else "toggle open"
            h3_expanded = "false" if start_collapsed else "true"
            tbl_style   = ' style="display:none"' if start_collapsed else ""
            # Prefix IDs with "g" to avoid collision with numeric category IDs
            # that applyHiddenCategoriesMenu() reads from localStorage.
            sid = f"g{groupid}"
            form_rows.append(
                f'<h3 id="h-{sid}" data-id="{sid}" role="button" '
                f'aria-expanded="{h3_expanded}" tabindex="0" class="{h3_cls}">'
                f"{_(group.title)}</h3>\n"
                f'<table role="presentation" id="{sid}"{tbl_style}>\n'
            )
            for a in group._group_actions:
                if a.dest in ("input", "output", "language"):
                    continue
                form_rows.append(self.arg2html(a, prefix, defaults, _))
            form_rows.append("</table>")
            groupid += 1
        num_hide = 0  # all groups start expanded; users can collapse what they don't need
        # Discover JSON template files next to the generator source
        templates: list[tuple[str, dict]] = []
        try:
            gen_file = Path(inspect.getfile(type(box)))
            for jf in sorted(gen_file.parent.glob("*.json")):
                try:
                    templates.append((jf.stem, json.loads(jf.read_text(encoding="utf-8"))))
                except (ValueError, OSError):
                    pass
        except (TypeError, OSError):
            pass
        templates_js = json.dumps([{"name": n, "data": d} for n, d in templates], separators=(",", ":"))
        templates_script = f'<script>var GENERATOR_TEMPLATES={templates_js};</script>' if templates else ""
        # Build the unified controls bar (template dropdown + zoom + info slots)
        template_section = ""
        if templates:
            opts = "\n".join(
                f'<option value="{i}">{t[0]}</option>'
                for i, t in enumerate(templates)
            )
            template_section = (
                f'<select id="template-select" class="template-select" onchange="applyTemplatePreset(this.value)">'
                f'<option value="">{_("Load template")}\u2026</option>{opts}'
                f'</select>\n'
                f'  <span class="controls-bar-sep"></span>\n'
            )
        controls_bar_html = (
            f'<div class="controls-bar">\n'
            f'  {template_section}'
            f'  <div id="preview-ctrl-card" class="preview-ctrl-card">\n'
            f'    <button type="button" title="{_("Zoom out")}" onclick="preview_scale/=1.2; document.getElementById(\'preview_img\').style.width = preview_scale + \'%\';">🔍➖</button>\n'
            f'    <button type="button" title="{_("Zoom in")}" onclick="preview_scale*= 1.2; document.getElementById(\'preview_img\').style.width = preview_scale + \'%\';">🔍➕</button>\n'
            f'    <button type="button" title="{_("Reset zoom")}" onclick="preview_scale=100; document.getElementById(\'preview_img\').style.width = preview_scale + \'%\';">↺</button>\n'
            f'  </div>\n'
            f'  <div id="surface-info-bar" class="surface-info-bar"></div>\n'
            f'  <div id="price-info-bar" class="price-info-bar"></div>\n'
            f'  <div id="fit-info-bar" class="fit-info-bar"></div>\n'
            f'</div>\n'
        )
        # Tab buttons go in the header center
        tabs_html = (
            f'<button class="tabbtn th-tab-btn active" onclick="switchTab(event,\'description\')">'
            f'{_("Description")}</button>'
            f'<button class="tabbtn th-tab-btn" onclick="switchTab(event,\'configuration\')">'
            f'{_("Configuration")}</button>'
        )
        header_html = self._touch_header_html(
            lang, back_url=resolved_back, back_icon_only=True, center_html=tabs_html
        )
        page = (
            self.genHTMLStart(lang) + "\n"
            "<head>\n"
            f"  <title>{_('%s - Boxes') % _(name)}</title>\n"
            f"  {self.genHTMLMeta()}\n"
            f"{self.genHTMLMetaLanguageLink()}\n"
            f"  {self.genHTMLCSS()}\n"
            f"  {self.genHTMLTouchCSS()}\n"
            f"  {self.genHTMLGeneratorCSS()}\n"
            f"  {self.genHTMLJS()}\n"
            f"  {self.genHTMLTouchJS()}\n"
            f"  {templates_script}\n"
            f'  <script src="{self.static_url}/generator.js"></script>\n'
            "</head>\n"
            f'<body class="touch-args" onload="initTouchArgs({num_hide})">\n'
            f"\n{header_html}\n\n"
            '<div class="touch-args-body">\n'
            f'  <div class="gen-doc-row">\n'
            f'    {self._gen_breadcrumb_html(box, name, _)}\n'
            f'    <p class="touch-gen-doc">{_(box.__doc__) if box.__doc__ else ""}</p>\n'
            f'  </div>\n'
            f'  <div id="tab-description" class="tab-panel">\n'
            "    <div class=\"description\">\n"
            f"      {desc_html}\n"
            "      <div>\n"
            f'        <img style="width:100%;max-width:480px;" src="{self.static_url}/samples/{box.__class__.__name__}.jpg"\n'
            f"             onerror=\"this.parentElement.innerHTML = '{no_img_msg}';\" alt=\"Picture of box.\">\n"
            "      </div>\n"
            "    </div>\n"
            "  </div>\n"
            '\n  <div id="tab-configuration" class="tab-panel" style="display:none">\n'
            f"{controls_bar_html}"
            '    <div class="config-layout">\n'
            '      <div class="config-form">\n'
            f'        <form id="arguments" action="{action}" method="GET" rel="nofollow">\n'
            f'          {"".join(form_rows)}\n'
            f'          <input type="hidden" name="language" id="language" value="{lang_name or ""}">\n'
            "        </form>\n"
            "      </div>\n"
            '      <div id="preview" class="config-preview">\n'
            '        <div id="preview-container" class="preview-container">\n'
            '          <div id="preview-loading" class="preview-loading" role="status" aria-label="Loading\u2026"></div>\n'
            '          <figure id="preview_figure">\n'
            f'            <img id="preview_img" style="width:100%" src="{self.static_url}/nothing.png">\n'
            "          </figure>\n"
            "        </div>\n"
            "      </div>\n"
            "    </div>\n"
            "  </div>\n"
            "\n</div><!-- /touch-args-body -->\n"
            "\n<!-- Sticky bottom action bar -->\n"
            '<div class="touch-action-bar">\n'
            f'  <button class="touch-action-btn" data-render="1" data-target="_blank">{_("Generate")}</button>\n'
            f'  <button class="touch-action-btn secondary" data-render="2" data-target="_self">{_("Download")}</button>\n'
            f'  <button class="touch-action-btn secondary" data-render="0" data-target="_self">{_("URL")}</button>\n'
            f'  <button class="touch-action-btn secondary" data-render="3" data-target="_blank">{_("QR")}</button>\n'
            f'  <button class="touch-action-btn secondary" type="button" onclick="saveParamsAsJson()">{_("Save")}</button>\n'
            f'  <label class="touch-action-btn secondary" style="cursor:pointer;">{_("Import")}'
            f'<input type="file" accept=".json" style="display:none" onchange="loadParamsFromJson(this)"></label>\n'
            "</div>\n"
            "\n<!-- Help modal -->\n"
            '<div id="help-modal" class="help-modal-overlay" onclick="closeHelpModal()">\n'
            '  <div class="help-modal-box" onclick="event.stopPropagation()">\n'
            '    <div id="help-modal-content" class="help-modal-content"></div>\n'
            '    <button type="button" class="stepper-btn help-modal-close" onclick="closeHelpModal()">Close</button>\n'
            "  </div>\n"
            "</div>\n"
            "\n<!-- Image modal -->\n"
            '<div id="img-modal" class="img-modal-overlay" onclick="closeImgModal()">\n'
            '  <img id="img-modal-img" src="" alt="">\n'
            "</div>\n"
            "\n</body>\n</html>\n"
        )
        return [page.encode("utf-8")]
