# Copyright (C) 2016-2017 Florian Festi
#
#  This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
from __future__ import annotations

import html


class HomeGalleryMixin:
    """HTML generation for the thumbnail gallery page.

    Designed as a mixin for BServer.  All methods use ``self`` attributes
    set by BServer.__init__ (static_url, groups, _cache, …).
    """

    # Stubs for attributes provided by BServer
    static_url: str
    groups: list
    _cache: dict

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

    def genPagePartHeader(self, lang: object, current_interface: str = "") -> str:
        raise NotImplementedError

    def genHTMLColsSelection(self) -> str:
        raise NotImplementedError

    def tag_badges_html(self, box: type) -> str:
        raise NotImplementedError

    # Gallery page

    def serveGallery(
        self, environ: object, start_response: object, lang: object
    ) -> list[bytes]:
        """Serve the thumbnail gallery page (with caching)."""
        _ = lang.gettext  # type: ignore[attr-defined]
        lang_name = lang.info().get("language", None)  # type: ignore[attr-defined]

        start_response("200 OK", [("Content-type", "text/html; charset=utf-8")])  # type: ignore[operator]

        cache_key = ("Gallery", lang_name)
        if cache_key in self._cache:
            return self._cache[cache_key]

        langparam = f"?language={lang_name}" if lang_name else ""

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
{self.genPagePartHeader(lang, current_interface="Gallery")}
"""]
        for nr, group in enumerate(self.groups):
            result.append(f'<div class="gallery-group" data-group-id="{nr}">\n')
            result.append(f"<h2>{_(group.title)}</h2>\n")
            for box in group.generators:
                bname = box.__name__
                thumbnail = f"{self.static_url}/samples/{bname}-thumb.jpg"
                href = f"{bname}{langparam}"
                badges = self.tag_badges_html(box)
                overlay = (
                    f'<span class="gallery-badges">{badges.strip()}</span>'
                    if badges.strip()
                    else ""
                )
                result.append(
                    f'  <span class="gallery" id="search_id_{bname}">'
                    f'<a title="{_(bname)} - {html.escape(_(box.__doc__))}" href="{href}">'
                    f'<span class="gallery-img-wrap">'
                    f'<img alt="{_(bname)}" src="{thumbnail}">{overlay}</span>'
                    f"<br>{_(bname)}</a></span>\n"
                )
            result.append("</div>\n")  # close .gallery-group

        result.append(
            "\n</div><div style=\"width: 5%; float: left;\"></div>\n"
            "        <div class=\"clear\"></div><hr></div>\n"
            "</body>\n</html>\n"
        )
        self._cache[cache_key] = [s.encode("utf-8") for s in result]
        return self._cache[cache_key]
