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

/* Category sidebar switching */

function thSwitchTab(groupId) {
    groupId = String(groupId);

    // Update sidebar nav items
    document.querySelectorAll('.th-sidenav-item').forEach(t => {
        const isActive = t.dataset.group === groupId;
        t.classList.toggle('active', isActive);
        t.setAttribute('aria-selected', isActive ? 'true' : 'false');
    });

    document.querySelectorAll('.th-panel').forEach(p => {
        const isActive = p.dataset.group === groupId;
        p.classList.toggle('active', isActive);
        p.style.display = isActive ? 'block' : 'none';
    });

    try { localStorage.setItem(TH_GROUP_KEY, groupId); } catch(_) {}

    // Re-apply current search filter to newly visible panel
    const q = (document.getElementById('th-search') || {}).value || '';
    thApplySearch(q.trim().toLowerCase());

    // On mobile, close the sidebar after selection
    thCloseSidebar();

    // Scroll active item into view in the sidebar
    const activeItem = document.querySelector('.th-sidenav-item.active');
    if (activeItem) activeItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/* Sidebar open / close (mobile) */

function thOpenSidebar() {
    document.body.classList.add('th-sidebar-open');
}

function thCloseSidebar() {
    document.body.classList.remove('th-sidebar-open');
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
 * Hide sidebar items and panels for categories the user has disabled.
 */
function applyHiddenCategoriesTouch() {
    const hidden = (typeof loadHiddenCategories === 'function')
        ? loadHiddenCategories()
        : new Set();

    document.querySelectorAll('.th-sidenav-item[data-group]').forEach(function(item) {
        item.style.display = hidden.has(item.dataset.group) ? 'none' : '';
    });
    document.querySelectorAll('.th-panel[data-group]').forEach(function(panel) {
        if (hidden.has(panel.dataset.group)) {
            panel.style.display = 'none';
            panel.classList.remove('active');
        }
    });

    // If the currently-active item is now hidden, jump to first visible one.
    const activeItem = document.querySelector('.th-sidenav-item.active');
    if (!activeItem || activeItem.style.display === 'none') {
        const first = document.querySelector('.th-sidenav-item[data-group]:not([style*="none"])');
        if (first) thSwitchTab(first.dataset.group);
    }
}

/* Hub init */

function initTouchHub() {
    // Record that we're in touch mode.
    setUIModePreference('touch');

    // Restore last active group.
    let lastGroup = null;
    try { lastGroup = localStorage.getItem(TH_GROUP_KEY); } catch(_) {}
    if (lastGroup !== null && document.querySelector(`.th-sidenav-item[data-group="${lastGroup}"]`)) {
        thSwitchTab(lastGroup);
    }

    applyHiddenCategoriesTouch();
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
