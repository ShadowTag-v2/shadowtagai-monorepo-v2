const { test, expect } = require('@playwright/test');

test.describe('KovelAI Homepage Verification (E2E Stub)', () => {
  test('should load without 500 errors', async ({ page }) => {
    // Stub definition as the API provides the backend root for now
    await page.goto('http://localhost:8000/api/v1/health');

    // Validate health check output
    const content = await page.content();
    expect(content).toContain('operational');
    expect(content).toContain('KovelAI S.E.U. Proxy');
  });

  // Future UI tests will go here
});
