// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

/**
 * E2E Tests — Attorney DiffView Interaction Flow
 *
 * Playwright tests covering the sandbox session page lifecycle:
 *   1. Session loads → DiffView renders
 *   2. Attorney navigates files via FileNavigator
 *   3. Attorney toggles file selection (partial accept mode)
 *   4. Accept/reject decisions trigger commit
 *   5. WebSocket status indicator is visible
 *   6. Error states render correctly
 *   7. Committed state shows audit trail
 *
 * These tests run against a local dev server with mock API responses.
 * The API routes are intercepted via Playwright's route() to avoid
 * requiring a running Python backend.
 */

import { expect, test, type Page } from '@playwright/test';

// ── Mock Data ─────────────────────────────────────────────────

const MOCK_SESSION_ID = 'e2e-test-session-abc123';
const MOCK_MATTER_ID = 'matter-civil-2026-001';

const MOCK_DIFFS = [
  {
    path: 'contracts/engagement-letter.md',
    language: 'markdown',
    hunks: [
      {
        oldStart: 1,
        oldLines: 3,
        newStart: 1,
        newLines: 4,
        changes: [
          { type: 'context', content: '# Engagement Letter', lineNumber: 1 },
          { type: 'delete', content: 'Fee: $500/hr', lineNumber: 2 },
          { type: 'add', content: 'Fee: $450/hr (revised)', lineNumber: 2 },
          { type: 'context', content: 'Scope: Full representation', lineNumber: 3 },
        ],
      },
    ],
    privilegeStatus: 'privileged',
    aiConfidence: 0.92,
    originalHash: 'abc123',
    overlayHash: 'def456',
    hunkCount: 1,
  },
  {
    path: 'memos/research-summary.md',
    language: 'markdown',
    hunks: [
      {
        oldStart: 5,
        oldLines: 2,
        newStart: 5,
        newLines: 3,
        changes: [
          { type: 'context', content: '## Case Analysis', lineNumber: 5 },
          { type: 'add', content: 'New precedent found: *Smith v. Jones* (2026)', lineNumber: 6 },
          { type: 'context', content: '## Conclusion', lineNumber: 7 },
        ],
      },
    ],
    privilegeStatus: 'work_product',
    aiConfidence: 0.85,
    originalHash: 'ghi789',
    overlayHash: 'jkl012',
    hunkCount: 1,
  },
];

const MOCK_COMMIT_RESULT = {
  success: true,
  committed_files: ['contracts/engagement-letter.md', 'memos/research-summary.md'],
  rejected_files: [],
  audit_id: 'audit-e2e-test-001',
  duration_ms: 142,
};

// ── Helpers ───────────────────────────────────────────────────

async function setupApiMocks(page: Page) {
  // Mock diffs endpoint
  await page.route(`**/api/sandbox/${MOCK_SESSION_ID}/diffs*`, (route) => {
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        session_id: MOCK_SESSION_ID,
        matter_id: MOCK_MATTER_ID,
        diffs: MOCK_DIFFS,
        file_count: MOCK_DIFFS.length,
      }),
    });
  });

  // Mock commit endpoint
  await page.route(`**/api/sandbox/${MOCK_SESSION_ID}/commit`, (route) => {
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(MOCK_COMMIT_RESULT),
    });
  });

  // Mock telemetry endpoint (swallow silently)
  await page.route('**/api/ops/telemetry', (route) => {
    return route.fulfill({ status: 200, body: '{}' });
  });
}

// ── Tests ─────────────────────────────────────────────────────

