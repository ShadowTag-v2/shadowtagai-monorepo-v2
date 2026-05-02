# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: sandbox-diffview.spec.ts >> Sandbox Session — Attorney DiffView Flow >> error state renders with retry button
- Location: tests/e2e/sandbox-diffview.spec.ts:201:7

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByText('Session Error')
Expected: visible
Timeout: 10000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 10000ms
  - waiting for getByText('Session Error')

```

# Page snapshot

```yaml
- generic [ref=e3]:
  - heading "404" [level=1] [ref=e4]
  - heading "This page could not be found." [level=2] [ref=e6]
```

# Test source

```ts
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
  128 |     await expect(page.getByText('Sandbox Review')).toBeVisible({ timeout: 10_000 });
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
> 214 |     await expect(page.getByText('Session Error')).toBeVisible({ timeout: 10_000 });
      |                                                   ^ Error: expect(locator).toBeVisible() failed
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
  229 |           session_id: MOCK_SESSION_ID,
  230 |           matter_id: MOCK_MATTER_ID,
  231 |           diffs: [],
  232 |           file_count: 0,
  233 |         }),
  234 |       });
  235 |     });
  236 | 
  237 |     await page.goto(SESSION_URL);
  238 | 
  239 |     await expect(page.getByText('No changes detected')).toBeVisible({ timeout: 10_000 });
  240 |   });
  241 | 
  242 |   test('AI confidence badges are displayed', async ({ page }) => {
  243 |     await page.goto(SESSION_URL);
  244 |     await expect(page.getByText('Sandbox Review')).toBeVisible({ timeout: 10_000 });
  245 | 
  246 |     // Confidence score should be visible (92% for first file)
  247 |     await expect(page.getByText('92%')).toBeVisible();
  248 |   });
  249 | });
  250 | 
```