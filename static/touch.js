/* ================================================================
   Boxes.py – Touch / Tablet UI  (touch.js)
   ================================================================ */

const UI_MODE_KEY   = 'boxes-ui-mode';
const TH_GROUP_KEY  = 'th-active-group';

/* Mode preference (localStorage) */

function getUIModePreference() {
    try { return localStorage.getItem(UI_MODE_KEY); } catch(_) { return null; }
}
function setUIModePreference(mode) {
    try { localStorage.setItem(UI_MODE_KEY, mode); } catch(_) {}
}

function thBuildModeSwitchUrl(path) {
    const params = new URLSearchParams(window.location.search);
    const language = params.get('language');

    if (!language) return path;

    const targetParams = new URLSearchParams();
    targetParams.set('language', language);
    return path + '?' + targetParams.toString();
}

/** Switch to classic (legacy) mode: save pref and go to Menu. */
function thSwitchToLegacy() {
    setUIModePreference('legacy');
    window.location.href = thBuildModeSwitchUrl('Menu');
}

/** Switch to touch mode from any classic page. */
function thSwitchToTouch() {
    setUIModePreference('touch');
    window.location.href = thBuildModeSwitchUrl('TouchHub');
}

/* Category tab switching */

function thSwitchTab(groupId) {
    groupId = String(groupId);

    document.querySelectorAll('.th-tab').forEach(t => {
        const isActive = t.dataset.group === groupId;
        t.classList.toggle('active', isActive);
        t.setAttribute('aria-selected', isActive ? 'true' : 'false');
    });

    document.querySelectorAll('.th-panel').forEach(p => {
        const isActive = p.dataset.group === groupId;
        p.classList.toggle('active', isActive);
        p.style.display = isActive ? 'block' : 'none';
    });

    // Sync dropdown select
    const sel = document.getElementById('th-tab-select');
    if (sel) sel.value = groupId;

    try { localStorage.setItem(TH_GROUP_KEY, groupId); } catch(_) {}

    // Re-apply current search filter to newly visible panel
    const q = (document.getElementById('th-search') || {}).value || '';
    thApplySearch(q.trim().toLowerCase());

    // Scroll tab into view (horizontal tab bar)
    const activeTab = document.querySelector('.th-tab.active');
    if (activeTab) activeTab.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
}

/* Search / filter */

function thFilterSearch() {
    const q = (document.getElementById('th-search').value || '').trim().toLowerCase();
    thApplySearch(q);
}

function thApplySearch(q) {
    const activePanel = document.querySelector('.th-panel.active');
    if (!activePanel) return;

    let visible = 0;
    activePanel.querySelectorAll('.th-card').forEach(card => {
        const text = (card.textContent || '').toLowerCase();
        const show = !q || text.includes(q);
        card.style.display = show ? '' : 'none';
        if (show) visible++;
    });

    // Show / hide no-results placeholder
    let noRes = activePanel.querySelector('.th-no-results');
    if (q && visible === 0) {
        if (!noRes) {
            noRes = document.createElement('p');
            noRes.className = 'th-no-results';
            activePanel.appendChild(noRes);
        }
        noRes.textContent = 'No results for "' + q + '"';
    } else if (noRes) {
        noRes.remove();
    }
}

/* Category visibility (shared with self.js HIDDEN_CATS_KEY) */

/**
 * Hide tabs and panels for categories the user has disabled.
 * Falls back gracefully if loadHiddenCategories (self.js) is unavailable.
 */
function applyHiddenCategoriesTouch() {
    const hidden = (typeof loadHiddenCategories === 'function')
        ? loadHiddenCategories()
        : new Set();

    document.querySelectorAll('.th-tab[data-group]').forEach(function(tab) {
        tab.style.display = hidden.has(tab.dataset.group) ? 'none' : '';
    });
    document.querySelectorAll('.th-panel[data-group]').forEach(function(panel) {
        if (hidden.has(panel.dataset.group)) {
            panel.style.display = 'none';
            panel.classList.remove('active');
        }
    });

    // If the currently-active tab is now hidden, jump to first visible one.
    const activeTab = document.querySelector('.th-tab.active');
    if (!activeTab || activeTab.style.display === 'none') {
        const first = document.querySelector('.th-tab[data-group]:not([style*="none"])');
        if (first) thSwitchTab(first.dataset.group);
    }

    thCheckTabbarOverflow();
}

