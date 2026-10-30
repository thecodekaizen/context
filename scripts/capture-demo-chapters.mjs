import { existsSync } from "node:fs";
import { createRequire } from "node:module";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { performance } from "node:perf_hooks";
import { spawnSync } from "node:child_process";

const require = createRequire(new URL("../web/package.json", import.meta.url));
const { chromium } = require("@playwright/test");

const root = fileURLToPath(new URL("../", import.meta.url));
const assets = root + "demo-video/assets/";
const story = JSON.parse(await readFile(root + "demo-video/story.json", "utf8"));

await mkdir(assets, { recursive: true });
await mkdir(assets + "raw", { recursive: true });

const ffmpegBin = existsSync("/opt/homebrew/bin/ffmpeg")
  ? "/opt/homebrew/bin/ffmpeg"
  : existsSync("/usr/local/bin/ffmpeg")
    ? "/usr/local/bin/ffmpeg"
    : "ffmpeg";

const browser = await chromium.launch({ headless: true });
const report = [];

const baseUrl = process.env.CONTEXT_BASE_URL || "http://127.0.0.1:8004";
const heroDossierUrl = `${baseUrl}/?dossier=technical-20261030T140841Z-1e14f9`;

async function record(chapter, action) {
  const targetMp4 = assets + chapter.id + ".mp4";
  console.log(`\n=======================================================`);
  console.log(`Recording chapter: ${chapter.id} (${chapter.duration}s)...`);
  console.log(`=======================================================`);

  const ctx = await browser.newContext({
    baseURL: baseUrl,
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
      console.log(`Holding ${chapter.id} for remaining ${remaining.toFixed(1)}s...`);
      await page.waitForTimeout(remaining * 1000);
    }
    if (errors.length) console.warn("Page errors:", errors.join("; "));

    await page.screenshot({ path: assets + chapter.id + ".png" });
    const raw = await page.video().path();
    await ctx.close();

    console.log(`Converting ${raw} -> ${targetMp4} using ${ffmpegBin}...`);
    const conversion = spawnSync(
      ffmpegBin,
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
        "18",
        "-preset",
        "fast",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        "-an",
        targetMp4,
      ],
      {
        encoding: "utf8",
        env: {
          ...process.env,
          PATH: `/opt/homebrew/bin:/usr/local/bin:${process.env.PATH || ""}`,
        },
      }
    );
    if (conversion.status !== 0 || conversion.error) {
      console.error("FFmpeg error:", conversion.error || conversion.stderr);
      throw new Error(conversion.stderr || conversion.error?.message || "FFmpeg failed");
    }

    report.push({ chapter: chapter.id, duration: chapter.duration, output: targetMp4 });
    console.log(`✓ Captured ${chapter.id}.mp4 successfully`);
  } catch (err) {
    await ctx.close();
    throw err;
  }
}

