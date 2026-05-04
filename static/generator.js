/* ================================================================
   Boxes.py – Generator configuration page  (generator.js)
   ================================================================ */

/* Touch args page init */

/**
 * Called from the generator page onload.
 * numHide mirrors the same argument as initArgsPage().
 */
function initTouchArgs(numHide) {
    // Reuse the existing initArgsPage from self.js
    if (typeof initArgsPage === 'function') initArgsPage(numHide);

    // Wrap the global refreshPreview so bulk template loading can suppress it.
    _wrapRefreshPreview();

    // Wire preview_img load/error to remove the loading spinner.
    const img = document.getElementById('preview_img');
    if (img) {
        img.addEventListener('load',  _hidePreviewLoading);
        img.addEventListener('error', _hidePreviewLoading);
    }

    // Wire up the sticky action bar buttons
    _bindTouchActionBar();

    // Machine config panel (localStorage-backed)
    if (typeof initMachineConfigPanel === 'function') initMachineConfigPanel();

    // Auto-size inputs/selects if field-sizing:content is unsupported (Firefox < 128)
    if (!CSS.supports('field-sizing', 'content')) {
        _autoSizeAllFields();
    }
}

/* ----------------------------------------------------------------
   Preview loading state
   ---------------------------------------------------------------- */

/** Wrap the global refreshPreview once so a suppress flag can mute it. */
function _wrapRefreshPreview() {
    if (window._refreshPreviewWrapped) return;
    const orig = window.refreshPreview;
    if (typeof orig !== 'function') return;
    window.refreshPreview = function () {
        if (window._suppressPreview) return;
        _showPreviewLoading();
        orig.call(this);
    };
    window._refreshPreviewWrapped = true;
}

/** Add the loading spinner overlay to the preview area. */
function _showPreviewLoading() {
    const preview = document.getElementById('preview');
    if (preview) preview.classList.add('is-loading');
}

/** Remove the loading spinner (called on img load or error). */
function _hidePreviewLoading() {
    const preview = document.getElementById('preview');
    if (preview) preview.classList.remove('is-loading');
}

/* Generator params JSON export / import */

function saveParamsAsJson() {
    const form = document.querySelector('#arguments');
    if (!form) return;
    const data = {};
    new FormData(form).forEach((value, key) => {
        if (key !== 'render' && key !== 'language') data[key] = value;
    });
    // Also capture unchecked checkboxes (FormData omits them)
    form.querySelectorAll('input[type="checkbox"]').forEach(cb => {
        if (!cb.checked) data[cb.name] = 'false';
    });
    const name = (window.location.pathname.split('/').pop() || 'generator').replace(/\W/g, '_');
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = name + '-params.json';
    a.click();
    URL.revokeObjectURL(a.href);
}

function loadParamsFromJson(input) {
    const file = input.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            const data = JSON.parse(e.target.result);
            // Show spinner immediately, suppress per-field refreshes,
            // then fire a single refresh once all fields are set.
            _showPreviewLoading();
            window._suppressPreview = true;
            _applyParamsData(data);
            window._suppressPreview = false;
            if (typeof refreshPreview === 'function') refreshPreview();
        } catch (_) {
            alert('Invalid JSON file.');
        }
    };
    reader.readAsText(file);
    input.value = '';
}

/** Apply a plain {key: value} object to the #arguments form. */
function _applyParamsData(data) {
    const form = document.querySelector('#arguments');
    if (!form) return;
    for (const [key, value] of Object.entries(data)) {
        const el = form.querySelector(`[name="${CSS.escape(key)}"]`);
        if (!el) continue;
        if (el.type === 'checkbox') {
            el.checked = (value === true || value === 'true' || value === '1' || value === 'on');
        } else {
            el.value = value;
        }
        el.dispatchEvent(new Event('change'));
    }
}

/**
 * Load a template preset by index from the server-inlined GENERATOR_TEMPLATES array.
 * Suppresses per-field refreshPreview calls, shows the spinner, then fires one refresh.
 */
function applyTemplatePreset(idx) {
    if (idx === '' || idx === null || idx === undefined) return;
    const tpl = (typeof GENERATOR_TEMPLATES !== 'undefined') && GENERATOR_TEMPLATES[parseInt(idx, 10)];
    if (!tpl) return;

    // Show spinner immediately
    _showPreviewLoading();

    // Suppress the per-field change→refreshPreview calls during bulk apply
    window._suppressPreview = true;
    _applyParamsData(tpl.data);
    window._suppressPreview = false;

    // Single refresh now that all fields are set
    if (typeof refreshPreview === 'function') refreshPreview();
}

function _bindTouchActionBar() {
    // Buttons in .touch-action-bar have data-render attribute
    document.querySelectorAll('.touch-action-btn[data-render]').forEach(btn => {
        btn.addEventListener('click', function() {
            const renderVal = this.dataset.render;
            const target    = this.dataset.target || '_blank';
            const form = document.querySelector('#arguments');
            if (!form) return;

            // Temporarily set render + formtarget on a hidden input and submit
            let ri = form.querySelector('input[name="render"][data-touch]');
            if (!ri) {
                ri = document.createElement('input');
                ri.type = 'hidden';
                ri.name = 'render';
                ri.setAttribute('data-touch', '1');
                form.appendChild(ri);
            }
            ri.value = renderVal;
            const prevTarget = form.target;
            form.target = target;

            // Inject color overrides (from self.js)
            if (typeof injectColorHiddenFields === 'function') injectColorHiddenFields(form);

            form.submit();
            form.target = prevTarget;
        });
    });
}
