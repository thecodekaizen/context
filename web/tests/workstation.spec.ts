import { test, expect } from "@playwright/test";

// Real deterministic demo endpoints; these tests do not invoke Meta models.
test("transport, curtain, cut navigation and export preserve evidence", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/");
  await expect(
    page.getByRole("button", { name: /Export Forensic Dossier/ }),
  ).toBeDisabled();
  await page.getByRole("button", { name: "Try benchmark omission →" }).click();
  const stage = page.locator(".forensic-stage");
  await expect(stage.locator("video")).toHaveCount(2);
  await expect
    .poll(() =>
      stage
        .locator("video")
        .first()
        .evaluate((v: HTMLVideoElement) => v.readyState),
    )
    .toBeGreaterThanOrEqual(1);
  await page
    .getByRole("slider", { name: "Edited video playhead" })
    .fill("3.45");
  await expect
    .poll(() =>
      stage
        .locator("video")
        .first()
        .evaluate((v: HTMLVideoElement) => v.currentTime),
    )
    .toBeCloseTo(3.45, 1);
  await expect(page.locator(".transport-time")).toContainText("00:03.450");
  await page.locator(".workbench .section-top").first().click();
  await page.keyboard.press("m");
  await expect(stage).toHaveClass(/curtain-mode/);
  await page.getByRole("slider", { name: "Curtain split position" }).fill("32");
  await expect(stage).toHaveAttribute("style", /32%/);
  await page.locator(".workbench .section-top").first().click();
  await page.keyboard.press("m");
  await expect(stage).not.toHaveClass(/curtain-mode/);
  await page.keyboard.press("Space");
  await expect
    .poll(() =>
      stage
        .locator("video")
        .first()
        .evaluate((v: HTMLVideoElement) => v.paused),
    )
    .toBe(false);
  await page.keyboard.press("k");
  await expect
    .poll(() =>
      stage
        .locator("video")
        .first()
        .evaluate((v: HTMLVideoElement) => v.paused),
    )
    .toBe(true);
  await page.keyboard.press("j");
  await expect
    .poll(() =>
      stage
        .locator("video")
        .first()
        .evaluate((v: HTMLVideoElement) => v.currentTime),
    )
    .toBeLessThan(3.45);
  await page.keyboard.press("k");
  await page
    .getByRole("button", { name: "Next omission", exact: true })
    .click();
  await expect
    .poll(() =>
      stage
        .locator("video")
        .nth(1)
        .evaluate((v: HTMLVideoElement) => v.currentTime),
    )
    .toBeGreaterThanOrEqual(5);
  await page.locator(".workbench .section-top").first().click();
  await page.keyboard.press("k");
  await expect(page.locator(".forensic-player [role=alert]")).toHaveCount(0);
  await page.getByRole("button", { name: /Export Forensic Dossier/ }).click();
  const dialog = page.getByRole("dialog");
  await expect(dialog).toBeVisible();
  await expect(dialog.locator(".fingerprints dd").first()).toHaveText(
    /^[a-f0-9]{64}$/,
  );
  await expect(dialog).toContainText("not a digital signature");
  await expect(dialog.locator("tbody tr")).toHaveCount(1);
  await page.screenshot({ path: "test-results/export-preview.png" });
  await page.emulateMedia({ media: "print" });
  await page.pdf({
    path: "test-results/forensic-dossier.pdf",
    format: "A4",
    printBackground: true,
  });
  await page.emulateMedia({ media: "screen" });
  await page.keyboard.press("Escape");
  await expect(dialog).not.toBeVisible();
  await page.screenshot({
    path: "test-results/workstation-desktop.png",
    fullPage: true,
  });
  for (const width of [390, 768, 1440]) {
    await page.setViewportSize({ width, height: 1000 });
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth),
    ).toBeLessThanOrEqual(width);
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({
    path: "test-results/workstation-mobile.png",
    fullPage: true,
  });
  expect(errors).toEqual([]);
});

test("spatial inspector exposes measured calipers and mask control", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Try spatial crop demo →" }).click();
  await expect(page.locator(".spatial-hud")).toBeVisible();
  await expect(page.locator(".spatial-overlay")).toHaveCount(1);
  await page
    .getByRole("slider", { name: "Peripheral mask opacity" })
    .fill("80");
  await expect(page.locator(".spatial-hud output")).toHaveText("80%");
  await expect(page.locator(".spatial-overlay > g").first()).toHaveAttribute(
    "opacity",
    "0.8",
  );
  await page
    .getByRole("checkbox", { name: "Crop overlay", exact: true })
    .uncheck();
  await expect(page.locator(".spatial-overlay")).toHaveCount(0);
  await page
    .getByRole("checkbox", { name: "Crop overlay", exact: true })
    .check();
  await expect
    .poll(() =>
      page
        .locator(".forensic-stage video")
        .first()
        .evaluate((v: HTMLVideoElement) => v.readyState),
    )
    .toBeGreaterThanOrEqual(2);
  await page.screenshot({
    path: "test-results/spatial-desktop.png",
    fullPage: true,
  });
});

