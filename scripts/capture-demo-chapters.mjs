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
    const remaining = Math.max(0, chapter.duration + 0.5 - elapsed);
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
        "-v",
        "error",
        "-y",
        "-ss",
        "0.5",
        "-i",
        raw,
        "-vf",
        "tpad=stop_mode=clone:stop_duration=1",
        "-t",
        String(chapter.duration + 0.5),
        "-c:v",
        "libx264",
        "-crf",
        "20",
        "-preset",
        "fast",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
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

  // Chapter 1: problem (30s)
  // Architecture rule: deterministic aligner first, evidence contract JSON, no political domain
  await record(story[1], async (page) => {
    await page.goto("/");
    await page.waitForSelector("header");
    await page.waitForTimeout(3000);

    // Focus on header and architecture statement
    const introSection = page.locator(".intro");
    await introSection.scrollIntoViewIfNeeded();
    await page.waitForTimeout(6000);

    // Highlight the "Compare Two Footages" input box
    const uploadBox = page.locator(".upload");
    await uploadBox.scrollIntoViewIfNeeded();
    await page.waitForTimeout(6000);
  });

  // Chapter 2: live_run (55s)
  // Live dual-player run: click "Try benchmark omission →", scrub 5-10s crash, review card
  await record(story[2], async (page) => {
    await page.goto("/");
    await page.waitForSelector("header");
    await page.waitForTimeout(2000);

    // Click "Try benchmark omission →"
    const btn = page.locator('button:has-text("Try benchmark omission →")');
    if (await btn.isVisible()) {
      await btn.click();
    } else {
      await page.click('button:has-text("Try controlled benchmark →")');
    }

    // Wait for analysis and workbench
    await page.waitForSelector(".workbench");
    await page.waitForTimeout(2000);

    // Scroll dual player into view
    const workbench = page.locator(".workbench");
    await workbench.scrollIntoViewIfNeeded();
    await page.waitForTimeout(3000);

    // Scrub video into omission cut (seconds 5 to 10)
    const videos = page.locator("video");
    const count = await videos.count();
    if (count >= 1) {
      await videos.first().evaluate((v) => {
        v.currentTime = 3.5;
        v.play();
      });
      await page.waitForTimeout(8000);
      await videos.first().evaluate((v) => v.pause());
    }

    // Scroll to findings cards and click omission reveal
    const findings = page.locator(".finding-item");
    if ((await findings.count()) > 0) {
      await findings.first().scrollIntoViewIfNeeded();
      await page.waitForTimeout(4000);
      await findings.first().click();
      await page.waitForTimeout(6000);
    }
  });

  // Chapter 3: sam_crop (30s)
  // Spatial crop & reframe detector with SAM 3.1: show SVG crop box & red margins
  await record(story[3], async (page) => {
    await page.goto("/");
    await page.waitForSelector("header");
    await page.waitForTimeout(2000);

    // Click "Try spatial crop demo →"
    const cropBtn = page.locator('button:has-text("Try spatial crop demo →")');
    if (await cropBtn.isVisible()) {
      await cropBtn.click();
      await page.waitForSelector(".workbench");
      await page.waitForTimeout(3000);

      // Scroll to dual player to highlight SVG bounding box and red shaded margins
      const workbench = page.locator(".workbench");
      await workbench.scrollIntoViewIfNeeded();
      await page.waitForTimeout(7000);

      const cropCard = page.locator(".crop-analysis-card");
      if (await cropCard.isVisible()) {
        await cropCard.scrollIntoViewIfNeeded();
        await page.waitForTimeout(7000);
      }
    } else {
      await page.waitForTimeout(10000);
    }
  });

  // Chapter 4: evaluation (25s)
  // Frozen 30-edit benchmark results: 100% recall, 0.0s boundary error, 0% false alarms
  await record(story[4], async (page) => {
    await page.goto("/");
    await page.waitForSelector("header");
    await page.waitForTimeout(1500);

    // Switch to Benchmark & Evaluation Hub
    const evalTab = page.locator("#btn-nav-benchmark");
    if (await evalTab.isVisible()) {
      await evalTab.click();
    }
    await page.waitForSelector(".benchmark-hub-section");
    await page.waitForTimeout(3000);

    // Scroll to metrics cards and table
    const table = page.locator(".benchmark-table-wrapper");
    if (await table.isVisible()) {
      await table.scrollIntoViewIfNeeded();
      await page.waitForTimeout(7000);
    }

    // Filter by Benign Controls (18)
    const benignBtn = page.locator('button:has-text("Benign Controls (18)")');
    if (await benignBtn.isVisible()) {
      await benignBtn.click();
      await page.waitForTimeout(6000);
    }
  });

  // Chapter 5: attribution_wrap (15s)
  // Meta model attribution, honest failure boundaries & open source wrap
  if (story[5]) {
    await record(story[5], async (page) => {
      await page.goto("/");
      await page.waitForSelector("header");
      await page.waitForTimeout(2000);

      const footer = page.locator("footer");
      if (await footer.isVisible()) {
        await footer.scrollIntoViewIfNeeded();
      }
      await page.waitForTimeout(8000);
    });
  }

  await writeFile(
    assets + "capture-report.json",
    JSON.stringify(
      {
        timestamp: new Date().toISOString(),
        story: "CONTEXT 3-Minute Hackathon Demo Chapter Captures",
        report,
      },
      null,
      2
    )
  );

  console.log("\n=======================================================");
  console.log("ALL DEMO CHAPTERS CAPTURED SUCCESSFULLY!");
  console.log("=======================================================");
} finally {
  await browser.close();
}
