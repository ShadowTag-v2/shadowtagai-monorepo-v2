// @ts-check
/** @type {import('@playwright/test').PlaywrightTestConfig} */
const config = {
  testDir: '.',
  testMatch: ['**/e2e_smoke.spec.js', '**/e2e*.spec.js'],
  timeout: 45000,
  retries: 2,
  use: {
    baseURL: process.env.STAGING_URL || 'https://counselconduit-staging-767252945109.us-central1.run.app',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    extraHTTPHeaders: {
      'X-Environment': 'staging',
    },
  },
  projects: [
    {
      name: 'chromium-staging',
      use: { browserName: 'chromium' },
    },
  ],
  reporter: [
    ['html', { open: 'never', outputFolder: 'test-results/staging-report' }],
    ['json', { outputFile: 'test-results/staging-results.json' }],
  ],
};
module.exports = config;
