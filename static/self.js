/*** Dropdown menu ***************************************/

function toggleDropdown(event) {
    event.preventDefault();
    const dropdown = document.getElementById('main-dropdown');
    dropdown.classList.toggle('show');
}

// Close dropdown when clicking outside of it
document.addEventListener('click', function (event) {
    const dropdown = document.getElementById('main-dropdown');
    const dropdownBtn = document.querySelector('.dropdown-btn');
    if (dropdown && !event.target.closest('.dropdown')) {
        dropdown.classList.remove('show');
    }
});

// Close dropdown when a link is clicked
document.addEventListener('click', function (event) {
    if (event.target.closest('.dropdown-content a')) {
        const dropdown = document.getElementById('main-dropdown');
        if (dropdown) dropdown.classList.remove('show');
    }
});

/*** Args page tabs **************************************/

const TAB_STORAGE_KEY = 'boxes-active-tab';

function activateTab(name) {
    const panel = document.getElementById('tab-' + name);
    if (!panel) return;
    document.querySelectorAll('.tab-panel').forEach(p => {
        p.style.display = 'none';
    });
    panel.style.display = 'block';
    document.querySelectorAll('.tabbtn').forEach(b => {
        b.classList.toggle('active', (b.getAttribute('onclick') || '').includes("'" + name + "'"));
    });
}

function switchTab(evt, name) {
    activateTab(name);
    try {
        localStorage.setItem(TAB_STORAGE_KEY, name);
    } catch (_) {
    }
    if (name === 'configuration') refreshPreview();
}

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
        status._hideTimer = setTimeout(() => {
            status.style.display = 'none';
        }, 1500);
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
    const blob = new Blob([JSON.stringify(overrides, null, 2)], {type: 'application/json'});
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

/*** Category visibility *******************************/

const HIDDEN_CATS_KEY = 'boxes-hidden-categories';

function loadHiddenCategories() {
    try {
        return new Set(JSON.parse(localStorage.getItem(HIDDEN_CATS_KEY) || '[]'));
    } catch (_) {
        return new Set();
    }
}

/** Menu page: hide h3 + its content div for hidden categories. */
function applyHiddenCategoriesMenu() {
    const hidden = loadHiddenCategories();
    document.querySelectorAll('h3.toggle[data-id]').forEach(function (el) {
        const id = el.getAttribute('data-id');
        // Only process numeric category IDs; skip settings-group IDs (e.g. "g0", "g1")
        // to avoid overwriting the inline display:none we set for collapsed groups.
        if (!/^\d+$/.test(id)) return;
        const div = document.getElementById(id);
        const hide = hidden.has(id);
        el.style.display = hide ? 'none' : '';
        if (div) div.style.display = hide ? 'none' : '';
    });
}

/** Gallery page: hide .gallery-group divs for hidden categories. */
function applyHiddenCategoriesGallery() {
    const hidden = loadHiddenCategories();
    document.querySelectorAll('.gallery-group[data-group-id]').forEach(function (div) {
        div.style.display = hidden.has(div.dataset.groupId) ? 'none' : '';
    });
}

/** Apply hidden-category rules on whatever page is loaded. */
function applyHiddenCategories() {
    applyHiddenCategoriesMenu();
    applyHiddenCategoriesGallery();
}

/** Categories page – explicit Save button. */
function saveCategorySettingsExplicit() {
    const hidden = new Set();
    document.querySelectorAll('input[data-cat-id]').forEach(function (cb) {
        if (!cb.checked) hidden.add(cb.dataset.catId);
    });
    try {
        localStorage.setItem(HIDDEN_CATS_KEY, JSON.stringify([...hidden]));
    } catch (_) {
    }
    const home = (typeof CAT_HOME_URL !== 'undefined') ? CAT_HOME_URL : null;
    if (home) {
        window.location.href = home;
    } else {
        window.history.back();
    }
}

