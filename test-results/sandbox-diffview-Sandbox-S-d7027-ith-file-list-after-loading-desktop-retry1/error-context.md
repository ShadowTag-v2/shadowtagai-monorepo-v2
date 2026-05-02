# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: sandbox-diffview.spec.ts >> Sandbox Session — Attorney DiffView Flow >> renders DiffView with file list after loading
- Location: tests/e2e/sandbox-diffview.spec.ts:124:7

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByText('Sandbox Review')
Expected: visible
Timeout: 10000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 10000ms
  - waiting for getByText('Sandbox Review')

```

# Page snapshot

```yaml
- generic [ref=e3]:
  - heading "404" [level=1] [ref=e4]
  - heading "This page could not be found." [level=2] [ref=e6]
```

# Test source

```ts
  28  |   {
  29  |     path: 'contracts/engagement-letter.md',
  30  |     language: 'markdown',
  31  |     hunks: [
  32  |       {
  33  |         oldStart: 1,
  34  |         oldLines: 3,
  35  |         newStart: 1,
  36  |         newLines: 4,
  37  |         changes: [
  38  |           { type: 'context', content: '# Engagement Letter', lineNumber: 1 },
  39  |           { type: 'delete', content: 'Fee: $500/hr', lineNumber: 2 },
  40  |           { type: 'add', content: 'Fee: $450/hr (revised)', lineNumber: 2 },
  41  |           { type: 'context', content: 'Scope: Full representation', lineNumber: 3 },
  42  |         ],
  43  |       },
  44  |     ],
  45  |     privilegeStatus: 'privileged',
  46  |     aiConfidence: 0.92,
  47  |     originalHash: 'abc123',
  48  |     overlayHash: 'def456',
  49  |     hunkCount: 1,
  50  |   },
  51  |   {
  52  |     path: 'memos/research-summary.md',
  53  |     language: 'markdown',
  54  |     hunks: [
  55  |       {
  56  |         oldStart: 5,
  57  |         oldLines: 2,
  58  |         newStart: 5,
  59  |         newLines: 3,
  60  |         changes: [
  61  |           { type: 'context', content: '## Case Analysis', lineNumber: 5 },
  62  |           { type: 'add', content: 'New precedent found: *Smith v. Jones* (2026)', lineNumber: 6 },
  63  |           { type: 'context', content: '## Conclusion', lineNumber: 7 },
  64  |         ],
  65  |       },
  66  |     ],
  67  |     privilegeStatus: 'work_product',
  68  |     aiConfidence: 0.85,
  69  |     originalHash: 'ghi789',
  70  |     overlayHash: 'jkl012',
  71  |     hunkCount: 1,
  72  |   },
  73  | ];
  74  | 
  75  | const MOCK_COMMIT_RESULT = {
  76  |   success: true,
  77  |   committed_files: ['contracts/engagement-letter.md', 'memos/research-summary.md'],
  78  |   rejected_files: [],
  79  |   audit_id: 'audit-e2e-test-001',
  80  |   duration_ms: 142,
  81  | };
  82  | 
  83  | // ── Helpers ───────────────────────────────────────────────────
  84  | 
  85  | async function setupApiMocks(page: Page) {
  86  |   // Mock diffs endpoint
  87  |   await page.route(`**/api/sandbox/${MOCK_SESSION_ID}/diffs*`, (route) => {
  88  |     return route.fulfill({
  89  |       status: 200,
  90  |       contentType: 'application/json',
  91  |       body: JSON.stringify({
  92  |         session_id: MOCK_SESSION_ID,
  93  |         matter_id: MOCK_MATTER_ID,
  94  |         diffs: MOCK_DIFFS,
  95  |         file_count: MOCK_DIFFS.length,
  96  |       }),
  97  |     });
  98  |   });
  99  | 
  100 |   // Mock commit endpoint
  101 |   await page.route(`**/api/sandbox/${MOCK_SESSION_ID}/commit`, (route) => {
  102 |     return route.fulfill({
  103 |       status: 200,
  104 |       contentType: 'application/json',
  105 |       body: JSON.stringify(MOCK_COMMIT_RESULT),
  106 |     });
  107 |   });
  108 | 
  109 |   // Mock telemetry endpoint (swallow silently)
  110 |   await page.route('**/api/ops/telemetry', (route) => {
  111 |     return route.fulfill({ status: 200, body: '{}' });
  112 |   });
  113 | }
  114 | 
  115 | // ── Tests ─────────────────────────────────────────────────────
  116 | 
  117 | test.describe('Sandbox Session — Attorney DiffView Flow', () => {
  118 |   const SESSION_URL = `/sandbox/${MOCK_SESSION_ID}?matter=${MOCK_MATTER_ID}`;
  119 | 
  120 |   test.beforeEach(async ({ page }) => {
  121 |     await setupApiMocks(page);
  122 |   });
  123 | 
  124 |   test('renders DiffView with file list after loading', async ({ page }) => {
  125 |     await page.goto(SESSION_URL);
  126 | 
  127 |     // Wait for loading to complete
> 128 |     await expect(page.getByText('Sandbox Review')).toBeVisible({ timeout: 10_000 });
      |                                                    ^ Error: expect(locator).toBeVisible() failed
  129 | 
  130 |     // File navigator should list both files
  131 |     await expect(page.getByText('engagement-letter.md')).toBeVisible();
  132 |     await expect(page.getByText('research-summary.md')).toBeVisible();
  133 | 
  134 |     // Matter ID should be displayed
  135 |     await expect(page.getByText(MOCK_MATTER_ID)).toBeVisible();
  136 |   });
  137 | 
  138 |   test('shows session ID prefix in header', async ({ page }) => {
  139 |     await page.goto(SESSION_URL);
  140 |     await expect(page.getByText('Sandbox Review')).toBeVisible({ timeout: 10_000 });
  141 | 
  142 |     // Session badge shows prefix
  143 |     await expect(page.getByText(MOCK_SESSION_ID.slice(0, 8))).toBeVisible();
  144 |   });
  145 | 
  146 |   test('navigating files scrolls to selected file', async ({ page }) => {
  147 |     await page.goto(SESSION_URL);
  148 |     await expect(page.getByText('Sandbox Review')).toBeVisible({ timeout: 10_000 });
  149 | 
  150 |     // Click on second file in navigator
  151 |     await page.getByText('research-summary.md').click();
  152 | 
  153 |     // The diff content for that file should be visible
  154 |     await expect(page.getByText('Case Analysis')).toBeVisible();
  155 |   });
  156 | 
  157 |   test('shows privilege badges on files', async ({ page }) => {
  158 |     await page.goto(SESSION_URL);
  159 |     await expect(page.getByText('Sandbox Review')).toBeVisible({ timeout: 10_000 });
  160 | 
  161 |     // Privileged badge should appear
  162 |     await expect(page.getByText('Privileged', { exact: true }).first()).toBeVisible();
  163 |   });
  164 | 
  165 |   test('accept decision submits and shows success', async ({ page }) => {
  166 |     await page.goto(SESSION_URL);
  167 |     await expect(page.getByText('Sandbox Review')).toBeVisible({ timeout: 10_000 });
  168 | 
  169 |     // Click accept button
  170 |     const acceptButton = page.getByRole('button', { name: /accept/i });
  171 |     await expect(acceptButton).toBeVisible();
  172 |     await acceptButton.click();
  173 | 
  174 |     // Should transition to committed state
  175 |     await expect(page.getByText('Decision Recorded')).toBeVisible({ timeout: 5_000 });
  176 |     await expect(page.getByText('2 file(s) committed')).toBeVisible();
  177 |     await expect(page.getByText('audit-e2e-test-001')).toBeVisible();
  178 |   });
  179 | 
  180 |   test('reject decision submits correctly', async ({ page }) => {
  181 |     await page.goto(SESSION_URL);
  182 |     await expect(page.getByText('Sandbox Review')).toBeVisible({ timeout: 10_000 });
  183 | 
  184 |     const rejectButton = page.getByRole('button', { name: /reject/i });
  185 |     await expect(rejectButton).toBeVisible();
  186 |     await rejectButton.click();
  187 | 
  188 |     // Should still show Decision Recorded (server mock returns success)
  189 |     await expect(page.getByText('Decision Recorded')).toBeVisible({ timeout: 5_000 });
  190 |   });
  191 | 
  192 |   test('WebSocket status indicator is visible', async ({ page }) => {
  193 |     await page.goto(SESSION_URL);
  194 |     await expect(page.getByText('Sandbox Review')).toBeVisible({ timeout: 10_000 });
  195 | 
  196 |     // WS status indicator should be present (will show Offline in E2E since no WS server)
  197 |     const wsStatus = page.locator('[data-state]');
  198 |     await expect(wsStatus).toBeVisible();
  199 |   });
  200 | 
  201 |   test('error state renders with retry button', async ({ page }) => {
  202 |     // Override diffs endpoint to return error
  203 |     await page.route(`**/api/sandbox/${MOCK_SESSION_ID}/diffs*`, (route) => {
  204 |       return route.fulfill({
  205 |         status: 500,
  206 |         contentType: 'application/json',
  207 |         body: JSON.stringify({ error: 'Internal server error' }),
  208 |       });
  209 |     });
  210 | 
  211 |     await page.goto(SESSION_URL);
  212 | 
  213 |     // Error state
  214 |     await expect(page.getByText('Session Error')).toBeVisible({ timeout: 10_000 });
  215 |     await expect(page.getByText('Internal server error')).toBeVisible();
  216 | 
  217 |     // Retry button present
  218 |     const retryBtn = page.getByRole('button', { name: /retry/i });
  219 |     await expect(retryBtn).toBeVisible();
  220 |   });
  221 | 
  222 |   test('empty diffs state renders correctly', async ({ page }) => {
  223 |     // Override to return empty diffs
  224 |     await page.route(`**/api/sandbox/${MOCK_SESSION_ID}/diffs*`, (route) => {
  225 |       return route.fulfill({
  226 |         status: 200,
  227 |         contentType: 'application/json',
  228 |         body: JSON.stringify({
```