import { test, expect } from "@playwright/test";

test("real saved reversal is prominent and copied brief contains source evidence", async ({
  page,
  context,
}) => {
  await context.grantPermissions(["clipboard-read", "clipboard-write"]);
  await page.goto("/?dossier=83767ad0f4c44a6e93cac7b7eea7dc48");
  const hero = page.getByTestId("consequential-finding");
  await expect(hero).toContainText("no humans");
  expect(
    await hero.evaluate((element) => element.getBoundingClientRect().top),
  ).toBeLessThan(600);
  await hero.getByRole("link").click();
  await expect(page.locator("#source-comparison")).toBeInViewport();
  await page.getByRole("button", { name: "Copy Markdown Brief" }).click();
  const brief = await page.evaluate(() => navigator.clipboard.readText());
  expect(brief).toContain("meaning_changed");
  expect(brief).toContain("no humans");
  expect(brief).toContain("13.25");
  const markers = await page.request.get(
    "/api/dossiers/83767ad0f4c44a6e93cac7b7eea7dc48/markers.csv",
  );
  expect(await markers.text()).toContain("meaning_changed");
});