// Safety net: re-apply when the browser restores a page from bfcache.
window.addEventListener('pageshow', function (event) {
    if (event.persisted) {
        applyHiddenCategories();
        if (typeof applyHiddenCategoriesTouch === 'function') {
            applyHiddenCategoriesTouch();
        }
    }
});

/** Color settings page – explicit Save button. */
function saveColorSettingsExplicit() {
    const overrides = loadColorSettings();
    document.querySelectorAll('select[data-role]').forEach(function (sel) {
        overrides[sel.dataset.role] = sel.value;
    });
    persistColorSettings(overrides);
    window.history.back();
}

/** Categories page – init checkboxes from localStorage. */
function initCategorySettingsPage() {
    const hidden = loadHiddenCategories();
    document.querySelectorAll('input[data-cat-id]').forEach(function (cb) {
        cb.checked = !hidden.has(cb.dataset.catId);
    });
}

/** Categories page – called by each checkbox onchange. */
function onCategoryCheckboxChange(cb) {
    const hidden = loadHiddenCategories();
    if (cb.checked) {
        hidden.delete(cb.dataset.catId);
    } else {
        hidden.add(cb.dataset.catId);
    }
    try {
        localStorage.setItem(HIDDEN_CATS_KEY, JSON.stringify([...hidden]));
    } catch (_) {
    }
    const status = document.getElementById('cat-settings-status');
    if (status) {
        status.style.display = 'inline';
        clearTimeout(status._hideTimer);
        status._hideTimer = setTimeout(function () {
            status.style.display = 'none';
        }, 1500);
    }
}

/** Categories page – restore all categories. */
function resetCategorySettings() {
    try {
        localStorage.removeItem(HIDDEN_CATS_KEY);
    } catch (_) {
    }
    window.location.reload();
}

/*** Gallery image height zoom ****************************/

const GALLERY_ZOOM_DEFAULT = 120;
const GALLERY_ZOOM_STEP = 20;
const GALLERY_ZOOM_MIN = 60;
const GALLERY_ZOOM_MAX = 300;

function applyGalleryZoom(h) {
    document.documentElement.style.setProperty('--gallery-item-height', h + 'px');
}

function galleryZoomIn() {
    const cur = parseInt(localStorage.getItem('gallery-item-height') || String(GALLERY_ZOOM_DEFAULT), 10);
    const next = Math.min(cur + GALLERY_ZOOM_STEP, GALLERY_ZOOM_MAX);
    localStorage.setItem('gallery-item-height', String(next));
    applyGalleryZoom(next);
}

function galleryZoomOut() {
    const cur = parseInt(localStorage.getItem('gallery-item-height') || String(GALLERY_ZOOM_DEFAULT), 10);
    const next = Math.max(cur - GALLERY_ZOOM_STEP, GALLERY_ZOOM_MIN);
    localStorage.setItem('gallery-item-height', String(next));
    applyGalleryZoom(next);
}

function initGalleryCols() {
    const saved = parseInt(localStorage.getItem('gallery-item-height') || String(GALLERY_ZOOM_DEFAULT), 10);
    applyGalleryZoom(saved);
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
    applyHiddenCategories();
}

function initArgsPage(num_hide = null) {
    initPage(num_hide);
    initColorInjection();
    initDescriptionImages();
    const i = document.querySelectorAll("td > input, td > select, td > textarea, td .stepper-input");
    for (let el of i) {
        el.addEventListener("change", refreshPreview);
    }
    // Always start on the description tab (do not restore from localStorage).
    refreshPreview();
}

/*** Image modal *************************************************/

function openImgModal(src) {
    document.getElementById('img-modal-img').src = src;
    document.getElementById('img-modal').style.display = 'flex';
}

function closeImgModal() {
    document.getElementById('img-modal').style.display = 'none';
    document.getElementById('img-modal-img').src = '';
}

