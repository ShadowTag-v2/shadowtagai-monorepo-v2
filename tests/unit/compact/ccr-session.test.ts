/**
 * ExitPlanModeScanner unit tests — standalone.
 *
 * Tests the pure stateful classifier logic without importing from the
 * production ccrSession.ts (which has deep deps on lodash-es, debug.ts, etc.).
 * Instead we replicate the scanner logic inline for testing.
 *
 * This validates the STATE MACHINE transitions that the CCR polling loop relies on.
 */
import { describe, it, expect, beforeEach } from 'vitest';

// ── Constants & Types (mirrored from ccrSession.ts) ─────────────────────
const EXIT_PLAN_MODE_V2_TOOL_NAME = 'exit_plan_mode_v2';
const ULTRAPLAN_TELEPORT_SENTINEL = '__ULTRAPLAN_TELEPORT_LOCAL__';

type ScanResult =
  | { kind: 'approved'; plan: string }
  | { kind: 'teleport'; plan: string }
  | { kind: 'rejected'; id: string }
  | { kind: 'pending' }
  | { kind: 'terminated'; subtype: string }
  | { kind: 'unchanged' };

// Minimal message types matching SDK shape
interface ToolUseBlock { type: 'tool_use'; id: string; name: string; input: unknown }
interface ToolResultBlock { type: 'tool_result'; tool_use_id: string; content: string | { type: string; text: string }[]; is_error?: boolean }
type SDKMessage =
  | { type: 'assistant'; message: { content: (ToolUseBlock | { type: string })[] } }
  | { type: 'user'; message: { content: (ToolResultBlock | { type: string })[] } }
  | { type: 'result'; subtype: string };

// ── ExitPlanModeScanner (self-contained copy for test isolation) ─────────
class ExitPlanModeScanner {
  private exitPlanCalls: string[] = [];
  private results = new Map<string, ToolResultBlock>();
  private rejectedIds = new Set<string>();
  private terminated: { subtype: string } | null = null;
  private rescanAfterRejection = false;
  everSeenPending = false;

  get rejectCount(): number { return this.rejectedIds.size; }

  get hasPendingPlan(): boolean {
    const id = this.exitPlanCalls.findLast((c) => !this.rejectedIds.has(c));
    return id !== undefined && !this.results.has(id);
  }

  ingest(newEvents: SDKMessage[]): ScanResult {
    for (const m of newEvents) {
      if (m.type === 'assistant') {
        for (const block of m.message.content) {
          if (block.type !== 'tool_use') continue;
          const tu = block as ToolUseBlock;
          if (tu.name === EXIT_PLAN_MODE_V2_TOOL_NAME) {
            this.exitPlanCalls.push(tu.id);
          }
        }
      } else if (m.type === 'user') {
        const content = m.message.content;
        if (!Array.isArray(content)) continue;
        for (const block of content) {
          if (block.type === 'tool_result') {
            this.results.set((block as ToolResultBlock).tool_use_id, block as ToolResultBlock);
          }
        }
      } else if (m.type === 'result' && m.subtype !== 'success') {
        this.terminated = { subtype: m.subtype };
      }
    }

    const shouldScan = newEvents.length > 0 || this.rescanAfterRejection;
    this.rescanAfterRejection = false;

    let found: { kind: 'approved'; plan: string } | { kind: 'teleport'; plan: string } | { kind: 'rejected'; id: string } | { kind: 'pending' } | null = null;

    if (shouldScan) {
      for (let i = this.exitPlanCalls.length - 1; i >= 0; i--) {
        const id = this.exitPlanCalls[i]!;
        if (this.rejectedIds.has(id)) continue;
        const tr = this.results.get(id);
        if (!tr) {
          found = { kind: 'pending' };
        } else if (tr.is_error === true) {
          const teleportPlan = extractTeleportPlan(tr.content);
          found = teleportPlan !== null ? { kind: 'teleport', plan: teleportPlan } : { kind: 'rejected', id };
        } else {
          found = { kind: 'approved', plan: extractApprovedPlan(tr.content) };
        }
        break;
      }
      if (found?.kind === 'approved' || found?.kind === 'teleport') return found;
    }

    if (found?.kind === 'rejected') {
      this.rejectedIds.add(found.id);
      this.rescanAfterRejection = true;
    }
    if (this.terminated) {
      return { kind: 'terminated', subtype: this.terminated.subtype };
    }
    if (found?.kind === 'rejected') return found;
    if (found?.kind === 'pending') {
      this.everSeenPending = true;
      return found;
    }
    return { kind: 'unchanged' };
  }
}

