import { createRequire } from "node:module";
import { mkdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const require = createRequire(new URL("../web/package.json", import.meta.url));
const { chromium } = require("@playwright/test");

const root = fileURLToPath(new URL("../", import.meta.url));
const outDir = root + "docs/screenshots/";
await mkdir(outDir, { recursive: true });

const browser = await chromium.launch();

async function run() {
  const ctx = await browser.newContext({
    baseURL: "http://127.0.0.1:8000",
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 2, // HiDPI / 2x Retina quality
  });
  const page = await ctx.newPage();
  page.setDefaultTimeout(30000);

  console.log("1. Capturing Intake & Workbench Home...");
  await page.goto("/");
  await page.waitForSelector("header");
  await page.waitForTimeout(1500);
  await page.screenshot({ path: outDir + "01-workbench-intake.png", fullPage: false });
  console.log("✓ Saved 01-workbench-intake.png");

  console.log("2. Capturing Dual-Player Omission Scrubber...");
  const benchBtn = page.locator('button:has-text("Try benchmark omission →")');
  if (await benchBtn.isVisible()) {
    await benchBtn.click();
  } else {
    await page.click('button:has-text("Try controlled benchmark →")');
  }
  await page.waitForSelector(".workbench");
  await page.waitForTimeout(2000);

  // Scroll to workbench
  await page.locator(".workbench").scrollIntoViewIfNeeded();
  await page.waitForTimeout(1000);

  // Set video time to 3.5s to expose the 5.0s - 10.0s omission
  const videos = page.locator("video");
  if ((await videos.count()) >= 1) {
    await videos.first().evaluate((v) => {
      v.currentTime = 3.5;
      v.pause();
    });
    await page.waitForTimeout(2000);
  }

  // Expand finding if present
  const finding = page.locator(".finding-item").first();
  if (await finding.isVisible()) {
    await finding.click();
    await page.waitForTimeout(1000);
  }

  await page.screenshot({ path: outDir + "02-dual-player-omission.png", fullPage: false });
  console.log("✓ Saved 02-dual-player-omission.png");

  console.log("3. Capturing Spatial Crop & SAM 3.1 Inspector...");
  await page.goto("/");
  await page.waitForSelector("header");
  await page.waitForTimeout(1000);
  const cropBtn = page.locator('button:has-text("Try spatial crop demo →")');
  if (await cropBtn.isVisible()) {
    await cropBtn.click();
    await page.waitForSelector(".workbench");
    await page.waitForTimeout(2500);
    const cropSection = page.locator(".crop-section, .comparison, .workbench");
    await cropSection.first().scrollIntoViewIfNeeded();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: outDir + "03-spatial-crop-sam.png", fullPage: false });
    console.log("✓ Saved 03-spatial-crop-sam.png");
  }

  console.log("4. Capturing Benchmark & Evaluation Matrix Hub...");
  await page.goto("/");
  await page.waitForSelector("header");
  await page.waitForTimeout(1000);
  const evalTab = page.locator("#btn-nav-benchmark");
  if (await evalTab.isVisible()) {
    await evalTab.click();
  }
  await page.waitForSelector(".benchmark-hub-section");
  await page.waitForTimeout(2500);

  const table = page.locator(".benchmark-table-wrapper");
  if (await table.isVisible()) {
    await table.scrollIntoViewIfNeeded();
    await page.waitForTimeout(1000);
  }

  await page.screenshot({ path: outDir + "04-evaluation-matrix.png", fullPage: false });
  console.log("✓ Saved 04-evaluation-matrix.png");

  await ctx.close();
  await browser.close();
  console.log("All 4 screenshots captured successfully!");
}

run().catch((err) => {
  console.error("Capture failed:", err);
  process.exit(1);
});