/**
 * Rebuild the <select> options from currently-visible .th-tab buttons,
 * then check whether the tabs overflow a single row and switch to dropdown mode.
 */
function thCheckTabbarOverflow() {
    const bar = document.querySelector('.th-tabbar');
    const sel = document.getElementById('th-tab-select');
    if (!bar || !sel) return;

    // Rebuild select options from visible tabs
    const currentVal = sel.value;
    sel.innerHTML = '';
    document.querySelectorAll('.th-tab[data-group]').forEach(tab => {
        if (tab.style.display === 'none') return;
        const opt = document.createElement('option');
        opt.value = tab.dataset.group;
        const label = tab.querySelector('.th-tab-label');
        const count = tab.querySelector('.th-tab-count');
        opt.textContent = (label ? label.textContent : tab.title)
            + (count ? ' (' + count.textContent + ')' : '');
        if (tab.classList.contains('active')) opt.selected = true;
        sel.appendChild(opt);
    });
    // Restore previous value if still present
    if (currentVal && sel.querySelector(`option[value="${currentVal}"]`)) {
        sel.value = currentVal;
    }

    // Temporarily remove max-height + overflow to measure real scroll height
    const savedMax   = bar.style.maxHeight;
    const savedOvfl  = bar.style.overflow;
    bar.style.maxHeight = 'none';
    bar.style.overflow  = 'visible';
    // Remove dropdown class so tabs are visible for measurement
    bar.classList.remove('th-tabbar--dropdown');

    const tapMin = parseFloat(
        getComputedStyle(document.documentElement).getPropertyValue('--th-tap-min')
    ) || 52;
    const overflows = bar.scrollHeight > tapMin + 4;

    bar.style.maxHeight = savedMax;
    bar.style.overflow  = savedOvfl;

    bar.classList.toggle('th-tabbar--dropdown', overflows);
}

/* Hub init */

function initTouchHub() {
    // Record that we're in touch mode.
    setUIModePreference('touch');

    // Restore last active group.
    let lastGroup = null;
    try { lastGroup = localStorage.getItem(TH_GROUP_KEY); } catch(_) {}
    if (lastGroup !== null && document.querySelector(`.th-tab[data-group="${lastGroup}"]`)) {
        thSwitchTab(lastGroup);
    }

    applyHiddenCategoriesTouch();

    // Re-check tab overflow when window is resized
    if (typeof ResizeObserver !== 'undefined') {
        const bar = document.querySelector('.th-tabbar');
        if (bar) new ResizeObserver(thCheckTabbarOverflow).observe(bar);
    } else {
        window.addEventListener('resize', thCheckTabbarOverflow);
    }
}

/* field-sizing fallback (Firefox / Safari) */

const _sizeCanvas = document.createElement('canvas');

function _measureText(el, text) {
    const ctx = _sizeCanvas.getContext('2d');
    const cs  = getComputedStyle(el);
    ctx.font  = cs.fontSize + ' ' + cs.fontFamily;
    return ctx.measureText(text).width;
}

function _autoSizeField(el) {
    const MIN = 70;
    const PAD = el.tagName === 'SELECT' ? 44 : 24; // selects need extra room for native arrow
    let text = '';
    if (el.tagName === 'SELECT') {
        text = el.options[el.selectedIndex] ? el.options[el.selectedIndex].text : '';
    } else {
        text = el.value || el.placeholder || '';
    }
    const w = Math.max(MIN, Math.ceil(_measureText(el, text)) + PAD);
    el.style.width = w + 'px';
}

function _autoSizeAllFields() {
    const sel = 'body.touch-args table input[type="text"], body.touch-args table select';
    document.querySelectorAll(sel).forEach(el => {
        _autoSizeField(el);
        el.addEventListener('change', () => _autoSizeField(el));
        el.addEventListener('input',  () => _autoSizeField(el));
    });
}
