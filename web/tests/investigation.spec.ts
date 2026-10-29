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

test("matched corpus source reveals missing context in synchronized dual player", async ({
  page,
}) => {
  await page.goto("/?dossier=artemis-captioned-omission");
  await expect(page.locator(".dossier-hero")).toBeVisible({ timeout: 15000 });
  await expect(page.locator(".matched-source-banner")).toBeVisible();
  await expect(page.locator(".matched-source-banner h4")).toContainText(
    "NASA Artemis I Mission Journey",
  );
  await expect(page.locator(".source-coverage-pill")).toContainText("86% Match");

  // Click button to reveal missing context in dual player
  await page.locator(".btn-open-dual-comparator").click();
  await expect(page.locator(".workbench")).toBeVisible();
  await expect(page.locator("video")).toHaveCount(2);
  await expect(page.getByText("86% VISUAL COVERAGE")).toBeVisible();
});

test("prelude anticipatory roadway hazard lens displays telemetry, tracks, and lead time", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));

  // Mock prelude investigate API call for fast, deterministic browser test
  await page.route("**/api/prelude/investigate*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        video_id: "prelude_mock_001",
        video_path: "mock.mp4",
        media_url: "/api/prelude/samples/near_crash_011/media",
        duration: 7.8,
        t_cutoff: 7.1,
        t_incident: 7.8,
        lead_time: 1.2,
        hazard_detected: true,
        risk_level: "critical",
        finding: {
          hazard_detected: true,
          risk_level: "critical",
          t_cue_seconds: 6.6,
          t_incident_seconds: 7.8,
          lead_time_seconds: 1.2,
          conflict_type: "lateral_encroachment",
          summary: "Pre-incident hazard detected at t=6.6s (1.2s lead time before incident at t=7.8s).",
          hazard_actor: "silver hatchback crossing ego lane",
          kinematic_signals: {
            peak_lateral_flow: 19.6,
            peak_looming_rate: 86.2,
            active_tracks_count: 22,
          },
          observations: ["At t=6.6s, silver hatchback enters ego travel lane."],
          uncertainty: "Offline monocular replay only.",
          disclaimer: "Offline research/replay only. Not for real-time driving safety.",
        },
        actors: [
          {
            track_id: "actor_1",
            label: "vehicle",
            trajectory: [
              { time: 6.6, box: [0.3, 0.4, 0.6, 0.7], velocity: [-0.15, 0.05], area: 0.09 },
            ],
            is_hazard: true,
            looming_rate: 86.2,
            lateral_crossing_velocity: 0.15,
          },
        ],
        timeline_events: [
          { time: 0.0, kind: "intake", label: "Dashcam Ingestion", detail: "Duration 7.8s" },
          { time: 6.6, kind: "early_warning", label: "Hazard Flagged", detail: "Early warning" },
        ],
        disclaimer: "Offline research/replay only. Not for real-time driving safety.",
      }),
    });
  });

  await page.goto("/");

  // Switch to PRELUDE lens
  await page.click('button:has-text("Anticipate Roadway Hazards")');
  await expect(page.locator(".prelude-studio")).toBeVisible();
  await expect(page.locator(".prelude-title")).toHaveText(
    "Anticipatory Roadway Hazard Intelligence",
  );
  await expect(page.locator(".sample-chip")).toHaveCount(4);

  // Verify telemetry & risk display
  await expect(page.locator(".hero-risk-panel")).toBeVisible({ timeout: 5000 });
  await expect(page.locator(".telemetry-box")).toHaveCount(3);
  await expect(page.locator(".prelude-timeline-track")).toBeVisible();
  await expect(page.locator(".timeline-window.pre-incident")).toBeVisible();
  await expect(page.locator(".timeline-window.withheld")).toBeVisible();
  await expect(page.locator(".lead-time-tag")).toContainText("+1.20s Lead Time");

  // Verify disclaimer
  await expect(page.locator(".prelude-disclaimer-pill")).toContainText(
    "Offline Replay Only",
  );

  // Switch back to CONTEXT
  await page.locator(".prelude-back-btn").click();
  await expect(
    page.getByRole("heading", { name: /Investigate footage from ONE input/ }),
  ).toBeVisible();

  expect(errors).toEqual([]);
});