function initDescriptionImages() {
    document.querySelectorAll('#tab-description img').forEach(function (img) {
        img.addEventListener('click', function () {
            openImgModal(img.src);
        });
    });
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

document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        closeHelpModal();
        closeImgModal();
    }
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

/**
 * Move a text position by (dx, dy) * step, where step is read live from
 * the element whose id is stepId.  Called by DPadMoverArg arrow buttons.
 */
function dpadStep(xId, yId, stepId, dx, dy) {
    const step = parseFloat(document.getElementById(stepId).value) || 1.0;
    if (dx !== 0) stepInput(xId, dx * step);
    if (dy !== 0) stepInput(yId, dy * step);
}

/** Reset both offset fields to 0.  Called by the DPadMoverArg centre button. */
function dpadReset(xId, yId) {
    [xId, yId].forEach(id => {
        const el = document.getElementById(id);
        el.value = '0';
        el.dispatchEvent(new Event('change'));
    });
}

/*** Preview ****************************************/

preview_scale = 100;

function refreshPreview() {
    const form = document.querySelector("#arguments");
    const formData = new FormData(form);
    formData.set("format", "svg");

    let url = form.action + "?" + new URLSearchParams(formData).toString() + "&render=4";
    url = appendColorParams(url);

    const preview = document.getElementById("preview_img");
    preview.src = url;
    updateSurfaceInfo(url);
}

/*** Machine configuration ******************************/

const MACHINE_STORAGE_KEY = 'boxes-machine-config';

const KNOWN_MACHINES = [
    {brand: 'Ortur', model: 'Master 3', w: 400, h: 380},
    {brand: 'Ortur', model: 'H20 40W', w: 410, h: 275},
    {brand: 'xTool', model: 'M1 Ultra', w: 300, h: 300},
];

/** Available materials: { id, label, price_per_m2 } */
const MATERIALS = [
    {id: 'tilleul3', label: '3mm Tilleul', price_per_m2: 25},
    {id: 'noyer', label: '3mm Noyer', price_per_m2: 36},
];

const MACHINE_DEFAULTS = {w: 300, h: 300, material: '', margin_coef: 1};

function loadMachineConfig() {
    try {
        const saved = JSON.parse(localStorage.getItem(MACHINE_STORAGE_KEY) || 'null');
        return Object.assign({}, MACHINE_DEFAULTS, saved || {});
    } catch (_) {
        return Object.assign({}, MACHINE_DEFAULTS);
    }
}

function saveMachineConfig(w, h, material, margin_coef) {
    const cfg = loadMachineConfig();
    cfg.w = w;
    cfg.h = h;
    if (material !== undefined) cfg.material = material;
    if (margin_coef !== undefined) cfg.margin_coef = margin_coef;
    try {
        localStorage.setItem(MACHINE_STORAGE_KEY, JSON.stringify(cfg));
    } catch (_) {
    }
}

