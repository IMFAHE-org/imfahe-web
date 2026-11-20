const { chromium } = require("playwright");
const fs = require("node:fs");
const path = require("node:path");
const root = path.resolve(__dirname, "..");
const routes = JSON.parse(fs.readFileSync(path.join(root, "content/pages.json"))).map((p) => p.route);
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
      const info = await page.evaluate(() => ({
        overflow: document.documentElement.scrollWidth > innerWidth,
        offScreen: [...document.querySelectorAll("body *")].flatMap((el) => {
          const box = el.getBoundingClientRect();
          return box.right > innerWidth + 1 && box.width
            ? [{ tag: el.tagName, className: el.getAttribute("class"), right: Math.round(box.right) }]
            : [];
        }).slice(0, 8),
        headings: document.querySelectorAll("main h1").length,
        missing: [...document.images].filter((i) => i.complete && !i.naturalWidth).length,
        filters: [...document.images].filter((i) => getComputedStyle(i).filter !== "none").length,
        initialBytes: performance.getEntriesByType("resource").reduce((sum, r) => sum + r.encodedBodySize, 0),
      }));
      if (info.overflow || info.headings !== 1 || info.missing || info.filters) {
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
  await page.screenshot({ path: path.join(process.env.RUNNER_TEMP || ".", "imfahe-desktop.png") });
  if (errors.length) throw Error(errors.join("\n"));
  console.log(JSON.stringify({ pageViewportChecks: routes.length * widthSet.length, mobileNavigation: "ok", onDemandVideo: "ok", home: stats }, null, 2));
  await browser.close();
})().catch((error) => { console.error(error); process.exit(1); });
