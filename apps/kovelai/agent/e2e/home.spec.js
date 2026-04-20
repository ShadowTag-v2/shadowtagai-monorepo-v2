// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * KovelAI Production E2E Tests
 * Tests the deployed static site at kovelai.web.app.
 * Run: npx playwright test --config=playwright.config.js
 */

const BASE_URL = process.env.KOVELAI_URL || 'https://kovelai.web.app';

test.describe('KovelAI Homepage — Structure & SEO', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
  });

  test('page loads with 200 status', async ({ page }) => {
    const response = await page.goto(BASE_URL);
    expect(response.status()).toBe(200);
  });

  test('has correct title', async ({ page }) => {
    await expect(page).toHaveTitle(/CounselConduit.*Legal AI/);
  });

  test('has meta description', async ({ page }) => {
    const desc = await page.getAttribute('meta[name="description"]', 'content');
    expect(desc).toBeTruthy();
    expect(desc.length).toBeGreaterThan(50);
  });

  test('has Open Graph tags', async ({ page }) => {
    const ogTitle = await page.getAttribute('meta[property="og:title"]', 'content');
    const ogDesc = await page.getAttribute('meta[property="og:description"]', 'content');
    const ogUrl = await page.getAttribute('meta[property="og:url"]', 'content');
    expect(ogTitle).toBeTruthy();
    expect(ogDesc).toBeTruthy();
    expect(ogUrl).toContain('kovelai');
  });

  test('has JSON-LD structured data', async ({ page }) => {
    const jsonLd = await page.$eval('script[type="application/ld+json"]', (el) => el.textContent);
    const data = JSON.parse(jsonLd);
    expect(data['@context']).toBe('https://schema.org');
    expect(data['@type']).toBe('SoftwareApplication');
    expect(data.name).toBe('CounselConduit');
    expect(data.offers).toBeTruthy();
  });

  test('has single h1 element', async ({ page }) => {
    const h1Count = await page.locator('h1').count();
    expect(h1Count).toBe(1);
  });

  test('has manifest.json linked', async ({ page }) => {
    const manifest = await page.getAttribute('link[rel="manifest"]', 'href');
    expect(manifest).toBe('/manifest.json');
  });
});

test.describe('KovelAI Homepage — Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
  });

  test('nav has correct links', async ({ page }) => {
    const features = page.locator('nav a[href="#features"]');
    const pricing = page.locator('nav a[href="#pricing"]');
    const security = page.locator('nav a[href="#security"]');
    await expect(features).toBeVisible();
    await expect(pricing).toBeVisible();
    await expect(security).toBeVisible();
  });

  test('skip-nav link exists for a11y', async ({ page }) => {
    const skipNav = page.locator('.skip-nav');
    await expect(skipNav).toHaveAttribute('href', '#features');
  });

  test('CTA button has correct ID', async ({ page }) => {
    const cta = page.locator('#cta-start');
    await expect(cta).toBeVisible();
    await expect(cta).toContainText('Request Access');
  });
});

test.describe('KovelAI Homepage — CTA Buttons', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
  });

  test('Solo pricing CTA exists with correct ID', async ({ page }) => {
    const cta = page.locator('#cta-solo');
    await expect(cta).toBeAttached();
    await expect(cta).toContainText(/Get Started/i);
  });

  test('Practice pricing CTA exists with correct ID', async ({ page }) => {
    const cta = page.locator('#cta-practice');
    await expect(cta).toBeAttached();
    await expect(cta).toContainText(/Get Started/i);
  });

  test('Enterprise pricing CTA exists with correct ID', async ({ page }) => {
    const cta = page.locator('#cta-enterprise');
    await expect(cta).toBeAttached();
    await expect(cta).toContainText(/Contact Sales/i);
  });
});