function initMachineConfigPanel() {
    const sel = document.getElementById('machine-preset');
    const wInput = document.getElementById('machine-w');
    const hInput = document.getElementById('machine-h');
    if (!sel || !wInput || !hInput) return;

    // Build <optgroup> options sorted by brand
    sel.innerHTML = '<option value="">\u2014 Custom \u2014</option>';
    const byBrand = {};
    for (const m of KNOWN_MACHINES) {
        (byBrand[m.brand] = byBrand[m.brand] || []).push(m);
    }
    for (const brand of Object.keys(byBrand).sort()) {
        const og = document.createElement('optgroup');
        og.label = brand;
        for (const m of byBrand[brand]) {
            const opt = document.createElement('option');
            opt.value = `${m.w}x${m.h}`;
            opt.textContent = `${m.model} (${m.w}\u00d7${m.h} mm)`;
            og.appendChild(opt);
        }
        sel.appendChild(og);
    }

    // Restore saved config
    const cfg = loadMachineConfig();
    wInput.value = cfg.w;
    hInput.value = cfg.h;
    _syncMachinePreset(sel, cfg.w, cfg.h);

    // Material selector
    const matSel = document.getElementById('machine-material');
    if (matSel) {
        matSel.innerHTML = '<option value="">Turn off material calculation</option>';
        for (const mat of MATERIALS) {
            const opt = document.createElement('option');
            opt.value = mat.id;
            opt.textContent = `${mat.label} (${mat.price_per_m2}\u20ac/m\u00b2)`;
            matSel.appendChild(opt);
        }
        matSel.value = cfg.material || '';
        matSel.addEventListener('change', function () {
            const w = parseFloat(wInput.value) || 300;
            const h = parseFloat(hInput.value) || 300;
            const coef = parseFloat(document.getElementById('machine-margin-coef')?.value || '1') || 1;
            saveMachineConfig(w, h, matSel.value, coef);
            _updatePriceInfo();
        });
    }

    // Margin coefficient
    const coefInput = document.getElementById('machine-margin-coef');
    if (coefInput) {
        coefInput.value = cfg.margin_coef !== undefined ? cfg.margin_coef : 1;
        coefInput.addEventListener('change', function () {
            const w = parseFloat(wInput.value) || 300;
            const h = parseFloat(hInput.value) || 300;
            const mat = matSel ? matSel.value : '';
            saveMachineConfig(w, h, mat, parseFloat(coefInput.value) || 1);
            _updatePriceInfo();
        });
    }

    sel.addEventListener('change', function () {
        if (!sel.value) return;
        const parts = sel.value.split('x');
        const w = Number(parts[0]);
        const h = Number(parts[1]);
        wInput.value = w;
        hInput.value = h;
        const mat = matSel ? matSel.value : '';
        const coef = parseFloat(coefInput?.value || '1') || 1;
        saveMachineConfig(w, h, mat, coef);
        _updateFitInfo();
    });

    const onDimChange = function () {
        const w = parseFloat(wInput.value) || 300;
        const h = parseFloat(hInput.value) || 300;
        const mat = matSel ? matSel.value : '';
        const coef = parseFloat(coefInput?.value || '1') || 1;
        saveMachineConfig(w, h, mat, coef);
        _syncMachinePreset(sel, w, h);
        _updateFitInfo();
    };
    wInput.addEventListener('change', onDimChange);
    hInput.addEventListener('change', onDimChange);
}

function _syncMachinePreset(sel, w, h) {
    for (const opt of sel.options) {
        if (opt.value === `${w}x${h}`) {
            sel.value = opt.value;
            return;
        }
    }
    sel.value = '';
}

/*** Surface info ***************************************/

let _svgDims = null;

async function updateSurfaceInfo(svgUrl) {
    const bar = document.getElementById('surface-info-bar');
    if (!bar) return;
    try {
        const resp = await fetch(svgUrl);
        if (!resp.ok) {
            _clearSurfaceInfo();
            return;
        }
        const text = await resp.text();
        const dims = _parseSvgMmDims(text);
        if (!dims) {
            _clearSurfaceInfo();
            return;
        }
        _svgDims = dims;
        const areaMm2 = dims.w * dims.h;
        const areaM2 = areaMm2 / 1_000_000;
        const areaStr = areaM2.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
        bar.innerHTML =
            `<span class="surf-dims">\ud83d\udcd0 ${dims.w.toFixed(1)} \u00d7 ${dims.h.toFixed(1)} mm</span>`
            + `<span class="surf-sep">\u2022</span>`
            + `<span class="surf-area">${areaStr} m\u00b2</span>`;
        bar.style.display = 'flex';
        _updateFitInfo();
        _updatePriceInfo();
    } catch (_) {
        _clearSurfaceInfo();
    }
}