function contentToText(content: string | { type: string; text: string }[]): string {
  return typeof content === 'string'
    ? content
    : Array.isArray(content)
      ? content.map((b) => ('text' in b ? b.text : '')).join('')
      : '';
}

function extractTeleportPlan(content: string | { type: string; text: string }[]): string | null {
  const text = contentToText(content);
  const marker = `${ULTRAPLAN_TELEPORT_SENTINEL}\n`;
  const idx = text.indexOf(marker);
  if (idx === -1) return null;
  return text.slice(idx + marker.length).trimEnd();
}

function extractApprovedPlan(content: string | { type: string; text: string }[]): string {
  const text = contentToText(content);
  const markers = ['## Approved Plan (edited by user):\n', '## Approved Plan:\n'];
  for (const marker of markers) {
    const idx = text.indexOf(marker);
    if (idx !== -1) return text.slice(idx + marker.length).trimEnd();
  }
  throw new Error(`No approved plan marker found in: ${text.slice(0, 200)}`);
}

// ── Helpers ──────────────────────────────────────────────────────────────
function toolUseMsg(id: string, name: string): SDKMessage {
  return { type: 'assistant', message: { content: [{ type: 'tool_use', id, name, input: {} }] } };
}

function toolResultMsg(toolUseId: string, content: string, isError = false): SDKMessage {
  return { type: 'user', message: { content: [{ type: 'tool_result', tool_use_id: toolUseId, content, is_error: isError }] } };
}

function terminalResult(subtype: string): SDKMessage {
  return { type: 'result', subtype };
}