test("evaluation derives counts and never invents passing metrics on errors", async ({
  page,
}) => {
  await page.goto("/");
  await page.locator("#btn-nav-benchmark").click();
  await expect(page.locator(".validation-status")).toContainText("GATE PASSED");
  await expect(page.locator(".benchmark-table-wrapper tbody tr")).toHaveCount(
    30,
  );
  await page.getByRole("button", { name: "Speed controls 3" }).click();
  await expect(page.locator(".benchmark-table-wrapper tbody tr")).toHaveCount(
    3,
  );
  await page.getByRole("button", { name: "Benign controls 18" }).click();
  await expect(page.locator(".benchmark-table-wrapper tbody tr")).toHaveCount(
    18,
  );
  await page.getByRole("button", { name: "All cases 30" }).click();
  await page.screenshot({
    path: "test-results/evaluation-desktop.png",
    fullPage: true,
  });
  await page.getByRole("button", { name: "Replay evidence ↗" }).first().click();
  await expect(page.locator(".forensic-stage video")).toHaveCount(2);
  await page.route("**/api/benchmark/results", (route) =>
    route.fulfill({ status: 503, json: { detail: "Unavailable" } }),
  );
  await page.locator("#btn-nav-benchmark").click();
  await expect(page.getByRole("alert")).toContainText("Evaluation unavailable");
  await expect(
    page.locator(".benchmark-metric-card strong").first(),
  ).toHaveText("—");
  await expect(page.locator(".validation-status")).toHaveText(
    "RESULTS UNAVAILABLE",
  );
});

// Contract fixture: validates review presentation/citation seeking, not model accuracy.
test("bounded review badge and citations retain exact source time", async ({
  page,
  request,
}) => {
  const response = await request.post("/api/demo/benchmark");
  expect(response.ok()).toBeTruthy();
  const evidence = await response.json();
  const measured = evidence.omission_evidence.omissions[0];
  evidence.findings = [
    {
      id: "review-contract",
      kind: "omission",
      source_start: measured.source_start,
      source_end: measured.source_end,
    },
  ];
  await page.route("**/api/demo/benchmark", (route) =>
    route.fulfill({ json: evidence }),
  );
  await page.route(
    "**/api/investigations/*/interpret/review-contract",
    (route) =>
      route.fulfill({
        json: {
          model: "muse-spark-1.2",
          finding_id: "review-contract",
          interpretation: {
            classification: "inconclusive",
            possible_effect:
              "Presentation fixture only; semantic effect is not established.",
            uncertainty: "Contract test, not a model result.",
            observations: [
              {
                text: "Fixture cited observation",
                citations: [
                  {
                    media: "source",
                    media_start: 5.125,
                    media_end: 6,
                    clip_id: "source-clip",
                  },
                ],
              },
            ],
          },
        },
      }),
  );
  await page.goto("/");
  await page.getByRole("button", { name: "Try benchmark omission →" }).click();
  await page.getByRole("button", { name: "Semantic Review ↗" }).click();
  await expect(page.locator(".grounding-badge")).toContainText(
    "GROUNDED INTERVAL · 00:05.000 — 00:10.000",
  );
  await expect(page.locator(".grounding-badge")).toContainText(
    "does not certify semantic accuracy",
  );
  await page.getByRole("button", { name: "Seek source @ 00:05.125" }).click();
  await expect
    .poll(() =>
      page
        .locator(".forensic-stage video")
        .nth(1)
        .evaluate((v: HTMLVideoElement) => v.currentTime),
    )
    .toBeCloseTo(5.125, 2);
  await expect(page.locator(".forensic-stage video").nth(1)).toHaveJSProperty(
    "paused",
    true,
  );
});

test("forensic text tokens meet AA contrast on every surface", async ({
  page,
}) => {
  await page.goto("/");
  const ratios = await page.evaluate(() => {
    const style = getComputedStyle(document.documentElement);
    const luminance = (hex: string) => {
      const rgb = hex
        .trim()
        .replace("#", "")
        .match(/.{2}/g)!
        .map((x) => parseInt(x, 16) / 255)
        .map((x) => (x <= 0.04045 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4));
      return rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722;
    };
    return ["--text", "--muted", "--subtle", "--evidence", "--warning"].flatMap(
      (fg) =>
        ["--obsidian", "--surface", "--surface-raised", "--sheet"].map((bg) => {
          const a = luminance(style.getPropertyValue(fg)),
            b = luminance(style.getPropertyValue(bg));
          return {
            pair: `${fg}/${bg}`,
            ratio: (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05),
          };
        }),
    );
  });
  for (const result of ratios)
    expect(result.ratio, result.pair).toBeGreaterThanOrEqual(4.5);
});

test("unreviewed uploads show a useful admission error without starting analysis", async ({
  page,
}) => {
  await page.goto("/");
  await page
    .getByLabel("Original source", { exact: true })
    .setInputFiles({
      name: "trusted-benchmark.mp4",
      mimeType: "video/mp4",
      buffer: Buffer.from("unreviewed source fixture"),
    });
  await page
    .getByLabel("Published edit", { exact: true })
    .setInputFiles({
      name: "technical-tutorial.mp4",
      mimeType: "video/mp4",
      buffer: Buffer.from("unreviewed edit fixture"),
    });
  const response = page.waitForResponse(
    (r) => r.url().endsWith("/api/analyze") && r.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Trace the edit ↗" }).click();
  expect((await response).status()).toBe(422);
  await expect(page.getByRole("alert")).toContainText(
    "Content admission blocked",
  );
  await expect(page.getByRole("alert")).toContainText(
    "Review the exact files locally",
  );
  await expect(page.locator(".forensic-stage")).toHaveCount(0);
});
