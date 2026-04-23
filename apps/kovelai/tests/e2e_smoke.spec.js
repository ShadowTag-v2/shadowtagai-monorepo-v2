// KovelAI E2E Smoke Tests — Playwright
// Run: npx playwright test apps/kovelai/tests/e2e_smoke.spec.js

const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.KOVELAI_URL || 'https://kovelai.web.app';

test.describe('KovelAI Landing Page', () => {
  test('loads and has correct title', async ({ page }) => {
    await page.goto(BASE_URL);
    await expect(page).toHaveTitle(/KovelAI/i);
  });

  test('health check returns 200', async ({ request }) => {
    const resp = await request.get(`${BASE_URL}/`);
    expect(resp.status()).toBe(200);
  });

  test('has primary CTA visible', async ({ page }) => {
    await page.goto(BASE_URL);
    const cta = page.locator(
      'a:has-text("Get Started"), button:has-text("Get Started"), a:has-text("Book"), button:has-text("Book")',
    );
    await expect(cta.first()).toBeVisible();
  });

  test('navigation links work', async ({ page }) => {
    await page.goto(BASE_URL);
    const navLinks = page.locator('nav a, header a');
    const count = await navLinks.count();
    expect(count).toBeGreaterThan(0);
  });

  test('no console errors on load', async ({ page }) => {
    const errors = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    expect(errors.filter((e) => !e.includes('favicon') && !e.includes('cookie'))).toHaveLength(0);
  });

  test('mobile viewport renders correctly', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(BASE_URL);
    await expect(page.locator('body')).toBeVisible();
  });
});
