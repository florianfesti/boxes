
/*** Thumbnails ******************************************/

function showThumbnail(img_link) {
    const img = document.getElementById("sample-preview");
    img.src = img_link;
    img.style.height = "auto";
    img.style.display = "block";
}

function showThumbnailEvt(evt) {
    const url = evt.target.getAttribute("data-thumbnail");
    showThumbnail(url);
}

function hideThumbnail() {
    const img = document.getElementById("sample-preview");
    img.style.display = "none";
}

/*** Expand/Collapse **************************************/

function expandId(id) {
    const e = document.getElementById(id);
    const h = document.getElementById("h-" + id);
    e.style.display = "block";
    h.classList.add("open");
    h.setAttribute("aria-expanded", "true");
}
function collapseId(id) {
    const e = document.getElementById(id);
    const h = document.getElementById("h-" + id);
    e.style.display = "none";
    h.classList.remove("open");
    h.setAttribute("aria-expanded", "false");
}

function toggleId(id) {
    const e = document.getElementById(id);
    const h = document.getElementById("h-" + id);
    if (e.style.display == null || e.style.display === "none") {
        expandId(id);
    } else {
        collapseId(id);
    }
}

function toggleEl(el) {
    const id = el.getAttribute("data-id");
    toggleId(id);
}

function toggleEvt(evt) {
    const id = evt.target.getAttribute("data-id");
    // https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Roles/button_role#examples
    if (evt instanceof MouseEvent) {
        toggleId(id);
    }
    if (evt instanceof KeyboardEvent && (evt.key === "Enter" || evt.key === " ")) {
        evt.preventDefault();
        toggleId(id);
    }
}

/*** Init page ***************************************/

function initToggle(el, hide = false) {
    // Add event handler.
    el.addEventListener("click", toggleEvt);
    el.addEventListener("keydown", toggleEvt);
    // Hide.
    if (hide) {
        toggleEl(el);
    }
}

function initThumbnail(el) {
    // Add event handler.
    el.addEventListener("mouseenter", showThumbnailEvt);
    el.addEventListener("mouseleave", hideThumbnail);
}

function initPage(num_hide = null) {
    const h = document.getElementsByClassName("toggle");
    let i = 0;
    for (let el of h) {
        if (num_hide === null || i < num_hide) {
            initToggle(el, true);
        } else {
            initToggle(el, false);
        }
        i++;
    }
    const t = document.getElementsByClassName("thumbnail");
    for (let el of t) initThumbnail(el);
}

function initArgsPage(num_hide = null) {
    initPage(num_hide);
    const i = document.querySelectorAll("td > input, td > select");
    for (let el of i) {
	el.addEventListener("change", refreshPreview);
    }
    refreshPreview();
    document.getElementById("preview_chk").addEventListener("change", togglePreview);
}

/*** Preview ****************************************/

function refreshPreview() {
    if (document.getElementById("preview_img").hidden)
	return;

    const form = document.querySelector("#arguments");
    const formData = new FormData(form);
    formData.set("format", "svg");

    const url = form.action + "?" + new URLSearchParams(formData).toString() + "&render=1";

    const preview = document.getElementById("preview_img");
    preview.src = url;
}

function togglePreview() {
    document.getElementById("preview_img").hidden = !event.target.checked;
    if (event.target.checked)
	refreshPreview();
}

/*** GrindFinity ******************************************/

function GridfinityTrayLayout_GenerateLayout(x, y, nx, ny, countx, county) {
    // x = width in mm
    // y = height in mm
    // nx # of gridfinity grids in X
    // ny # of gridfinity grids in Y
    // countx split x into this many
    // county split y into this many
    layout = '';
    if (countx == 0)
        countx = nx;
    if (county == 0)
        county = ny
    stepx = x / countx;
    stepy = y / county;
    for (i = 0; i < countx; i++) {
        line = ' |'.repeat(i) + ` ,> ${stepx}mm\n`;
        layout += line;
    }
    for (i = 0; i < county; i++) {
        layout += "+-".repeat(countx) + "+\n";
        layout += "| ".repeat(countx) + `|  ${stepy}mm\n`;
    }
    layout += "+-".repeat(countx) + "+\n";
    return layout
}

