// @ts-check
/** @type {import('@playwright/test').PlaywrightTestConfig} */
const config = {
  testDir: '.',
  testMatch: ['**/e2e_smoke.spec.js', '**/e2e*.spec.js'],
  timeout: 30000,
  retries: 1,
  use: {
    baseURL: process.env.KOVELAI_URL || 'https://kovelai.web.app',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { browserName: 'chromium' },
    },
  ],
};
module.exports = config;
