import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "tests",
  use: {
    baseURL: process.env.CONTEXT_BASE_URL || "http://127.0.0.1:8000",
    browserName: "chromium",
  },
  timeout: 60000,
});
