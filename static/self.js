
/*** Color Settings **************************************/

const COLOR_STORAGE_KEY = 'boxes-color-settings';

/** Return saved overrides as {ROLE: '#rrggbb'} or {} */
function loadColorSettings() {
    try {
        return JSON.parse(localStorage.getItem(COLOR_STORAGE_KEY) || '{}');
    } catch (_) {
        return {};
    }
}

/** Persist overrides and flash the status indicator if present. */
function persistColorSettings(overrides) {
    localStorage.setItem(COLOR_STORAGE_KEY, JSON.stringify(overrides));
    const status = document.getElementById('color-settings-status');
    if (status) {
        status.style.display = 'inline';
        clearTimeout(status._hideTimer);
        status._hideTimer = setTimeout(() => { status.style.display = 'none'; }, 1500);
    }
}

/** Called by each select's onchange – auto-save immediately. */
function onColorChange(sel) {
    const overrides = loadColorSettings();
    overrides[sel.dataset.role] = sel.value;
    persistColorSettings(overrides);
    updateSwatch(sel);
}

/** Update the color swatch span next to a select element. */
function updateSwatch(sel) {
    const swatch = sel.parentElement.querySelector('.color-swatch');
    if (swatch) swatch.style.background = sel.value;
}

/** Settings page – load saved values into selects and swatches on page load. */
function initColorSettingsPage() {
    const overrides = loadColorSettings();
    document.querySelectorAll('select[data-role]').forEach(sel => {
        const saved = overrides[sel.dataset.role];
        if (saved) {
            // Try to select the matching option; fall back silently if not found.
            const opt = Array.from(sel.options).find(o => o.value === saved);
            if (opt) sel.value = saved;
        }
        // Inject a live swatch next to the select.
        const swatch = document.createElement('span');
        swatch.className = 'color-swatch';
        swatch.style.background = sel.value;
        sel.insertAdjacentElement('afterend', swatch);
    });
}

/** Export current localStorage settings as a downloaded JSON file. */
function exportColorSettings() {
    const overrides = loadColorSettings();
    const blob = new Blob([JSON.stringify(overrides, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'boxes-color-settings.json';
    a.click();
    URL.revokeObjectURL(a.href);
}

/** Import a JSON file and apply it – triggered by the hidden file input. */
function importColorSettings(input) {
    const file = input.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            const overrides = JSON.parse(e.target.result);
            persistColorSettings(overrides);
            // Reload to reflect the imported values in all selects.
            window.location.reload();
        } catch (_) {
            alert('Invalid JSON file.');
        }
    };
    reader.readAsText(file);
    // Reset so the same file can be re-imported if needed.
    input.value = '';
}

/** Settings page – clear localStorage and reload. */
function resetColorSettings() {
    localStorage.removeItem(COLOR_STORAGE_KEY);
    window.location.reload();
}

/** Inject color overrides as hidden inputs into a form so they travel with every submit. */
function injectColorHiddenFields(form) {
    form.querySelectorAll('input[data-color-override]').forEach(el => el.remove());
    const overrides = loadColorSettings();
    for (const [role, hex] of Object.entries(overrides)) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'color_' + role.toLowerCase();
        input.value = hex;
        input.setAttribute('data-color-override', '1');
        form.appendChild(input);
    }
}

/** Append color override params to a URL string. */
function appendColorParams(url) {
    const overrides = loadColorSettings();
    const params = Object.entries(overrides)
        .map(([role, hex]) => 'color_' + role.toLowerCase() + '=' + encodeURIComponent(hex))
        .join('&');
    if (!params) return url;
    return url + (url.includes('?') ? '&' : '?') + params;
}

/** Called once from initArgsPage – patch form submission and preview refresh. */
function initColorInjection() {
    const form = document.querySelector('#arguments');
    if (!form) return;
    injectColorHiddenFields(form);
    form.addEventListener('submit', () => injectColorHiddenFields(form));
}

/*** Gallery columns per row *****************************/

function applyGalleryCols(n) {
    // .container: width 996px border-box, padding 10px each side → content 976px.
    // Gallery lives in a 75%-wide float: floor(976 * 0.75) = 732px.
    // Each item has margin 5px each side = 10px total horizontal.
    const containerW = 732;
    const itemW = Math.floor((containerW - n * 10) / n);
    document.documentElement.style.setProperty('--gallery-item-width', itemW + 'px');
}

function setGalleryCols(n) {
    n = parseInt(n, 10) || 4;
    localStorage.setItem('gallery-cols', String(n));
    applyGalleryCols(n);
    const sel = document.getElementById('gallery-cols-select');
    if (sel) sel.value = String(n);
}

function initGalleryCols() {
    const saved = parseInt(localStorage.getItem('gallery-cols') || '4', 10);
    applyGalleryCols(saved);
    const sel = document.getElementById('gallery-cols-select');
    if (sel) sel.value = String(saved);
}

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
    initGalleryCols();
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
    initColorInjection();
    const i = document.querySelectorAll("td > input, td > select, td > textarea, td .stepper-input");
    for (let el of i) {
	el.addEventListener("change", refreshPreview);
    }
    refreshPreview();
    document.getElementById("preview_chk").addEventListener("change", togglePreview);
}

/*** Help modal *************************************************/

function openHelpModal(id) {
    const content = document.getElementById(id);
    document.getElementById('help-modal-content').innerHTML = content ? content.innerHTML : '';
    document.getElementById('help-modal').style.display = 'flex';
}

function closeHelpModal() {
    document.getElementById('help-modal').style.display = 'none';
}

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeHelpModal();
});

/*** Stepper buttons (FloatStepper / IntStepper) *****************/

/** Reset a stepper field to the sentinel string "auto". */
function setInputAuto(id) {
    const input = document.getElementById(id);
    input.value = "auto";
    input.dispatchEvent(new Event('change'));
}

function stepInput(id, delta, autoDefault) {
    const input = document.getElementById(id);
    const raw = input.value.trim().toLowerCase();
    // "auto" sentinel → start from autoDefault (if provided) before applying delta
    let base = (raw === "auto")
        ? (autoDefault !== undefined ? autoDefault : 0)
        : (parseFloat(raw) || 0);
    // Round to 4 decimal places to avoid float imprecision.
    const newVal = Math.round((base + delta) * 10000) / 10000;
    input.value = String(newVal);
    input.dispatchEvent(new Event('change'));
}

function stepInputInt(id, delta, autoDefault) {
    const input = document.getElementById(id);
    const raw = input.value.trim().toLowerCase();
    let base = (raw === "auto")
        ? (autoDefault !== undefined ? autoDefault : 0)
        : (parseInt(raw, 10) || 0);
    input.value = String(base + delta);
    input.dispatchEvent(new Event('change'));
}

/*** Preview ****************************************/

preview_scale=100;

function refreshPreview() {
    if (document.getElementById("preview_img").hidden)
	return;

    const form = document.querySelector("#arguments");
    const formData = new FormData(form);
    formData.set("format", "svg");

    let url = form.action + "?" + new URLSearchParams(formData).toString() + "&render=4";
    url = appendColorParams(url);

    const preview = document.getElementById("preview_img");
    preview.src = url;
}

function togglePreview() {
    document.getElementById("preview").hidden = !event.target.checked;
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
