import { createRequire } from "node:module";
import { mkdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const require = createRequire(new URL("../web/package.json", import.meta.url));
const { chromium } = require("@playwright/test");

const outputDir = fileURLToPath(new URL("../docs/screenshots/", import.meta.url));
await mkdir(outputDir, { recursive: true });

const browser = await chromium.launch();
const context = await browser.newContext({
  baseURL: "http://127.0.0.1:8000",
  viewport: { width: 1440, height: 1080 },
});
const page = await context.newPage();
page.setDefaultTimeout(30000);

try {
  console.log("Navigating to CONTEXT home...");
  await page.goto("/?dossier=test-artemis-investigation");
  await page.waitForLoadState("networkidle");

  // Verify dossier is rendered
  await page.waitForSelector(".dossier-hero");
  console.log("Dossier loaded!");

  // Screenshot 1: Overview & Findings
  await page.screenshot({
    path: `${outputDir}/01-investigation-overview.png`,
    fullPage: true,
  });
  console.log("Captured 01-investigation-overview.png");

  // Screenshot 2: Switch to Player & Timeline tab
  await page.click('button:has-text("02 Visual Player")');
  await page.waitForTimeout(1000);
  await page.screenshot({
    path: `${outputDir}/02-investigation-player.png`,
    fullPage: true,
  });
  console.log("Captured 02-investigation-player.png");

  // Screenshot 3: Switch to Claims & Fact-Check tab
  await page.click('button:has-text("03 Claims & Fact-Check")');
  await page.waitForTimeout(1000);
  await page.screenshot({
    path: `${outputDir}/03-investigation-claims.png`,
    fullPage: true,
  });
  console.log("Captured 03-investigation-claims.png");

  // Screenshot 4: Switch to Discovered Sources tab
  await page.click('button:has-text("04 Discovered Sources")');
  await page.waitForTimeout(1000);
  await page.screenshot({
    path: `${outputDir}/04-investigation-sources.png`,
    fullPage: true,
  });
  console.log("Captured 04-investigation-sources.png");

  // Screenshot 5: Switch to Epistemic Limits tab
  await page.click('button:has-text("05 Epistemic Limits")');
  await page.waitForTimeout(1000);
  await page.screenshot({
    path: `${outputDir}/05-investigation-epistemic-limits.png`,
    fullPage: true,
  });
  console.log("Captured 05-investigation-epistemic-limits.png");

  // Screenshot 6: Home state with launch form
  await page.goto("/");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(500);
  await page.screenshot({
    path: `${outputDir}/06-investigation-launch-home.png`,
    fullPage: true,
  });
  console.log("Captured 06-investigation-launch-home.png");

  console.log("All screenshots captured successfully in docs/screenshots/!");
} catch (err) {
  console.error("Error capturing screenshots:", err);
  process.exit(1);
} finally {
  await browser.close();
}
