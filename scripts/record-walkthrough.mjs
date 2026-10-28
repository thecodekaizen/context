// Browser QA recording: actual local app, real provider request, no mocked findings.
import { createRequire } from "node:module";
import { mkdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";
const require = createRequire(new URL("../web/package.json", import.meta.url));
const { chromium, expect } = require("@playwright/test");
const output = fileURLToPath(new URL("../data/walkthrough/", import.meta.url));
await mkdir(output, { recursive: true });
const browser = await chromium.launch();
const context = await browser.newContext({
  baseURL: "http://127.0.0.1:8000",
  viewport: { width: 1440, height: 1000 },
  recordVideo: { dir: output, size: { width: 1440, height: 1000 } },
});
const page = await context.newPage();
page.setDefaultTimeout(150000);
const errors = [];
page.on("pageerror", (err) => errors.push(err.message));
try {
  const caseId = process.argv[2];
  await page.goto(caseId ? `/?case=${encodeURIComponent(caseId)}` : "/");
  if (!caseId)
    await page
      .getByRole("button", { name: "Explore licensed film case" })
      .click();
  await expect(
    page.getByRole("heading", {
      name: "6.00 seconds outside the published edit",
    }),
  ).toBeVisible();
  await page.locator(".workbench").scrollIntoViewIfNeeded();
  await page.getByRole("button", { name: "Reveal missing context" }).click();
  await expect(page.getByText("REVEALING OMITTED CONTEXT")).toBeVisible();
  await page.waitForTimeout(6500); // Record the full real omission interval.
  await page.getByRole("button", { name: "Review with Meta AI" }).click();
  await expect(
    page.getByRole("heading", { name: "Model observation 1", exact: true }),
  ).toBeVisible({ timeout: 150000 });
  await page.locator(".semantic").scrollIntoViewIfNeeded();
  await page.screenshot({
    path: fileURLToPath(new URL("../docs/film-review.png", import.meta.url)),
    fullPage: true,
  });
  const url = page.url();
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "Model observation 1", exact: true }),
  ).toBeVisible();
  await page.locator(".semantic").scrollIntoViewIfNeeded();
  const response = await page.request.get(
    "/api/investigations/" + new URL(url).searchParams.get("case"),
  );
  const saved = await response.json();
  if (saved.reviews.length !== 1)
    throw Error("Live interpretation did not survive reload");
  const citation = page
    .getByRole("button", { name: /^(Original|Published) \d/ })
    .first();
  await citation.click();
  await page.locator(".workbench").scrollIntoViewIfNeeded();
  await page.screenshot({
    path: fileURLToPath(
      new URL("../docs/film-workstation.png", import.meta.url),
    ),
    fullPage: true,
  });
  await page.waitForTimeout(1200);
  if (errors.length) throw Error(errors.join("; "));
  console.log(
    JSON.stringify({
      case_url: url,
      model: saved.reviews[0].model,
      observations: saved.reviews[0].interpretation.observations.length,
      review_restored: true,
      recording: await page.video().path(),
    }),
  );
} finally {
  await context.close();
  await browser.close();
}
