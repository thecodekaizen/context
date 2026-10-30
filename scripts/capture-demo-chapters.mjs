import { existsSync } from "node:fs";
import { createRequire } from "node:module";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { performance } from "node:perf_hooks";
import { spawnSync } from "node:child_process";

const require = createRequire(new URL("../web/package.json", import.meta.url));
const { chromium, expect } = require("@playwright/test");

const root = fileURLToPath(new URL("../", import.meta.url));
const assets = root + "demo-video/assets/";
const story = JSON.parse(await readFile(root + "demo-video/story.json", "utf8"));

await mkdir(assets, { recursive: true });
await mkdir(assets + "raw", { recursive: true });

const browser = await chromium.launch();
const report = [];

async function record(chapter, action) {
  const targetMp4 = assets + chapter.id + ".mp4";
  if (existsSync(targetMp4)) {
    console.log(`✓ Reusing existing ${chapter.id}.mp4`);
    report.push({ chapter: chapter.id, duration: chapter.duration, output: targetMp4 });
    return;
  }
  console.log(`Recording chapter: ${chapter.id} (${chapter.duration}s)...`);

  const ctx = await browser.newContext({
    baseURL: "http://127.0.0.1:8000",
    viewport: { width: 1440, height: 900 },
    recordVideo: { dir: assets + "raw", size: { width: 1440, height: 900 } },
    acceptDownloads: true,
  });

  const page = await ctx.newPage();
  page.setDefaultTimeout(30000);
  const began = performance.now();
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));

  try {
    await action(page);
    const elapsed = (performance.now() - began) / 1000;
    const remaining = Math.max(0, (chapter.duration + 0.5) - elapsed);
    if (remaining > 0) {
      await page.waitForTimeout(remaining * 1000);
    }
    if (errors.length) console.warn("Page errors:", errors.join("; "));

    await page.screenshot({ path: assets + chapter.id + ".png" });
    const raw = await page.video().path();
    await ctx.close();

    const conversion = spawnSync(
      "ffmpeg",
      [
        "-v", "error", "-y",
        "-ss", "0.5",
        "-i", raw,
        "-vf", "tpad=stop_mode=clone:stop_duration=1",
        "-t", String(chapter.duration + 0.5),
        "-c:v", "libx264", "-crf", "20",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-an",
        targetMp4,
      ],
      { encoding: "utf8" }
    );
    if (conversion.status !== 0) throw new Error(conversion.stderr);

    report.push({ chapter: chapter.id, duration: chapter.duration, output: targetMp4 });
    console.log(`✓ Captured ${chapter.id}.mp4 successfully`);
  } catch (err) {
    await ctx.close();
    throw err;
  }
}

try {
  // Capture Hero image for Intro
  const introCtx = await browser.newContext({
    baseURL: "http://127.0.0.1:8000",
    viewport: { width: 1440, height: 900 },
  });
  const introPage = await introCtx.newPage();
  await introPage.goto("/");
  await introPage.waitForSelector("header");
  await introPage.waitForTimeout(1000);
  await introPage.screenshot({ path: assets + "hero.png" });
  await introCtx.close();
  console.log("✓ Captured hero.png for intro");

  // Chapter 1: dossier (40s)
  // Single-video investigation: Artemis I uncrewed vs false caption
  await record(story[1], async (page) => {
    await page.goto("/?dossier=artemis-captioned-omission");
    await page.waitForSelector(".dossier-hero");
    await page.waitForTimeout(4000);

    // Scroll to overview findings
    await page.locator(".dossier-metrics").scrollIntoViewIfNeeded();
    await page.waitForTimeout(6000);

    // Switch to Claims & Fact-Check
    await page.click('button:has-text("03 Claims & Fact-Check")');
    await expect(page.locator(".claims-section")).toBeVisible();
    await page.waitForTimeout(8000);

    // Switch to Discovered Sources
    await page.click('button:has-text("04 Discovered Sources")');
    await expect(page.locator(".sources-section")).toBeVisible();
    await page.waitForTimeout(8000);

    // Return to overview
    await page.click('button:has-text("01 Overview & Dossier")');
    await page.waitForTimeout(4000);
  });

  // Chapter 2: reveal (35s)
  // Synchronized Dual-Player Missing Context Reveal
  await record(story[2], async (page) => {
    await page.goto("/?dossier=artemis-captioned-omission");
    await page.waitForSelector(".matched-source-banner");
    await page.waitForTimeout(3000);

    // Click button to reveal missing context in dual player
    await page.locator(".btn-open-dual-comparator").click();
    await expect(page.locator(".workbench")).toBeVisible();
    await page.waitForTimeout(4000);

    // Scrub video
    const video = page.locator("video").first();
    await video.evaluate((v) => {
      v.currentTime = 4;
      v.play();
    });
    await page.waitForTimeout(10000);
    await video.evaluate((v) => v.pause());

    // Highlight timeline segment
    await page.locator(".timeline").first().scrollIntoViewIfNeeded();
    await page.waitForTimeout(6000);
  });

  // Chapter 3: abstention (35s)
  // Epistemic honesty & harmless edit discrimination
  await record(story[3], async (page) => {
    await page.goto("/?dossier=artemis-captioned-omission");
    await page.waitForSelector(".dossier-nav");
    await page.waitForTimeout(3000);

    // Click Epistemic Limits & Uncertainty tab
    await page.click('button:has-text("05 Epistemic Limits")');
    await expect(page.locator(".boundaries-section")).toBeVisible();
    await page.waitForTimeout(8000);

    // Highlight honest abstention policies
    await page.locator(".boundary-card").first().scrollIntoViewIfNeeded();
    await page.waitForTimeout(8000);

    // Show Copy Markdown Brief interaction
    const copyBtn = page.locator('button:has-text("Copy Markdown Brief")');
    if (await copyBtn.isVisible()) {
      await copyBtn.click();
      await page.waitForTimeout(4000);
    }
  });

  // Chapter 4: prelude (30s)
  // PRELUDE anticipatory roadway hazards
  await record(story[4], async (page) => {
    await page.goto("/");
    await page.waitForSelector("header");
    await page.waitForTimeout(2000);

    // Switch to PRELUDE lens
    await page.click('button:has-text("Anticipate Roadway Hazards")');
    await expect(page.locator(".prelude-studio")).toBeVisible();
    await page.waitForTimeout(4000);

    // Select the first dashcam scenario (near_crash_011)
    await page.locator(".sample-chip").first().click();
    await page.waitForTimeout(3000);

    // Scroll to telemetry and risk indicators
    await page.locator(".hero-risk-panel").scrollIntoViewIfNeeded();
    await page.waitForTimeout(8000);

    // Show timeline window and lead time tag
    await page.locator(".prelude-timeline-track").scrollIntoViewIfNeeded();
    await page.waitForTimeout(6000);
  });

  await writeFile(
    assets + "capture-report.json",
    JSON.stringify(
      {
        timestamp: new Date().toISOString(),
        story: "CONTEXT Single-Video Multimodal Studio 3-Minute Walkthrough",
        report,
      },
      null,
      2
    )
  );

  console.log("\n=======================================================");
  console.log("ALL CHAPTERS CAPTURED SUCCESSFULLY!");
  console.log("=======================================================");
} finally {
  await browser.close();
}