function GridfinityTrayUpdateLayout(event) {
    console.log("update");
    if (window.layoutUpdated == true) {
        // Don't do the update if the layout has been manually touched.
        if (confirm("You have manually updated the Layout.  Do you wish to regenerate it?")) {
            window.layoutUpdated = false;
        } else {
            return;
        }
    }
    console.log("updating");
    nx = document.getElementById('nx').value;
    ny = document.getElementById('ny').value;
    countx = document.getElementById('countx').value;
    county = document.getElementById('county').value;
    margin = document.getElementById('margin').value;
    x = nx*42 - margin
    y = ny*42 - margin
    layout_id = document.getElementById('layout');
    layout_id.value = GridfinityTrayLayout_GenerateLayout(x, y, nx, ny, countx, county);
}

function setUpdated() {
    console.log("this was updated");
    window.layoutUpdated=true;
}
function GridfinityTrayLayoutInit() {
    console.log("update init");
    ids = ['nx', 'ny', 'countx', 'county', 'margin'];
    window.layoutUpdated=false;
    for (id_string of ids) {
        id = document.getElementById(id_string);
        id.addEventListener('input', GridfinityTrayUpdateLayout);
    }
    layout_id = document.getElementById('layout');
    layout_id.addEventListener('change', setUpdated);
    layout_id.addEventListener('input', setUpdated);

    GridfinityTrayUpdateLayout();
    layout_id = document.getElementById('layout');
    layout_id.rows = 20;
    layout_id.cols = 24;
}

/*** PhotoFrame ******************************************/

function PhotoFrameInit() {
    console.log("PhotoFrameInit: setting event handlers for matting");
    window.photoFrameUserMattingW = null;
    window.photoFrameUserMattingH = null;
    window.photoFrameUserGlassW = null;
    window.photoFrameUserGlassH = null;

    for (const id_string of ['matting_w', 'matting_h']) {
        const id = document.getElementById(id_string);
        id.addEventListener('input', PhotoFrame_MattingUpdate);
        // id.addEventListener('change', PhotoFrame_MattingUpdate);
    }
    for (const id_string of ['glass_w', 'glass_h']) {
        const id = document.getElementById(id_string);
        id.addEventListener('input', PhotoFrame_GlassUpdate);
        id.addEventListener('change', PhotoFrame_GlassUpdate);
    }
    for (const id_string of ['golden_mat']) {
        const id = document.getElementById(id_string);
        id.addEventListener('change', PhotoFrame_GoldenMattingChange);
    }
    for (const id_string of ['matting_overlap', 'x', 'y']) {
        const id = document.getElementById(id_string);
        id.addEventListener('input', PhotoFrame_GoldenMattingChange);
        id.addEventListener('change', PhotoFrame_GoldenMattingChange);
    }

    // Set the initial values
    PhotoFrame_GoldenMattingChange();
}

function PhotoFrame_MattingUpdate(event) {
    // If the user manually updates the matting, save the values and turn off golden matting

    const golden_mat = document.getElementById('golden_mat').checked;
    const matting_w = document.getElementById('matting_w').value;
    const matting_h = document.getElementById('matting_h').value;

    console.log("PhotoFrame_MattingUpdate", matting_w, matting_h, golden_mat);
    window.photoFrameUserMattingW = matting_w;
    window.photoFrameUserMattingH = matting_h;

    if (golden_mat) {
        document.getElementById('golden_mat').checked = false;
    }
    if (matting_w || matting_h) {
        document.getElementById('glass_w').value = 0;
        document.getElementById('glass_h').value = 0;
    }
}

