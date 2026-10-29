import { test, expect } from "@playwright/test";

test("single-video investigation dossier presentation, facts and citations", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));

  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: /Investigate footage from ONE input/ }),
  ).toBeVisible();

  // Load benchmark case
  await page.getByRole("button", { name: "Open Saved Investigation" }).click();
  await expect(page.locator(".dossier-hero")).toBeVisible({ timeout: 15000 });
  await expect(page.locator(".dossier-title")).toContainText(
    "Artemis I carried astronauts to the Moon",
  );
  await expect(
    page.locator(".metric-card.contradicted .metric-val"),
  ).toHaveText("1");
  await expect(
    page.getByText("Mission Type Uncrewed lunar flight test"),
  ).toBeVisible();

  // Tab switching: Visual Player
  await page.click('button:has-text("02 Visual Player")');
  await expect(page.locator(".cinema-video")).toBeVisible();
  await expect(page.locator(".frame-thumb-box")).toHaveCount(8);

  // Tab switching: Claims & Fact-Check
  await page.click('button:has-text("03 Claims & Fact-Check")');
  await expect(
    page.getByText("Extracted Factual Claims & Evaluation"),
  ).toBeVisible();
  await expect(page.locator(".verdict-badge.contradicted").first()).toHaveText(
    "CONTRADICTED",
  );

  // Tab switching: Discovered Sources
  await page.click('button:has-text("04 Discovered Sources")');
  await expect(
    page.getByText("Automatically Discovered Sources"),
  ).toBeVisible();
  await expect(page.locator(".source-card")).toHaveCount(8);

  expect(errors).toEqual([]);
});

test("two-video comparator drill-down works in supporting mode", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));

  await page.goto("/");
  await page.click('button:has-text("Two-Video Comparison Drill-Down")');
  await expect(
    page.getByRole("heading", { name: /alignment & omissions/ }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Try generated case" }).click();
  await expect(page.locator(".workbench")).toBeVisible();
  await expect(page.locator("video")).toHaveCount(2);
  await page.locator(".audio-evidence summary").click();
  await expect(page.getByText("Both files need an audio stream")).toBeVisible();

  expect(errors).toEqual([]);
});

test("mobile workspace fits viewport", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth),
  ).toBeLessThanOrEqual(390);
});

test("overview observation opens the player at its evidence timestamp", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Open Saved Investigation" }).click();
  const item = page
    .locator(".quick-obs-item")
    .filter({ hasText: "00:13" })
    .first();
  await item.click();
  const video = page.locator(".cinema-video");
  await expect(video).toBeVisible();
  await expect
    .poll(() => video.evaluate((v: HTMLVideoElement) => v.currentTime))
    .toBeGreaterThanOrEqual(13);
  await video.evaluate((v: HTMLVideoElement) => v.pause());
  expect(
    await video.evaluate((v: HTMLVideoElement) => v.currentTime),
  ).toBeLessThan(17);
});
