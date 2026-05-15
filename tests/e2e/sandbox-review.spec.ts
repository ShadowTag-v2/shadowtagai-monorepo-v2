// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

/**
 * E2E Playwright Tests — Sandbox Attorney Diff Review
 *
 * Phase 3 Milestone 3: Validates the full attorney flow:
 *   1. Navigate to /sandbox/{session-id}?matter={matter-id}
 *   2. Verify DiffView renders with file navigator
 *   3. Select files for cherry-pick
 *   4. Accept / reject / partial accept decisions
 *   5. Verify success/error state transitions
 *
 * Prerequisites:
 *   - Dev server running on localhost:3000
 *   - Mock sandbox session API returning test diffs
 */

import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3000';
const TEST_SESSION_ID = 'test-session-001';
const TEST_MATTER_ID = 'matter-001';

test.describe('Sandbox Attorney Diff Review', () => {
  test.beforeEach(async ({ page }) => {
    // Mock the diffs API endpoint
    await page.route(`**/api/sandbox/${TEST_SESSION_ID}/diffs*`, (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          sessionId: TEST_SESSION_ID,
          matterId: TEST_MATTER_ID,
          diffs: [
            {
              path: 'research/memo.md',
              language: 'markdown',
              hunks: [
                {
                  oldStart: 1,
                  oldLines: 3,
                  newStart: 1,
                  newLines: 5,
                  changes: [
                    { type: 'context', content: '# Research Memo', lineNumber: 1 },
                    { type: 'delete', content: 'Old findings', lineNumber: 2 },
                    { type: 'add', content: 'New findings with AI analysis', lineNumber: 2 },
                    { type: 'add', content: 'Additional context added', lineNumber: 3 },
                    { type: 'context', content: '', lineNumber: 4 },
                  ],
                },
              ],
              privilegeStatus: 'privileged',
              aiConfidence: 0.87,
              originalHash: 'abc123',
              overlayHash: 'def456',
              hunkCount: 1,
            },
            {
              path: 'contracts/draft.py',
              language: 'python',
              hunks: [
                {
                  oldStart: 1,
                  oldLines: 2,
                  newStart: 1,
                  newLines: 3,
                  changes: [
                    { type: 'context', content: 'def validate():', lineNumber: 1 },
                    { type: 'delete', content: '    return False', lineNumber: 2 },
                    { type: 'add', content: '    # AI-enhanced validation', lineNumber: 2 },
                    { type: 'add', content: '    return True', lineNumber: 3 },
                  ],
                },
              ],
              privilegeStatus: 'work_product',
              aiConfidence: 0.92,
              originalHash: 'ghi789',
              overlayHash: 'jkl012',
              hunkCount: 1,
            },
          ],
          fileCount: 2,
        }),
      });
    });
  });

  test('renders diff view with file navigator', async ({ page }) => {
    await page.goto(`${BASE_URL}/sandbox/${TEST_SESSION_ID}?matter=${TEST_MATTER_ID}`);

    // Wait for diff view to load
    await expect(page.getByLabel(`Diff review for session ${TEST_SESSION_ID}`)).toBeVisible();

    // Verify file navigator shows both files
    await expect(page.getByText('research/memo.md')).toBeVisible();
    await expect(page.getByText('contracts/draft.py')).toBeVisible();
  });

  test('shows privilege badges on privileged files', async ({ page }) => {
    await page.goto(`${BASE_URL}/sandbox/${TEST_SESSION_ID}?matter=${TEST_MATTER_ID}`);

    // Privileged badge should be visible
    await expect(page.getByText('Privileged')).toBeVisible();
    await expect(page.getByText('Work Product')).toBeVisible();
  });

  test('displays confidence badges', async ({ page }) => {
    await page.goto(`${BASE_URL}/sandbox/${TEST_SESSION_ID}?matter=${TEST_MATTER_ID}`);

    // Confidence scores should display
    await expect(page.getByText('87%')).toBeVisible();
    await expect(page.getByText('92%')).toBeVisible();
  });

  test('can accept all changes', async ({ page }) => {
    // Mock the commit endpoint
    await page.route(`**/api/sandbox/${TEST_SESSION_ID}/commit`, (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          committedFiles: ['research/memo.md', 'contracts/draft.py'],
          rejectedFiles: [],
          auditId: 'audit-001',
          durationMs: 142,
        }),
      });
    });

    await page.goto(`${BASE_URL}/sandbox/${TEST_SESSION_ID}?matter=${TEST_MATTER_ID}`);

    // Click accept button
    const acceptBtn = page.getByRole('button', { name: /accept/i });
    await expect(acceptBtn).toBeVisible();
    await acceptBtn.click();

    // Verify success state
    await expect(page.getByText('Decision Recorded')).toBeVisible();
    await expect(page.getByText('2 file(s) committed')).toBeVisible();
    await expect(page.getByText('audit-001')).toBeVisible();
  });

  test('can reject all changes', async ({ page }) => {
    await page.route(`**/api/sandbox/${TEST_SESSION_ID}/commit`, (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          committedFiles: [],
          rejectedFiles: ['research/memo.md', 'contracts/draft.py'],
          auditId: 'audit-002',
          durationMs: 89,
        }),
      });
    });

    await page.goto(`${BASE_URL}/sandbox/${TEST_SESSION_ID}?matter=${TEST_MATTER_ID}`);

    const rejectBtn = page.getByRole('button', { name: /reject/i });
    await expect(rejectBtn).toBeVisible();
    await rejectBtn.click();

    await expect(page.getByText('Decision Recorded')).toBeVisible();
    await expect(page.getByText('2 file(s) rejected')).toBeVisible();
  });

  test('shows error state on API failure', async ({ page }) => {
    // Override the diffs mock to return error
    await page.route(`**/api/sandbox/${TEST_SESSION_ID}/diffs*`, (route) => {
      route.fulfill({
        status: 403,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Trust Level violation' }),
      });
    });

    await page.goto(`${BASE_URL}/sandbox/${TEST_SESSION_ID}?matter=${TEST_MATTER_ID}`);

    await expect(page.getByText('Session Error')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Retry' })).toBeVisible();
  });

  test('shows empty state when no diffs', async ({ page }) => {
    // Override the diffs mock to return empty
    await page.route(`**/api/sandbox/${TEST_SESSION_ID}/diffs*`, (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          sessionId: TEST_SESSION_ID,
          matterId: TEST_MATTER_ID,
          diffs: [],
          fileCount: 0,
        }),
      });
    });

    await page.goto(`${BASE_URL}/sandbox/${TEST_SESSION_ID}?matter=${TEST_MATTER_ID}`);

    await expect(page.getByText('No changes detected')).toBeVisible();
  });
});
