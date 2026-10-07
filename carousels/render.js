// Renders every <section class="slide"> in carousels.html to out/<id>.png (1080x1350).
//   node render.js
const { chromium } = require("playwright");
const path = require("path");

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  await page.goto("file://" + path.join(__dirname, "carousels.html"));
  await page.evaluate(() => document.fonts.ready);
  const ids = await page.$$eval("section.slide", (els) => els.map((e) => e.id));
  for (const id of ids) {
    await page.locator("#" + id).screenshot({ path: path.join(__dirname, "out", id + ".png") });
    console.log("rendered", id);
  }
  await browser.close();
})();