test.describe('KovelAI Homepage — Features Section', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
  });

  test('features section renders 6 cards', async ({ page }) => {
    const cards = page.locator('.feature-card');
    await expect(cards).toHaveCount(6);
  });

  test('feature cards have titles and descriptions', async ({ page }) => {
    const titles = ['Kovel Attestation', 'Multi-Model Routing', 'Judge #6 Policy Gate',
                    'Oracle Studio', 'Ephemeral Client View', 'Immutable Transcripts'];
    for (const title of titles) {
      const card = page.locator('.feature-card', { hasText: title });
      await expect(card).toBeAttached();
    }
  });
});

test.describe('KovelAI Homepage — Pricing Section', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
  });

  test('renders 3 pricing cards', async ({ page }) => {
    const cards = page.locator('.pricing-card');
    await expect(cards).toHaveCount(3);
  });

  test('shows correct pricing amounts', async ({ page }) => {
    await expect(page.locator('.pricing-card').filter({ hasText: 'Solo' })).toContainText('$299');
    await expect(page.locator('.pricing-card').filter({ hasText: 'Practice' })).toContainText('$599');
    await expect(page.locator('.pricing-card').filter({ hasText: 'Enterprise' })).toContainText('$999');
  });

  test('Practice card is featured', async ({ page }) => {
    const featured = page.locator('.pricing-card.featured');
    await expect(featured).toHaveCount(1);
    await expect(featured).toContainText('Practice');
  });
});

test.describe('KovelAI Homepage — GA4 & Scripts', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
  });

  test('GA4 script tag loads', async ({ page }) => {
    const ga4Script = page.locator('script[src*="googletagmanager.com/gtag/js"]');
    await expect(ga4Script).toBeAttached();
  });

  test('external ga4.js loads', async ({ page }) => {
    const ga4External = page.locator('script[src="/js/ga4.js"]');
    await expect(ga4External).toBeAttached();
  });

  test('scroll-frames.js loads', async ({ page }) => {
    const scrollFrames = page.locator('script[src="scroll-frames.js"]');
    await expect(scrollFrames).toBeAttached();
  });
});

test.describe('KovelAI Homepage — Responsive Design', () => {
  test('renders on mobile viewport (375px)', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    const h1 = page.locator('h1');
    await expect(h1).toBeVisible();
  });

  test('nav links hidden on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    const navLinks = page.locator('.nav-links');
    await expect(navLinks).toBeHidden();
  });

  test('pricing stacks to single column on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    const grid = page.locator('.pricing-grid');
    const style = await grid.evaluate((el) => getComputedStyle(el).gridTemplateColumns);
    // On mobile, should be single column
    const columnCount = style.split(' ').length;
    expect(columnCount).toBe(1);
  });
});

test.describe('KovelAI Homepage — A11y Basics', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
  });

  test('main landmark exists', async ({ page }) => {
    const main = page.locator('main#main-content');
    await expect(main).toBeAttached();
  });

  test('nav has aria-label', async ({ page }) => {
    const nav = page.locator('nav[aria-label]');
    await expect(nav).toBeAttached();
  });

  test('footer has contentinfo role', async ({ page }) => {
    const footer = page.locator('footer[role="contentinfo"]');
    await expect(footer).toBeAttached();
  });

  test('canvas has aria-label', async ({ page }) => {
    const canvas = page.locator('#scroll-canvas[aria-label]');
    await expect(canvas).toBeAttached();
  });

  test('CTA buttons have meaningful text', async ({ page }) => {
    const startBtn = page.locator('#cta-start');
    await expect(startBtn).toHaveAttribute('aria-label', /Request access/i);
  });
});

test.describe('KovelAI Homepage — Security Headers', () => {
  test('returns correct security headers', async ({ page }) => {
    const response = await page.goto(BASE_URL);
    const headers = response.headers();

    // CSP present and no unsafe-eval
    const csp = headers['content-security-policy'] || '';
    expect(csp).toContain("default-src 'self'");
    expect(csp).not.toContain('unsafe-eval');

    // X-Content-Type-Options
    expect(headers['x-content-type-options']).toBe('nosniff');

    // X-Frame-Options
    expect(headers['x-frame-options']).toBe('DENY');
  });
});
