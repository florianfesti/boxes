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
    };
    loc = new URL(window.location.href);
    pathname = loc.pathname;
    page = pathname.substr(pathname.lastIndexOf('/')+1);
    if (page in page_callbacks) {
        callback = page_callbacks[page];
        callback();
    }
}

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
