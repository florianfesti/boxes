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


function toggleId(id) {
    const e = document.getElementById(id);
    const h = document.getElementById("h-" + id);
    if (e.style.display == null || e.style.display === "none") {
        e.style.display = "block";
        h.classList.add("open");
        h.setAttribute("aria-expanded", "true");
    } else {
        e.style.display = "none";
        h.classList.remove("open");
        h.setAttribute("aria-expanded", "false");
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