// ── Tests ────────────────────────────────────────────────────────────────
describe('ExitPlanModeScanner', () => {
  let scanner: ExitPlanModeScanner;
  beforeEach(() => { scanner = new ExitPlanModeScanner(); });

  it('returns unchanged for empty event batches', () => {
    expect(scanner.ingest([])).toEqual({ kind: 'unchanged' });
  });

  it('returns unchanged for non-ExitPlanMode tool_use', () => {
    expect(scanner.ingest([toolUseMsg('tu-1', 'Bash')]).kind).toBe('unchanged');
  });

  it('returns pending when ExitPlanMode emitted but no result', () => {
    const result = scanner.ingest([toolUseMsg('tu-1', EXIT_PLAN_MODE_V2_TOOL_NAME)]);
    expect(result.kind).toBe('pending');
    expect(scanner.hasPendingPlan).toBe(true);
    expect(scanner.everSeenPending).toBe(true);
  });

  it('returns approved when tool_result with plan marker', () => {
    scanner.ingest([toolUseMsg('tu-1', EXIT_PLAN_MODE_V2_TOOL_NAME)]);
    const result = scanner.ingest([toolResultMsg('tu-1', '## Approved Plan:\nStep 1: Do it\nStep 2: Profit')]);
    expect(result.kind).toBe('approved');
    if (result.kind === 'approved') {
      expect(result.plan).toBe('Step 1: Do it\nStep 2: Profit');
    }
  });

  it('returns approved for edited plan marker', () => {
    scanner.ingest([toolUseMsg('tu-1', EXIT_PLAN_MODE_V2_TOOL_NAME)]);
    const result = scanner.ingest([toolResultMsg('tu-1', '## Approved Plan (edited by user):\nRevised step 1')]);
    expect(result.kind).toBe('approved');
    if (result.kind === 'approved') {
      expect(result.plan).toBe('Revised step 1');
    }
  });

  it('returns rejected when is_error without teleport sentinel', () => {
    scanner.ingest([toolUseMsg('tu-1', EXIT_PLAN_MODE_V2_TOOL_NAME)]);
    const result = scanner.ingest([toolResultMsg('tu-1', 'User rejected', true)]);
    expect(result.kind).toBe('rejected');
    expect(scanner.rejectCount).toBe(1);
  });

  it('returns teleport when is_error with teleport sentinel', () => {
    scanner.ingest([toolUseMsg('tu-1', EXIT_PLAN_MODE_V2_TOOL_NAME)]);
    const result = scanner.ingest([
      toolResultMsg('tu-1', `${ULTRAPLAN_TELEPORT_SENTINEL}\nExecute locally: step A`, true),
    ]);
    expect(result.kind).toBe('teleport');
    if (result.kind === 'teleport') {
      expect(result.plan).toBe('Execute locally: step A');
    }
  });

  it('returns terminated for error result subtypes', () => {
    scanner.ingest([terminalResult('error_max_turns')]);
    const result = scanner.ingest([]);
    expect(result.kind).toBe('terminated');
    if (result.kind === 'terminated') {
      expect(result.subtype).toBe('error_max_turns');
    }
  });

  it('ignores success result subtypes', () => {
    expect(scanner.ingest([terminalResult('success')]).kind).toBe('unchanged');
  });

  it('approved takes precedence over terminated in same batch', () => {
    const result = scanner.ingest([
      toolUseMsg('tu-1', EXIT_PLAN_MODE_V2_TOOL_NAME),
      toolResultMsg('tu-1', '## Approved Plan:\nThe plan'),
      terminalResult('error_during_execution'),
    ]);
    expect(result.kind).toBe('approved');
  });

  it('tracks multiple rejections correctly', () => {
    scanner.ingest([toolUseMsg('tu-1', EXIT_PLAN_MODE_V2_TOOL_NAME)]);
    scanner.ingest([toolResultMsg('tu-1', 'no', true)]);
    expect(scanner.rejectCount).toBe(1);

    scanner.ingest([toolUseMsg('tu-2', EXIT_PLAN_MODE_V2_TOOL_NAME)]);
    scanner.ingest([toolResultMsg('tu-2', 'still no', true)]);
    expect(scanner.rejectCount).toBe(2);
  });

  it('hasPendingPlan ignores rejected calls', () => {
    scanner.ingest([toolUseMsg('tu-1', EXIT_PLAN_MODE_V2_TOOL_NAME)]);
    scanner.ingest([toolResultMsg('tu-1', 'rejected', true)]);
    expect(scanner.hasPendingPlan).toBe(false);

    scanner.ingest([toolUseMsg('tu-2', EXIT_PLAN_MODE_V2_TOOL_NAME)]);
    expect(scanner.hasPendingPlan).toBe(true);
  });

  it('processes multi-round conversation with interleaved rejections', () => {
    // Round 1: propose → reject
    scanner.ingest([toolUseMsg('tu-1', EXIT_PLAN_MODE_V2_TOOL_NAME)]);
    let r = scanner.ingest([toolResultMsg('tu-1', 'bad plan', true)]);
    expect(r.kind).toBe('rejected');

    // Round 2: propose → reject
    scanner.ingest([toolUseMsg('tu-2', EXIT_PLAN_MODE_V2_TOOL_NAME)]);
    r = scanner.ingest([toolResultMsg('tu-2', 'still bad', true)]);
    expect(r.kind).toBe('rejected');

    // Round 3: propose → approve
    scanner.ingest([toolUseMsg('tu-3', EXIT_PLAN_MODE_V2_TOOL_NAME)]);
    r = scanner.ingest([toolResultMsg('tu-3', '## Approved Plan:\nFinal plan')]);
    expect(r.kind).toBe('approved');
    expect(scanner.rejectCount).toBe(2);
  });
});

describe('extractApprovedPlan', () => {
  it('throws when no plan marker present', () => {
    expect(() => extractApprovedPlan('just some text without marker')).toThrow('No approved plan marker');
  });

  it('handles array content blocks', () => {
    const plan = extractApprovedPlan([
      { type: 'text', text: '## Approved Plan:\nArray plan content' },
    ]);
    expect(plan).toBe('Array plan content');
  });
});

describe('extractTeleportPlan', () => {
  it('returns null when sentinel absent', () => {
    expect(extractTeleportPlan('no sentinel here')).toBeNull();
  });

  it('extracts plan after sentinel', () => {
    const text = `Some preamble\n${ULTRAPLAN_TELEPORT_SENTINEL}\nDo this locally`;
    expect(extractTeleportPlan(text)).toBe('Do this locally');
  });
});