function PhotoFrame_GlassUpdate(event) {
    // If the user enters glass dimensions, save the values and turn off golden matting

    // console.log("PhotoFrame_GlassUpdate");

    const golden_mat = document.getElementById('golden_mat').checked;
    const glass_w = parseFloat(document.getElementById('glass_w').value);
    const glass_h = parseFloat(document.getElementById('glass_h').value);
    const matting_w = parseFloat(document.getElementById('matting_w').value);
    const matting_h = parseFloat(document.getElementById('matting_h').value);

    console.log("PhotoFrame_GlassUpdate", glass_w, glass_h, matting_w, matting_h, golden_mat);
    window.photoFrameUserGlassW = glass_w;
    window.photoFrameUserGlassH = glass_h;

    if (golden_mat) {
        document.getElementById('golden_mat').checked = false;
    }
    if (glass_w || glass_h) {
        document.getElementById('matting_w').value = 0;
        document.getElementById('matting_h').value = 0;
    }
}

function PhotoFrame_GoldenMattingChange(event) {
    // If the user turns on golden matting, calculate the values
    // If the user turns off golden matting, restore the manual matting values
    // If golden matting is on and the user changes the photo size or overlap, recalculate the matting

    const golden_mat = document.getElementById('golden_mat').checked;
    console.log("PhotoFrame_GoldenMattingChange", golden_mat);

    if (golden_mat) {
        try {
            const mattingWidth = PhotoFrame_GoldenMattingWidth();
            document.getElementById('matting_w').value = mattingWidth;
            document.getElementById('matting_h').value = mattingWidth;
        } catch (error) {
            document.getElementById('matting_w').value = 0;
            document.getElementById('matting_h').value = 0;
        }
        document.getElementById('glass_w').value = 0;
        document.getElementById('glass_h').value = 0;
    } else {
        if (window.photoFrameUserGlassW != null && window.photoFrameUserGlassH != null) {
            document.getElementById('glass_w').value = window.photoFrameUserGlassW;
            document.getElementById('glass_h').value = window.photoFrameUserGlassH;
            document.getElementById('matting_w').value = 0;
            document.getElementById('matting_h').value = 0;
        } else if (window.photoFrameUserMattingW != null && window.photoFrameUserMattingH != null) {
            document.getElementById('matting_w').value = window.photoFrameUserMattingW;
            document.getElementById('matting_h').value = window.photoFrameUserMattingH;
            document.getElementById('glass_w').value = 0;
            document.getElementById('glass_h').value = 0;
        }
    }
}

function PhotoFrame_GoldenMattingWidth() {
    // Calculate the width of the matting border. The border is around the hole in the matting
    // that the photo fits into, not the photo per se

    // Caller is responsible for catching errors

    let mattingWidth = goldenMattingWidth(PhotoFrame_MatHole("x"), PhotoFrame_MatHole("y"));
    mattingWidth = parseFloat(mattingWidth.toFixed(1));
    return mattingWidth;
}

function PhotoFrame_MatHole(element_id) {
    const photo_x = parseFloat(document.getElementById(element_id).value);
    const matting_overlap = parseFloat(document.getElementById('matting_overlap').value);
    return photo_x - 2 * matting_overlap;
}

function goldenMattingWidth(photoWidth, photoHeight) {
    // Validate input dimensions
    if (photoWidth <= 0 || photoHeight <= 0) {
        throw new Error("Photo dimensions must be positive values");
    }

    // Calculate the width of the matting border
    const phi = (1 + Math.sqrt(5)) / 2;
    const a = 4;
    const b = 2 * (photoWidth + photoHeight);
    const c = -(phi - 1) * photoWidth * photoHeight;

    // It is mathematically impossible to get complex roots
    // or for the other root to be the right answer, so relax
    const disc = b**2 - 4 * a * c;
    const x1 = (-b + Math.sqrt(disc)) / (2 * a);

    // Broad check for valid result in case user has achieved the impossible
    if (!isFinite(x1) || isNaN(x1) || x1 <= 0) {
        throw new Error("Calculation resulted in an invalid matting width");
    }

    return x1;
}

/*** TrayLayout ******************************************/

