import { expect, test } from '@playwright/test';

test.describe('HeadFade Live Site E2E Tests', () => {
  test('should load the homepage and display correct elements', async ({ page }) => {
    // Navigate to the live site
    await page.goto('https://headfade.web.app/');

    // Check title or main heading
    await expect(page.locator('h1')).toContainText('HeadFade');

    // Check subheading
    await expect(
      page.getByText('The Global Turing Test — Can You Tell What Is Real?'),
    ).toBeVisible();

    // Check voting buttons
    await expect(page.getByRole('button', { name: 'Vote Real' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Vote AI' })).toBeVisible();

    // Check for the terminal output
    await expect(
      page.getByText('> SECURE TERMINAL: Awaiting Human Deception Input...'),
    ).toBeVisible();

    // Check footer links
    await expect(page.getByRole('link', { name: 'Creator Marketplace' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Embed Player Demo' })).toBeVisible();
  });

  test('should simulate user voting interactions', async ({ page }) => {
    await page.goto('https://headfade.web.app/');

    // Ensure button is visible before clicking
    const voteAiBtn = page.getByRole('button', { name: 'Vote AI' });
    await expect(voteAiBtn).toBeVisible();

    // Simulate voting
    await voteAiBtn.click();

    // Expect the terminal to update to analyzing state or verdict
    await expect(page.locator('.terminal-window')).toContainText(/analyzing|verdict|hdi/i, {
      timeout: 10000,
    });
  });
});
