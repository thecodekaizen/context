import { test, expect } from "@playwright/test";
test("generated evidence, omission reveal and download", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: /Every cut leaves/ }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Try generated case" }).click();
  await expect(
    page.getByText("Visual source correspondence found"),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", {
      name: "4.00 seconds outside the published edit",
    }),
  ).toBeVisible();
  await expect(page.locator("video")).toHaveCount(2);
  await page.getByRole("button", { name: "Reveal missing context" }).click();
  await expect(page.getByText("REVEALING OMITTED CONTEXT")).toBeVisible();
  const source = page.locator("video").nth(1);
  await expect
    .poll(() => source.evaluate((v: HTMLVideoElement) => v.currentTime))
    .toBeGreaterThanOrEqual(4);
  await expect
    .poll(() => source.evaluate((v: HTMLVideoElement) => v.readyState))
    .toBeGreaterThanOrEqual(2);
  const href = await page
    .getByText("Download evidence JSON")
    .getAttribute("href");
  const evidence = await (await page.request.get(href!)).json();
  expect(evidence.findings[0]).toMatchObject({
    kind: "omission",
    source_start: 4,
    source_end: 8,
  });
  await page.screenshot({ path: "../docs/workstation.png", fullPage: true });
  expect(errors).toEqual([]);
});
test("mobile workspace fits viewport", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth),
  ).toBeLessThanOrEqual(390);
});
test("simulated missing Meta credential preserves evidence", async ({
  page,
}) => {
  await page.route("**/api/investigations/*/interpret/*", (route) =>
    route.fulfill({
      status: 503,
      json: {
        detail:
          "Meta analysis unavailable: configure MODEL_API_KEY in the server environment.",
      },
    }),
  );
  await page.goto("/");
  await page.getByRole("button", { name: "Try generated case" }).click();
  await expect(
    page.getByText("Visual source correspondence found"),
  ).toBeVisible();
  await page.getByRole("button", { name: "Review with Meta AI" }).click();
  await expect(page.getByRole("alert")).toContainText("MODEL_API_KEY");
  await expect(
    page.getByRole("heading", {
      name: "4.00 seconds outside the published edit",
    }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Reveal missing context" }).click();
  await expect(page.getByText("REVEALING OMITTED CONTEXT")).toBeVisible();
});
test("model review presentation and citation seeking using a labeled test response", async ({
  page,
}) => {
  await page.route("**/api/investigations/*/interpret/*", (route) =>
    route.fulfill({
      json: {
        model: "TEST RESPONSE",
        finding_id: "f0",
        interpretation: {
          observations: [
            {
              text: "Synthetic test observation",
              citations: [
                {
                  media: "source",
                  media_start: 5,
                  media_end: 6,
                  clip_id: "source_context",
                },
              ],
            },
          ],
          possible_effect: "Synthetic test interpretation",
          uncertainty: "This is a mocked UI test, not actual model inference.",
        },
      },
    }),
  );
  await page.goto("/");
  await page.getByRole("button", { name: "Try generated case" }).click();
  await expect(
    page.getByText("Visual source correspondence found"),
  ).toBeVisible();
  await page.getByRole("button", { name: "Review with Meta AI" }).click();
  await expect(page.getByText("Synthetic test observation")).toBeVisible();
  await page.getByRole("button", { name: /Original 00:05.00/ }).click();
  await expect
    .poll(() =>
      page
        .locator("video")
        .nth(1)
        .evaluate((v: HTMLVideoElement) => v.currentTime),
    )
    .toBe(5);
  await expect(
    page.getByText(
      "Citation bounds checked. Model claims are not independently verified.",
    ),
  ).toBeVisible();
});
test("index an original and discover it from an edited upload", async ({
  page,
}) => {
  await page.request.post("/api/demo");
  await page.goto("/");
  await page
    .getByLabel("Add an original recording")
    .setInputFiles("../data/demo/original.mp4");
  await page.getByRole("button", { name: "Add to collection" }).click();
  await expect(
    page.getByText("Indexed original.mp4. Ready to search."),
  ).toBeVisible();
  await page
    .getByLabel("Find the source of an edit")
    .setInputFiles("../data/demo/edited.mp4");
  await page.getByRole("button", { name: "Search collection" }).click();
  await expect(
    page.getByText("Source selected from your collection"),
  ).toBeVisible();
  await expect(
    page.getByText("Visual source correspondence found"),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", {
      name: "4.00 seconds outside the published edit",
    }),
  ).toBeVisible();
});
test("ambiguous collection result does not display a selected source", async ({
  page,
}) => {
  await page.route("**/api/library", (route) =>
    route.fulfill({
      json: {
        sources: [{ id: "test", name: "Similar originals", duration: 12 }],
      },
    }),
  );
  await page.route("**/api/library/search", (route) =>
    route.fulfill({
      json: {
        search: {
          status: "ambiguous",
          candidates: [
            { id: "a", name: "Original A", coverage: 1, score: 1 },
            { id: "b", name: "Original B", coverage: 1, score: 1 },
          ],
        },
        evidence: null,
      },
    }),
  );
  await page.goto("/");
  await page.getByLabel("Find the source of an edit").setInputFiles({
    name: "edit.mp4",
    mimeType: "video/mp4",
    buffer: Buffer.from("UI test fixture"),
  });
  await page.getByRole("button", { name: "Search collection" }).click();
  await expect(
    page.getByText("More than one source fits this edit"),
  ).toBeVisible();
  await expect(page.locator("video")).toHaveCount(0);
});

test("investigation survives reload and saved-case navigation", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Try generated case" }).click();
  await expect(
    page.getByText("Visual source correspondence found"),
  ).toBeVisible();
  await expect(page).toHaveURL(/case=demo/);
  await page.reload();
  await expect(
    page.getByRole("heading", {
      name: "4.00 seconds outside the published edit",
    }),
  ).toBeVisible();
  await page
    .getByText("Saved investigations", { exact: false })
    .first()
    .click();
  await expect(
    page.getByRole("button", { name: /Generated case/ }),
  ).toBeVisible();
});

test("licensed production example shows measured omission and attribution", async ({
  page,
}) => {
  const health = await (await page.request.get("/api/health")).json();
  test.skip(
    !health.film_demo_available,
    "Optional licensed film sample is not installed",
  );
  await page.goto("/");
  await page
    .getByRole("button", { name: "Explore licensed film case" })
    .click();
  await expect(
    page.getByRole("heading", {
      name: "6.00 seconds outside the published edit",
    }),
  ).toBeVisible();
  await expect(
    page.getByText("Selected local source:", { exact: false }),
  ).toContainText("Big Buck Bunny");
  await page.getByText("Method, provenance & limitations").click();
  await expect(
    page.getByText("CC BY 3.0", { exact: false }).first(),
  ).toBeVisible();
});
