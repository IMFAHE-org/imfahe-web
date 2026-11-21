const { chromium } = require("playwright");
const fs = require("node:fs");
const path = require("node:path");
const root = path.resolve(__dirname, "..");
const pages = JSON.parse(fs.readFileSync(path.join(root, "content/pages.json")));
const languages = Object.keys(JSON.parse(fs.readFileSync(path.join(root, "content/i18n.json"))));
// The first language is served from the site root; the others from /<code>/. A page without a translation is skipped.
const routes = languages.flatMap((code, index) => pages
  .filter((p) => index === 0 || fs.existsSync(path.join(root, "content", code, `${p.slug}.html`)))
  .map((p) => (index === 0 ? "" : `${code}/`) + p.route));
const host = process.argv[2] || "http://127.0.0.1:8823/";
const widthSet = [320, 390, 768, 1280];

(async () => {
  const browser = await chromium.launch({
    headless: true,
  });
  const page = await browser.newPage();
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  const stats = [];
  for (const width of widthSet) {
    await page.setViewportSize({ width, height: 900 });
    for (const route of routes) {
      const response = await page.goto(host + route, { waitUntil: "load" });
      if (response.status() !== 200) throw Error(`Bad route ${route}`);
      await page.evaluate(() => document.fonts.ready);
      const info = await page.evaluate(() => ({
        overflow: document.documentElement.scrollWidth > innerWidth,
        offScreen: [...document.querySelectorAll("body *")].flatMap((el) => {
          const box = el.getBoundingClientRect();
          return box.right > innerWidth + 1 && box.width
            ? [{ tag: el.tagName, className: el.getAttribute("class"), right: Math.round(box.right) }]
            : [];
        }).slice(0, 8),
        headings: document.querySelectorAll("main h1").length,
        headingJumps: [...document.querySelectorAll("main h1, main h2, main h3, main h4, main h5, main h6")]
          .map((heading) => Number(heading.tagName[1]))
          .some((level, index, levels) => index > 0 && level > levels[index - 1] + 1),
        missing: [...document.images].filter((i) => i.complete && !i.naturalWidth).length,
        filters: [...document.images].filter((i) => getComputedStyle(i).filter !== "none").length,
        initialBytes: performance.getEntriesByType("resource").reduce((sum, r) => sum + r.encodedBodySize, 0),
      }));
      if (info.overflow || info.headings !== 1 || info.headingJumps || info.missing || info.filters) {
        if (info.overflow) {
          const diagnostic = await page.evaluate(() => {
            const html = document.documentElement;
            const viewport = html.clientWidth;
            const candidates = [...document.querySelectorAll("body *")].flatMap((element) => {
              const bounds = element.getBoundingClientRect();
              if (!bounds.width) return [];
              if (bounds.right > viewport || element.scrollWidth > element.clientWidth + 1 && element.scrollWidth > viewport - bounds.left) {
                return [{tag: element.tagName, css: element.className, x: bounds.x, right: bounds.right,
                  scroll: element.scrollWidth, client: element.clientWidth, text: element.textContent.trim().slice(0, 40)}];
              }
              return [];
            }).slice(0, 20);
            const containers = [...document.querySelectorAll("body > *, main > *")];
            const without = containers.map((element) => {
              const style = element.style.display;
              element.style.display = "none";
              const width = html.scrollWidth;
              element.style.display = style;
              return {tag: element.tagName, css: element.className, id: element.id, width};
            });
            return {innerWidth, viewport, scrollWidth: html.scrollWidth, candidates, without};
          });
          console.error(JSON.stringify(diagnostic, null, 2));
        }
        throw Error(`${route || "/"} at ${width}: ${JSON.stringify(info)}`);
      }
      if (!route) stats.push({ width, ...info });
    }
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(host);
  const mobile = page.locator(".mobile-nav");
  await mobile.locator(":scope > summary").click();
  await mobile.getByText("Internationalization", { exact: true }).click();
  if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)) {
    throw Error("Expanded mobile menu causes horizontal overflow");
  }
  await mobile.getByRole("link", { name: "IMFAHE Connects" }).click();
  if (!page.url().endsWith("/imfahe-connects-program/")) throw Error("Mobile menu did not navigate");
  await page.goto(host);
  await page.route("https://www.youtube-nocookie.com/**", (route) => route.fulfill({ body: "<title>Test video</title>", contentType: "text/html" }));
  if (await page.locator("iframe").count()) throw Error("Video loaded before interaction");
  await page.getByRole("button", { name: "What is IMFAHE?" }).click();
  if (await page.locator("iframe.player").count() !== 1) throw Error("Video did not load on demand");
  await page.goto(host);
  await page.screenshot({ path: path.join(process.env.RUNNER_TEMP || ".", "imfahe-mobile.png") });
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.evaluate(() => document.fonts.ready);
  await page.locator(".media--mission img").evaluate((image) => image.decode());
  await page.screenshot({ path: path.join(process.env.RUNNER_TEMP || ".", "imfahe-desktop.png") });
  const programs = page.locator("#programs");
  const summary = programs.locator(".section-summary");
  const scales = await programs.evaluate((section) => {
    const title = section.querySelector("h2");
    const intro = section.querySelector("p.section-summary");
    const cardTitle = section.querySelector("h3");
    const size = (element) => parseFloat(getComputedStyle(element).fontSize);
    return {title: size(title), intro: size(intro), cardTitle: size(cardTitle), introWeight: getComputedStyle(intro).fontWeight};
  });
  if (!(scales.title > scales.cardTitle && scales.cardTitle > scales.intro && Number(scales.introWeight) <= 500)) {
    throw Error(`Invalid program section hierarchy: ${JSON.stringify(scales)}`);
  }
  await summary.scrollIntoViewIfNeeded();
  await programs.locator(".program-row img").first().evaluate((image) => image.decode());
  await programs.locator(".section-intro").first().screenshot({ path: path.join(process.env.RUNNER_TEMP || ".", "imfahe-programs-intro.png") });
  if (errors.length) throw Error(errors.join("\n"));
  console.log(JSON.stringify({ pageViewportChecks: routes.length * widthSet.length, mobileNavigation: "ok", onDemandVideo: "ok", home: stats }, null, 2));
  await browser.close();
})().catch((error) => { console.error(error); process.exit(1); });