function _parseSvgMmDims(svgText) {
    const m = svgText.match(/<svg\b[^>]*>/);
    if (!m) return null;
    const tag = m[0];
    const wm = tag.match(/\bwidth="([\d.]+)mm"/);
    const hm = tag.match(/\bheight="([\d.]+)mm"/);
    if (!wm || !hm) return null;
    const w = parseFloat(wm[1]);
    const h = parseFloat(hm[1]);
    return (isFinite(w) && isFinite(h) && w > 0 && h > 0) ? {w, h} : null;
}

function _clearSurfaceInfo() {
    _svgDims = null;
    const bar = document.getElementById('surface-info-bar');
    const fit = document.getElementById('fit-info-bar');
    const price = document.getElementById('price-info-bar');
    if (bar) bar.innerHTML = '';           // :empty CSS hides it
    if (fit) {
        fit.className = 'fit-info-bar';
        fit.textContent = '';
    }
    if (price) {
        price.innerHTML = '';
    }
}

function _updatePriceInfo() {
    const price = document.getElementById('price-info-bar');
    if (!price || !_svgDims) return;
    const cfg = loadMachineConfig();
    const matId = cfg.material || '';
    const margin = parseFloat(cfg.margin_coef) || 1;
    const mat = MATERIALS.find(m => m.id === matId);
    if (!mat) {
        price.innerHTML = '';
        return;
    }
    const areaM2 = (_svgDims.w * _svgDims.h) / 1_000_000;
    const total = areaM2 * mat.price_per_m2 * margin;
    const totalStr = total.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
    price.innerHTML =
        `<span class="surf-price-label">\ud83d\udcb6 ${mat.label}</span>`
        + `<span class="surf-sep">\u2022</span>`
        + `<span class="surf-price-value">${totalStr} \u20ac</span>`;
    price.style.display = 'flex';
}

function _updateFitInfo() {
    const fit = document.getElementById('fit-info-bar');
    if (!fit || !_svgDims) return;
    const cfg = loadMachineConfig();
    const mw = cfg.w, mh = cfg.h;
    const dw = _svgDims.w, dh = _svgDims.h;
    if (dw <= mw && dh <= mh) {
        fit.className = 'fit-info-bar fit-ok';
        fit.textContent = `\u2705 Fits on 1 sheet`;
    } else {
        const sw = Math.ceil(dw / mw);
        const sh = Math.ceil(dh / mh);
        const total = sw * sh;
        fit.className = 'fit-info-bar fit-warn';
        fit.textContent = `\u26a0\ufe0f Needs ${total} sheet${total > 1 ? 's' : ''} (${sw}\u00d7${sh} grid)`;
    }
    fit.style.display = 'flex';
    _updatePriceInfo();
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
    x = nx * 42 - margin
    y = ny * 42 - margin
    layout_id = document.getElementById('layout');
    layout_id.value = GridfinityTrayLayout_GenerateLayout(x, y, nx, ny, countx, county);
}

function setUpdated() {
    console.log("this was updated");
    window.layoutUpdated = true;
}

function GridfinityTrayLayoutInit() {
    console.log("update init");
    ids = ['nx', 'ny', 'countx', 'county', 'margin'];
    window.layoutUpdated = false;
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
    const disc = b ** 2 - 4 * a * c;
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
            for (var i = 0; i < operands[1]; i++) {
                sections.push(Number(operands[0]) / Number(operands[1]));
            }
            continue;
        }
        operands = section.split("*");
        if (operands.length > 2) return sections;
        if (operands.length == 2) {
            for (var i = 0; i < operands[1]; i++) {
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
    window.layoutUpdated = false;
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
    page = pathname.substr(pathname.lastIndexOf('/') + 1);
    if (page in page_callbacks) {
        callback = page_callbacks[page];
        callback();
    }
}

/*** Search for generators **************************************/

document.addEventListener('DOMContentLoaded', function () {
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
        applyHiddenCategories();
    } else {
        expandAll();
        showOnly(search.value)
    }
}
