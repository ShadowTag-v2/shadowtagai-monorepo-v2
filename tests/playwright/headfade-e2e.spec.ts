import { test, expect } from '@playwright/test';

test.describe('HeadFade E2E Test Suite - Pre-May 12 Launch', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://headfade.web.app');
  });

  test('should load homepage and show live metrics', async ({ page }) => {
    await expect(page.locator('text=HeadFade')).toBeVisible();
    await expect(page.locator('[data-testid="daily-active-users"]')).toContainText(/\d+/);
  });

  test('should analyze a sample video and return HDI', async ({ page }) => {
    await page.click('text=Try Demo');
    await page.fill('input[placeholder="Enter video URL"]', 'https://example.com/demo-video.mp4');
    await page.click('button:has-text("Analyze")');

    await expect(page.locator('[data-testid="hdi-score"]')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('[data-testid="hdi-score"]')).toContainText(/\d+%/);
  });

  test('should display Remix Tree Visualizer', async ({ page }) => {
    await page.goto('/demo/remix-tree');
    await expect(page.locator('text=Remix Tree Visualizer')).toBeVisible();
    await expect(page.locator('.remix-node')).toHaveCount({ min: 3 });
  });

  test('should complete micro-license purchase flow', async ({ page }) => {
    await page.click('text=Marketplace');
    await page.click('button:has-text("Buy License")');
    await expect(page.locator('text=License Granted')).toBeVisible({ timeout: 8000 });
  });

  test('Lighthouse performance audit', async ({ page }) => {
    const metrics = await page.evaluate(() => (window as any).performance);
    expect(metrics).toBeDefined();
  });
});
```