function ParseSections(s) {
    var sections = [];
    for (var section of s.split(":")) {
	var operands = section.split("/");
	if (operands.length > 2) return sections;
	if (operands.length == 2) {
	    for (var i=0; i<operands[1]; i++) {
		sections.push(Number(operands[0])/Number(operands[1]));
	    }
	    continue;
	}
	operands = section.split("*");
	if (operands.length > 2) return sections;
	if (operands.length == 2) {
	    for (var i=0; i<operands[1]; i++) {
		sections.push(Number(operands[0]));
	    }
	    continue;
	}
	sections.push(Number(section));
    }
    return sections;
}

function TrayLayout_GenerateLayout(sx, sy) {

    sx = ParseSections(sx);
    sy = ParseSections(sy);
    nx = sx.length
    ny = sy.length
    layout = '';
    if (nx <= 0)
        nx = 1;
    if (ny <= 0)
        ny = 1;

    for (i = 0; i < nx; i++) {
        line = ' |'.repeat(i) + ` ,> ${sx[i].toFixed(2)}mm\n`;
        layout += line;
    }
    for (i = 0; i < ny; i++) {
        layout += "+-".repeat(nx) + "+\n";
        layout += "| ".repeat(nx) + `|  ${sy[i].toFixed(2)}mm\n`;
    }
    layout += "+-".repeat(nx) + "+\n";
    return layout
}

function TrayUpdateLayout(event) {
    if (window.layoutUpdated == true) {
        // Don't do the update if the layout has been manually touched.
        if (confirm("You have manually updated the Layout.  Do you wish to regenerate it?")) {
            window.layoutUpdated = false;
        } else {
            return;
        }
    }
    sx = document.getElementById('sx').value;
    sy = document.getElementById('sy').value;
    layout_id = document.getElementById('layout');
    layout_id.value = TrayLayout_GenerateLayout(sx, sy);
}


function TrayLayoutInit() {
    ids = ['sx', 'sy'];
    window.layoutUpdated=false;
    for (id_string of ids) {
        id = document.getElementById(id_string);
        id.addEventListener('input', TrayUpdateLayout);
    }
    TrayUpdateLayout();
    layout_id = document.getElementById('layout');
    layout_id.addEventListener('change', setUpdated);
    layout_id.addEventListener('input', setUpdated);
    layout_id.rows = 20;
    layout_id.cols = 24;
}

function addCallbacks() {
    page_callbacks = {
        "TrayLayout": TrayLayoutInit,
        "GridfinityTrayLayout": GridfinityTrayLayoutInit,
        "PhotoFrame": PhotoFrameInit,
    };
    loc = new URL(window.location.href);
    pathname = loc.pathname;
    page = pathname.substr(pathname.lastIndexOf('/')+1);
    if (page in page_callbacks) {
        callback = page_callbacks[page];
        callback();
    }
}

/*** Search for generators **************************************/

document.addEventListener('DOMContentLoaded', function() {
    addCallbacks();
}, false);

function collapseAll() {
    const h = document.getElementsByClassName("toggle");
    for (let el of h) {
        id = el.getAttribute("data-id")
        collapseId(id);
    }
}

function expandAll() {
    const h = document.getElementsByClassName("toggle");
    for (let el of h) {
        id = el.getAttribute("data-id")
        expandId(id);
    }
}

function showAll(str) {
    let matching_ids = document.querySelectorAll('[id^="search_id_"]')
    for (let id of matching_ids) {
        id.style.display = "inline-block";
    }
}

function showOnly(str) {
    str = str.toLowerCase();
    let matching_ids = document.querySelectorAll('[id^="search_id_"]')
    for (let id of matching_ids) {
        name = id.id.replace("search_id_", "").toLowerCase();
        if (name.includes(str) || id.textContent.toLowerCase().includes(str)) {
            id.style.display = "inline-block";
        } else {
            id.style.display = "none";
	}
    }
}

function filterSearchItems() {
    const search = document.getElementById("search")
    if (search.value.length == 0) {
        collapseAll();
        showAll()
    } else {
        expandAll();
        showOnly(search.value)
    }
}