test.describe('Sandbox Session — Attorney DiffView Flow', () => {
  const SESSION_URL = `/sandbox/${MOCK_SESSION_ID}?matter=${MOCK_MATTER_ID}`;

  test.beforeEach(async ({ page }) => {
    await setupApiMocks(page);
  });

  test('renders DiffView with file list after loading', async ({ page }) => {
    await page.goto(SESSION_URL);

    // Wait for loading to complete
    await expect(page.getByText('Sandbox Review')).toBeVisible({ timeout: 10_000 });

    // File navigator should list both files
    await expect(page.getByText('engagement-letter.md')).toBeVisible();
    await expect(page.getByText('research-summary.md')).toBeVisible();

    // Matter ID should be displayed
    await expect(page.getByText(MOCK_MATTER_ID)).toBeVisible();
  });

  test('shows session ID prefix in header', async ({ page }) => {
    await page.goto(SESSION_URL);
    await expect(page.getByText('Sandbox Review')).toBeVisible({ timeout: 10_000 });

    // Session badge shows prefix
    await expect(page.getByText(MOCK_SESSION_ID.slice(0, 8))).toBeVisible();
  });

  test('navigating files scrolls to selected file', async ({ page }) => {
    await page.goto(SESSION_URL);
    await expect(page.getByText('Sandbox Review')).toBeVisible({ timeout: 10_000 });

    // Click on second file in navigator
    await page.getByText('research-summary.md').click();

    // The diff content for that file should be visible
    await expect(page.getByText('Case Analysis')).toBeVisible();
  });

  test('shows privilege badges on files', async ({ page }) => {
    await page.goto(SESSION_URL);
    await expect(page.getByText('Sandbox Review')).toBeVisible({ timeout: 10_000 });

    // Privileged badge should appear
    await expect(page.getByText('Privileged', { exact: true }).first()).toBeVisible();
  });

  test('accept decision submits and shows success', async ({ page }) => {
    await page.goto(SESSION_URL);
    await expect(page.getByText('Sandbox Review')).toBeVisible({ timeout: 10_000 });

    // Click accept button
    const acceptButton = page.getByRole('button', { name: /accept/i });
    await expect(acceptButton).toBeVisible();
    await acceptButton.click();

    // Should transition to committed state
    await expect(page.getByText('Decision Recorded')).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText('2 file(s) committed')).toBeVisible();
    await expect(page.getByText('audit-e2e-test-001')).toBeVisible();
  });

  test('reject decision submits correctly', async ({ page }) => {
    await page.goto(SESSION_URL);
    await expect(page.getByText('Sandbox Review')).toBeVisible({ timeout: 10_000 });

    const rejectButton = page.getByRole('button', { name: /reject/i });
    await expect(rejectButton).toBeVisible();
    await rejectButton.click();

    // Should still show Decision Recorded (server mock returns success)
    await expect(page.getByText('Decision Recorded')).toBeVisible({ timeout: 5_000 });
  });

  test('WebSocket status indicator is visible', async ({ page }) => {
    await page.goto(SESSION_URL);
    await expect(page.getByText('Sandbox Review')).toBeVisible({ timeout: 10_000 });

    // WS status indicator should be present (will show Offline in E2E since no WS server)
    const wsStatus = page.locator('[data-state]');
    await expect(wsStatus).toBeVisible();
  });

  test('error state renders with retry button', async ({ page }) => {
    // Override diffs endpoint to return error
    await page.route(`**/api/sandbox/${MOCK_SESSION_ID}/diffs*`, (route) => {
      return route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal server error' }),
      });
    });

    await page.goto(SESSION_URL);

    // Error state
    await expect(page.getByText('Session Error')).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText('Internal server error')).toBeVisible();

    // Retry button present
    const retryBtn = page.getByRole('button', { name: /retry/i });
    await expect(retryBtn).toBeVisible();
  });

  test('empty diffs state renders correctly', async ({ page }) => {
    // Override to return empty diffs
    await page.route(`**/api/sandbox/${MOCK_SESSION_ID}/diffs*`, (route) => {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          session_id: MOCK_SESSION_ID,
          matter_id: MOCK_MATTER_ID,
          diffs: [],
          file_count: 0,
        }),
      });
    });

    await page.goto(SESSION_URL);

    await expect(page.getByText('No changes detected')).toBeVisible({ timeout: 10_000 });
  });

  test('AI confidence badges are displayed', async ({ page }) => {
    await page.goto(SESSION_URL);
    await expect(page.getByText('Sandbox Review')).toBeVisible({ timeout: 10_000 });

    // Confidence score should be visible (92% for first file)
    await expect(page.getByText('92%')).toBeVisible();
  });
});
