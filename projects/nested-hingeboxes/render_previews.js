// Render the cut sheets in this folder to PNG previews in previews/, and screenshot
// the 3D model (model.html) to previews/model.png.
// Needs Playwright with Chromium:  node projects/nested-hingeboxes/render_previews.js
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const here = __dirname;
const files = [];
for (const n of [6, 8, 9, 10, 12]) files.push(`sheets/sheets${n}.svg`, `layouts/sheets${n}.svg`);

(async () => {
  fs.mkdirSync(path.join(here, "previews"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1400, height: 800 } });
  for (const f of files) {
    const svg = fs.readFileSync(path.join(here, f), "utf8");
    await page.setContent(
      `<html><body style="margin:0;background:#fff">` +
      `<div style="width:1400px">${svg.replace(/<\?xml[^>]*>/, "")}</div></body></html>`);
    // scale the SVG to 1400 px wide, keeping its aspect ratio
    await page.evaluate(() => {
      const s = document.querySelector("svg");
      s.setAttribute("width", "1400");
      s.removeAttribute("height");
      s.style.display = "block";
    });
    const name = (f.startsWith("layouts/") ? "layout-" : "") + path.basename(f);
    const out = path.join(here, "previews", name.replace(/\.svg$/, ".png"));
    await page.locator("svg").screenshot({ path: out });
    console.log(out);
  }
  await browser.close();
  await renderModel();
})();

// The boxes side by side with their lids open, as model.html shows them.
async function renderModel() {
  const browser = await chromium.launch({ args: ["--use-gl=angle", "--enable-unsafe-swiftshader"] });
  const page = await browser.newPage({ viewport: { width: 1500, height: 760 }, deviceScaleFactor: 2 });
  await page.goto("file://" + path.join(here, "model.html"));
  await page.waitForSelector("#loading", { state: "hidden", timeout: 60000 });
  await page.click("#view-row");
  await page.$eval("#lid", el => {
    el.value = 100;
    el.dispatchEvent(new Event("input", { bubbles: true }));
  });
  await page.click("#reset");
  // zoom in a little from the fitted view, then move the mouse off the boxes
  const stage = await page.locator("#stage").boundingBox();
  await page.mouse.move(stage.x + stage.width / 2, stage.y + stage.height / 2);
  for (let i = 0; i < 3; i++) {
    await page.mouse.wheel(0, -100);
    await page.waitForTimeout(150);
  }
  await page.mouse.move(stage.x + 5, stage.y + 5);
  await page.waitForTimeout(1000);
  const out = path.join(here, "previews", "model.png");
  await page.screenshot({ path: out, clip: { x: stage.x + 250, y: stage.y + 180, width: 860, height: 440 } });
  console.log(out);
  await browser.close();
}
