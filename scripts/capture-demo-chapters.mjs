import { existsSync } from "node:fs";
import { createRequire } from "node:module";
import { mkdir, readFile, writeFile, copyFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { performance } from "node:perf_hooks";
import { spawnSync } from "node:child_process";
const require = createRequire(new URL("../web/package.json", import.meta.url));
const { chromium, expect } = require("@playwright/test");
const root = fileURLToPath(new URL("../", import.meta.url));
const assets = root + "demo-video/assets/";
const story = JSON.parse(
  await readFile(root + "demo-video/story.json", "utf8"),
);
const caseId = process.argv[2] || process.env.CONTEXT_DEMO_CASE;
if (!caseId)
  throw Error("Provide a saved film case ID with a real Meta review.");
await mkdir(assets, { recursive: true });
const captureIdentity = assets + "capture-case.txt";
if (
  existsSync(captureIdentity) &&
  (await readFile(captureIdentity, "utf8")).trim() !== caseId
) {
  throw Error(
    "Existing assets belong to a different case. Use a fresh assets directory.",
  );
}
await writeFile(captureIdentity, caseId + "\n");

const browser = await chromium.launch();
const report = [];
async function record(chapter, action) {
  if (existsSync(assets + chapter.id + ".mp4")) {
    report.push({ chapter: chapter.id, actual_ui: true, reused_capture: true });
    console.log("Reusing " + chapter.id);
    return;
  }
  const ctx = await browser.newContext({
    baseURL: "http://127.0.0.1:8000",
    viewport: { width: 1440, height: 900 },
    recordVideo: { dir: assets + "raw", size: { width: 1440, height: 900 } },
    acceptDownloads: true,
  });
  const page = await ctx.newPage();
  const began = performance.now();
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  try {
    await page.goto(chapter.id === "collection" ? "/" : `/?case=${caseId}`);
    if (chapter.id !== "collection")
      await expect(
        page.getByRole("heading", {
          name: "6.00 seconds outside the published edit",
        }),
      ).toBeVisible();
    await action(page);
    const remaining =
      (chapter.duration + 1.5) * 1000 - (performance.now() - began);
    if (remaining > 0) await page.waitForTimeout(remaining);
    if (errors.length) throw Error(errors.join("; "));
    await page.screenshot({ path: assets + chapter.id + ".png" });
    const raw = await page.video().path();
    await ctx.close();
    const output = assets + chapter.id + ".mp4";
    const conversion = spawnSync(
      "ffmpeg",
      [
        "-v",
        "error",
        "-y",
        "-ss",
        "0.6",
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
        output,
      ],
      { encoding: "utf8" },
    );
    if (conversion.status !== 0) throw Error(conversion.stderr);
    report.push({
      chapter: chapter.id,
      actual_ui: true,
      source_case: caseId,
      output,
    });
    console.log("Captured " + chapter.id);
  } catch (err) {
    await ctx.close();
    throw err;
  }
}
try {
  await record(story[1], async (page) => {
    await page.locator(".collection").scrollIntoViewIfNeeded();
    await page.waitForTimeout(2000);
    await page
      .getByLabel("Add an original recording")
      .setInputFiles(root + "data/evaluation/source.mp4");
    await page.getByRole("button", { name: "Add to collection" }).click();
    await expect(
      page.getByText("Indexed source.mp4. Ready to search."),
    ).toBeVisible();
    await page.waitForTimeout(4000);
    await page
      .getByLabel("Find the source of an edit")
      .setInputFiles(root + "data/evaluation/omission.mp4");
    await page.getByRole("button", { name: "Search collection" }).click();
    await expect(
      page.getByText("Source selected from your collection"),
    ).toBeVisible();
    await page.waitForTimeout(4000);
    await page.locator(".workbench").scrollIntoViewIfNeeded();
  });
  await record(story[2], async (page) => {
    await page.locator(".workbench").scrollIntoViewIfNeeded();
    await page.waitForTimeout(3000);
    await page
      .locator("video")
      .first()
      .evaluate((v) => v.play());
    await page.waitForTimeout(12500);
    await page
      .locator("video")
      .first()
      .evaluate((v) => v.pause());
  });
  await record(story[3], async (page) => {
    await page.locator(".workbench").scrollIntoViewIfNeeded();
    await page.waitForTimeout(4000);
    await page.getByRole("button", { name: /Reveal omitted/ }).click();
    await expect(page.getByText("REVEALING OMITTED CONTEXT")).toBeVisible();
    await page.waitForTimeout(7000);
  });
  await record(story[4], async (page) => {
    await page.getByRole("button", { name: "Review with Meta AI" }).click();
    await expect(
      page.getByText("SAVED REVIEW", { exact: false }),
    ).toBeVisible();
    await page.locator(".semantic").scrollIntoViewIfNeeded();
    await page.waitForTimeout(9000);
    await page
      .getByRole("heading", { name: "Possible effect on interpretation" })
      .scrollIntoViewIfNeeded();
  });
  await record(story[5], async (page) => {
    await page.locator(".semantic").scrollIntoViewIfNeeded();
    await page.waitForTimeout(3000);
    await page
      .getByRole("button", { name: /^Original \d/ })
      .first()
      .click();
    await page.locator(".workbench").scrollIntoViewIfNeeded();
    await page.waitForTimeout(6500);
    await page.locator(".semantic").scrollIntoViewIfNeeded();
  });
  await record(story[6], async (page) => {
    const download = page.waitForEvent("download");
    await page.getByText("Download evidence JSON").click();
    const file = await download;
    await file.saveAs(assets + "actual-evidence.json");
    await page.waitForTimeout(2500);
    await page.reload();
    await expect(
      page.getByText("SAVED REVIEW", { exact: false }),
    ).toBeVisible();
    await page.getByText("Method, provenance & limitations").click();
    await page
      .getByText("Source SHA-256:", { exact: false })
      .scrollIntoViewIfNeeded();
    await page.waitForTimeout(5500);
    await page.locator(".workbench").scrollIntoViewIfNeeded();
  });
  const ctx = await browser.newContext({
    baseURL: "http://127.0.0.1:8000",
    viewport: { width: 1440, height: 900 },
  });
  const page = await ctx.newPage();
  await page.goto("/?case=" + caseId);
  await expect(
    page.getByRole("heading", {
      name: "6.00 seconds outside the published edit",
    }),
  ).toBeVisible();
  await page.getByRole("button", { name: /Linked playback/ }).click();
  await page
    .locator("video")
    .first()
    .evaluate((v) => {
      v.currentTime = 8;
    });
  await page
    .locator("video")
    .nth(1)
    .evaluate((v) => {
      v.currentTime = 10;
    });
  await page.waitForFunction(() =>
    Array.from(document.querySelectorAll("video")).every(
      (v) => v.readyState >= 2,
    ),
  );
  await page.waitForTimeout(800);
  await page.locator(".workbench").screenshot({ path: assets + "hero.png" });
  await ctx.close();
  await writeFile(
    assets + "capture-report.json",
    JSON.stringify(
      {
        caseId,
        report,
        model_review: "saved real response; no fresh inference",
      },
      null,
      2,
    ),
  );
  await copyFile(root + "docs/evaluation.json", assets + "evaluation.json");
} finally {
  await browser.close();
}