try {
  // Capture Hero image for Intro (Chapter 0)
  console.log("Capturing hero.png for Intro...");
  const introCtx = await browser.newContext({
    baseURL: baseUrl,
    viewport: { width: 1440, height: 900 },
  });
  const introPage = await introCtx.newPage();
  await introPage.goto("/?dossier=technical-20261030T140841Z-1e14f9");
  await introPage.waitForSelector("#source-comparison", { timeout: 15000 });
  await introPage.waitForTimeout(2000);

  // Position source video to reveal "WARM CACHE ONLY"
  const vids = introPage.locator("video");
  if ((await vids.count()) >= 2) {
    await vids.nth(1).evaluate((v) => {
      v.currentTime = 7.0;
    });
    await introPage.waitForTimeout(1000);
  }

  // Scroll to show both the dossier hero and the dual player
  const heroHeader = introPage.locator(".dossier-hero");
  if (await heroHeader.isVisible()) {
    await heroHeader.scrollIntoViewIfNeeded();
  }
  await introPage.waitForTimeout(1500);
  await introPage.screenshot({ path: assets + "hero.png" });
  await introCtx.close();
  console.log("✓ Captured hero.png for intro");

  // Chapter 1: problem (30s)
  // Architecture rule: deterministic aligner first, pre-publication QA workflow
  await record(story[1], async (page) => {
    await page.goto("/");
    await page.waitForSelector("header");
    await page.waitForTimeout(2000);

    // Focus on header and deterministic telemetry bar
    const telemetry = page.locator(".global-telemetry");
    await telemetry.scrollIntoViewIfNeeded();
    await page.waitForTimeout(5000);

    // Scroll into the compare section
    const introSection = page.locator(".intro");
    if (await introSection.isVisible()) {
      await introSection.scrollIntoViewIfNeeded();
    }
    await page.waitForTimeout(6000);

    // Highlight the "COMPARE TWO FOOTAGES" upload box
    const uploadBox = page.locator(".upload");
    if (await uploadBox.isVisible()) {
      await uploadBox.scrollIntoViewIfNeeded();
    }
    await page.waitForTimeout(8000);

    // Expand content admission note
    const policy = page.locator(".content-policy-note");
    if (await policy.isVisible()) {
      await policy.click();
    }
    await page.waitForTimeout(4000);
  });

  // Chapter 2: live_run (55s)
  // Live dual-player run: Python cache qualification hero clip
  // Detects 4-second omission (00:06.000 - 00:10.000) where "WARM CACHE ONLY" was cut
  await record(story[2], async (page) => {
    await page.goto("/?dossier=technical-20261030T140841Z-1e14f9");
    await page.waitForSelector("#source-comparison", { timeout: 15000 });
    await page.waitForTimeout(2000);

    // 1. Show Dossier Header & Metrics row
    const heroHeader = page.locator(".dossier-hero");
    if (await heroHeader.isVisible()) {
      await heroHeader.scrollIntoViewIfNeeded();
      await page.waitForTimeout(4000);
    }

    // Highlight the metrics: lane coverage (0% visual · 100% audio) & 1 grounded omission
    const metrics = page.locator(".dossier-metrics");
    if (await metrics.isVisible()) {
      await metrics.scrollIntoViewIfNeeded();
      await page.waitForTimeout(5000);
    }

    // 2. Scroll to Dual Forensic Player
    const playerSection = page.locator("#source-comparison");
    await playerSection.scrollIntoViewIfNeeded();
    await page.waitForTimeout(3000);

    // Play synchronized playback for 4 seconds
    const videos = page.locator("video");
    if ((await videos.count()) >= 2) {
      await videos.first().evaluate((v) => {
        v.currentTime = 2.0;
        v.play();
      });
      await page.waitForTimeout(4000);
      await videos.first().evaluate((v) => v.pause());
    }

    // 3. Scroll to model observations and expand citations
    const details = page.locator(".comparison-details summary");
    if (await details.isVisible()) {
      await details.scrollIntoViewIfNeeded();
      await details.click();
      await page.waitForTimeout(3000);
    }

    // 4. Click citation seek button: "Inspect source 6.00–10.00s"
    const seekBtn = page.locator("button.evidence-seek").first();
    if (await seekBtn.isVisible()) {
      await seekBtn.click();
      await page.waitForTimeout(2000);
    } else {
      // Direct seek fallback
      if ((await videos.count()) >= 2) {
        await videos.nth(1).evaluate((v) => {
          v.currentTime = 6.0;
        });
      }
    }

    // 5. Scroll back up to player to show revealed "WARM CACHE ONLY" terminal
    await playerSection.scrollIntoViewIfNeeded();
    await page.waitForTimeout(14000);
  });

  // Chapter 3: sam_crop (30s)
  // Spatial crop & reframe detector with OpenCV geometry & SAM 3.1 separation
  await record(story[3], async (page) => {
    await page.goto("/");
    await page.waitForSelector("header");
    await page.waitForTimeout(2000);

    // Click "Try spatial crop demo →"
    const cropBtn = page.locator('button:has-text("Try spatial crop demo →")');
    if (await cropBtn.isVisible()) {
      await cropBtn.click();
      await page.waitForSelector(".workbench", { timeout: 15000 });
      await page.waitForTimeout(2000);

      // Scroll to dual player to highlight SVG bounding box and red shaded margins
      const workbench = page.locator(".workbench");
      await workbench.scrollIntoViewIfNeeded();
      await page.waitForTimeout(8000);

      // Scroll to the Crop Analysis Card
      const cropCard = page.locator(".crop-analysis-card");
      if (await cropCard.isVisible()) {
        await cropCard.scrollIntoViewIfNeeded();
        await page.waitForTimeout(10000);
      }
    } else {
      await page.waitForTimeout(10000);
    }
  });

  // Chapter 4: evaluation (25s)
  // Frozen 30-edit benchmark results: 100% recall, 0.0s boundary error, 0/18 benign alarms (<16.7%)
  await record(story[4], async (page) => {
    await page.goto("/");
    await page.waitForSelector("header");
    await page.waitForTimeout(1500);

    // Switch to Benchmark & Evaluation Hub
    const evalTab = page.locator("#btn-nav-benchmark");
    if (await evalTab.isVisible()) {
      await evalTab.click();
    }
    await page.waitForSelector(".benchmark-hub-section", { timeout: 10000 });
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
      await page.waitForTimeout(7000);
    }
  });

  // Chapter 5: attribution_wrap (15s)
  // Meta model attribution, honest failure boundaries & open source wrap
  if (story[5]) {
    await record(story[5], async (page) => {
      await page.goto("/?dossier=technical-20261030T140841Z-1e14f9");
      await page.waitForSelector("header");
      await page.waitForTimeout(2000);

      // Click "↗ Export Forensic Dossier" in header
      const exportBtn = page.locator("button.export-trigger").first();
      if (await exportBtn.isVisible()) {
        await exportBtn.click();
        await page.waitForSelector("dialog.audit-dialog[open]", { timeout: 5000 }).catch(() => {});
        await page.waitForTimeout(7000);
      }

      const footer = page.locator("footer, .content-policy-note");
      if (await footer.isVisible()) {
        await footer.scrollIntoViewIfNeeded();
      }
      await page.waitForTimeout(4000);
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
