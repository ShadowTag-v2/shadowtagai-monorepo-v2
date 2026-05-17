// Playwright E2E test configuration for CounselConduit staging
// See: docs/runbooks/canary-deployment.md

import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  timeout: 30_000,
  retries: 2,
  workers: 2,

  use: {
    baseURL: "https://counselconduit-staging-767252945109.us-central1.run.app",
    extraHTTPHeaders: {
      Accept: "application/json",
    },
    trace: "on-first-retry",
  },

  projects: [
    {
      name: "api-smoke",
      testMatch: /.*smoke\.spec\.ts/,
    },
    {
      name: "api-admin",
      testMatch: /.*admin\.spec\.ts/,
    },
    {
      name: "api-providers",
      testMatch: /.*providers\.spec\.ts/,
    },
  ],
});
