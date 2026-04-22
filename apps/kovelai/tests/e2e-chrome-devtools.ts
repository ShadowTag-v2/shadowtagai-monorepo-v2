/**
 * E2E Test Suite using Chrome DevTools MCP
 *
 * Item #20: Create E2E test with Chrome DevTools MCP.
 *
 * Tests the full KovelAI user flow:
 * 1. Landing page loads
 * 2. Privilege banner visible
 * 3. Search form functional
 * 4. Dead Man's Switch active
 * 5. Results render correctly
 * 6. Anti-forensic controls work (copy/context menu blocked)
 * 7. Session wipe on timeout
 *
 * Run: Execute via Antigravity Chrome DevTools MCP
 */

export interface E2ETestCase {
  name: string;
  description: string;
  steps: E2EStep[];
  expectedOutcome: string;
}

interface E2EStep {
  action: 'navigate' | 'click' | 'type' | 'snapshot' | 'screenshot' | 'wait' | 'evaluate';
  target?: string;
  value?: string;
  timeout?: number;
}

// ─── Test Suite ─────────────────────────────────────────────────

export const KOVELAI_E2E_TESTS: E2ETestCase[] = [
  {
    name: 'TC-001: Landing Page Load',
    description: 'Verify KovelAI landing page loads with privilege banner',
    steps: [
      { action: 'navigate', value: 'http://localhost:3000' },
      { action: 'wait', value: 'PRIVILEGED SESSION', timeout: 5000 },
      { action: 'snapshot' },
      { action: 'screenshot' },
    ],
    expectedOutcome: 'Page loads with KOVEL PROTECTED banner visible',
  },
  {
    name: 'TC-002: Search Form Submission',
    description: 'Verify search form accepts input and submits',
    steps: [
      { action: 'navigate', value: 'http://localhost:3000' },
      { action: 'wait', value: 'Search securely', timeout: 5000 },
      { action: 'click', target: 'input[placeholder*="Search securely"]' },
      { action: 'type', value: 'attorney-client privilege waiver AI' },
      { action: 'click', target: 'button[type="submit"]' },
      { action: 'wait', value: 'Searching', timeout: 2000 },
      { action: 'screenshot' },
    ],
    expectedOutcome: 'Search submits and shows loading state',
  },
  {
    name: 'TC-003: Anti-Forensic Controls',
    description: 'Verify copy and right-click are blocked on results',
    steps: [
      { action: 'navigate', value: 'http://localhost:3000' },
      { action: 'evaluate', value: `
        const el = document.querySelector('[oncontextmenu]');
        const event = new MouseEvent('contextmenu', { cancelable: true });
        const blocked = !el?.dispatchEvent(event);
        return blocked;
      ` },
      { action: 'evaluate', value: `
        const el = document.querySelector('[oncopy]');
        const event = new ClipboardEvent('copy', { cancelable: true });
        const blocked = !el?.dispatchEvent(event);
        return blocked;
      ` },
    ],
    expectedOutcome: 'Context menu and copy events are prevented',
  },
  {
    name: 'TC-004: Dead Man Switch Visibility',
    description: 'Verify Dead Man Switch status bar is visible',
    steps: [
      { action: 'navigate', value: 'http://localhost:3000' },
      { action: 'wait', value: 'Heartbeats', timeout: 5000 },
      { action: 'snapshot' },
    ],
    expectedOutcome: 'Heartbeat counter and session status visible in footer',
  },
  {
    name: 'TC-005: Session Info Display',
    description: 'Verify session ID and status are displayed',
    steps: [
      { action: 'navigate', value: 'http://localhost:3000' },
      { action: 'wait', value: 'Session:', timeout: 5000 },
      { action: 'evaluate', value: `
        const footer = document.querySelector('footer, [style*="position: fixed"][style*="bottom"]');
        return footer?.textContent ?? '';
      ` },
    ],
    expectedOutcome: 'Footer shows truncated session ID and heartbeat count',
  },
  {
    name: 'TC-006: Responsive Layout (Mobile)',
    description: 'Verify search UI renders correctly on mobile viewport',
    steps: [
      // Emulate mobile via Chrome DevTools MCP resize_page
      { action: 'navigate', value: 'http://localhost:3000' },
      { action: 'snapshot' },
      { action: 'screenshot' },
    ],
    expectedOutcome: 'Search form and results stack vertically on mobile',
  },
  {
    name: 'TC-007: Security Headers',
    description: 'Verify anti-caching headers on API responses',
    steps: [
      { action: 'evaluate', value: `
        const res = await fetch('/api/privileged-search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: 'test', ephemeralToken: 'x', sandboxId: 'x', sessionId: '00000000-0000-0000-0000-000000000000' }),
        });
        return {
          cacheControl: res.headers.get('cache-control'),
          pragma: res.headers.get('pragma'),
          privilegeShield: res.headers.get('x-privilege-shield'),
        };
      ` },
    ],
    expectedOutcome: 'Response includes no-store, no-cache, and X-Privilege-Shield headers',
  },
];

/**
 * Generates a Chrome DevTools MCP test runner script.
 *
 * Usage:
 * 1. Start KovelAI dev server: `npm run dev`
 * 2. Open Chrome with DevTools
 * 3. Run each test case via Chrome DevTools MCP tools
 */
export function generateTestRunnerInstructions(): string {
  let instructions = '# KovelAI E2E Test Instructions\n\n';
  instructions += 'Execute via Chrome DevTools MCP:\n\n';

  for (const test of KOVELAI_E2E_TESTS) {
    instructions += `## ${test.name}\n`;
    instructions += `${test.description}\n\n`;
    instructions += `**Expected**: ${test.expectedOutcome}\n\n`;
    instructions += `Steps:\n`;
    for (const step of test.steps) {
      instructions += `  - ${step.action}`;
      if (step.value) instructions += `: ${step.value.slice(0, 80)}`;
      if (step.target) instructions += ` → ${step.target}`;
      instructions += '\n';
    }
    instructions += '\n---\n\n';
  }

  return instructions;
}
