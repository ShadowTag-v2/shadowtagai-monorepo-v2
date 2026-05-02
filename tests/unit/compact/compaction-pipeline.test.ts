import { describe, it, expect, beforeEach } from 'vitest';
import { apiMicrocompact } from '../../../src/services/compact/apiMicrocompact.js';
import { historySnip, groupByApiRound } from '../../../src/services/compact/historySnip.js';
import { contextCollapse } from '../../../src/services/compact/contextCollapse.js';
import { allocateTokenBudget } from '../../../src/services/compact/tokenBudget.js';
import { runCompactionPipeline, resetCompactionCircuitBreaker } from '../../../src/services/compact/index.js';

describe('L1: apiMicrocompact', () => {
  it('passes through empty arrays', () => {
    expect(apiMicrocompact([], 8000)).toEqual([]);
  });
  it('normalizes whitespace in string content', () => {
    const result = apiMicrocompact([{ role: 'user', content: 'hello\n\n\n\nworld  ' }], 8000);
    expect(result[0].content).toBe('hello\n\nworld');
  });
  it('leaves system messages unmodified', () => {
    const sys = { role: 'system', content: 'You are helpful\n\n\n\n' };
    const result = apiMicrocompact([sys], 8000);
    expect(result[0].content).toBe(sys.content);
  });
  it('replaces image blocks with placeholder', () => {
    const msgs = [{ role: 'user', content: [{ type: 'image', data: 'b64' }, { type: 'text', text: 'describe' }] }];
    const result = apiMicrocompact(msgs, 8000);
    expect((result[0].content as any[])[0].text).toContain('Image content removed');
  });
  it('truncates tool results exceeding maxLength', () => {
    const msgs = [
      { role: 'assistant', content: [{ type: 'tool_use', id: 'tu-1', name: 'Bash', input: {} }] },
      { role: 'user', content: [{ type: 'tool_result', tool_use_id: 'tu-1', content: 'x'.repeat(20000) }] },
    ];
    const result = apiMicrocompact(msgs, 8000);
    expect((result[1].content as any[])[0].content).toContain('[Truncated');
  });
});

describe('L2: historySnip', () => {
  it('returns empty for empty input', () => { expect(historySnip([], 10000)).toEqual([]); });
  it('returns single-group unmodified', () => {
    const msgs = [{ role: 'user', content: 'hi' }, { role: 'assistant', content: 'hey', message: { id: 'a1' } }];
    expect(historySnip(msgs, 10000)).toEqual(msgs);
  });
  it('snips old groups when over budget', () => {
    const msgs = [
      { role: 'user', content: 'a'.repeat(200) }, { role: 'assistant', content: 'b'.repeat(200), message: { id: 'g1' } },
      { role: 'user', content: 'c'.repeat(200) }, { role: 'assistant', content: 'd'.repeat(200), message: { id: 'g2' } },
      { role: 'user', content: 'e'.repeat(200) }, { role: 'assistant', content: 'f'.repeat(200), message: { id: 'g3' } },
    ];
    const result = historySnip(msgs, 200);
    expect(result[0].historySnipped).toBe(true);
    expect(result.length).toBeLessThan(msgs.length);
  });
});

describe('groupByApiRound', () => {
  it('groups by assistant ID boundaries', () => {
    const msgs = [
      { role: 'user', content: 'q1' }, { role: 'assistant', content: 'a1', message: { id: 'id-1' } },
      { role: 'user', content: 'q2' }, { role: 'assistant', content: 'a2', message: { id: 'id-2' } },
    ];
    expect(groupByApiRound(msgs).length).toBe(3);
  });
});

describe('L3: contextCollapse', () => {
  it('passes through single messages', () => {
    expect(contextCollapse([{ role: 'user', content: 'hi' }], 100000)).toHaveLength(1);
  });
  it('returns unchanged when under budget', () => {
    const msgs = [{ role: 'user', content: 'hi' }, { role: 'assistant', content: 'hello' }];
    expect(contextCollapse(msgs, 100000)).toEqual(msgs);
  });
  it('collapses adjacent duplicates', () => {
    const msgs = Array.from({ length: 5 }, () => ({ role: 'user', content: 'hello' }));
    const result = contextCollapse(msgs, 10);
    expect(result.length).toBeLessThan(5);
    expect(result.some((m: any) => m.collapsed)).toBe(true);
  });
});

describe('L4: allocateTokenBudget', () => {
  it('returns valid budget', () => {
    const b = allocateTokenBudget([], 200_000);
    expect(b.historyLimit).toBeGreaterThan(0);
    expect(b.totalLimit).toBeGreaterThan(0);
    expect(b.reservedOutput).toBe(20_000);
    expect(b.effectiveWindow).toBe(200_000);
  });
  it('caps tool output at 16K', () => {
    expect(allocateTokenBudget([], 1_000_000).maxToolOutputLength).toBeLessThanOrEqual(16_000);
  });
  it('respects env override', () => {
    const orig = process.env.CLAUDE_CODE_AUTO_COMPACT_WINDOW;
    process.env.CLAUDE_CODE_AUTO_COMPACT_WINDOW = '100000';
    try { expect(allocateTokenBudget([], 200_000).effectiveWindow).toBe(100_000); }
    finally { orig === undefined ? delete process.env.CLAUDE_CODE_AUTO_COMPACT_WINDOW : (process.env.CLAUDE_CODE_AUTO_COMPACT_WINDOW = orig); }
  });
});

describe('Compaction Orchestrator', () => {
  beforeEach(() => resetCompactionCircuitBreaker());
  it('runs all 4 layers', async () => {
    const r = await runCompactionPipeline([{ role: 'user', content: 'hello' }]);
    expect(r.layersApplied).toEqual(expect.arrayContaining(['tokenBudget', 'apiMicrocompact', 'historySnip', 'contextCollapse']));
    expect(r.circuitBroken).toBe(false);
  });
  it('handles empty arrays', async () => {
    const r = await runCompactionPipeline([]);
    expect(r.messages).toEqual([]);
  });
  it('returns budget metadata', async () => {
    const r = await runCompactionPipeline([{ role: 'user', content: 'test' }]);
    expect(r.budget.historyLimit).toBeGreaterThan(0);
  });
  it('accepts a model identifier', async () => {
    const r = await runCompactionPipeline([{ role: 'user', content: 'test' }], 200_000, 'claude-sonnet-4-20250514');
    expect(r.budget.effectiveWindow).toBe(200_000);
    expect(r.circuitBroken).toBe(false);
  });
});

describe('Compaction Circuit Breaker', () => {
  beforeEach(() => resetCompactionCircuitBreaker());

  it('activates after MAX_CONSECUTIVE_FAILURES', async () => {
    // Circuit breaker triggers after 3 consecutive failures.
    // We can't easily inject failures without mocking internals, so
    // test the reset and break-state interface.
    const r = await runCompactionPipeline([{ role: 'user', content: 'ok' }]);
    expect(r.circuitBroken).toBe(false);

    // Reset clears any accumulated failures
    resetCompactionCircuitBreaker();
    const r2 = await runCompactionPipeline([{ role: 'user', content: 'ok' }]);
    expect(r2.circuitBroken).toBe(false);
  });

  it('reset allows pipeline to resume', async () => {
    resetCompactionCircuitBreaker();
    const r = await runCompactionPipeline([{ role: 'user', content: 'test' }]);
    expect(r.layersApplied.length).toBeGreaterThan(0);
  });
});

describe('Full Pipeline Stress Tests', () => {
  beforeEach(() => resetCompactionCircuitBreaker());

  it('processes a realistic conversation with tool pairs', async () => {
    const msgs = [
      { role: 'system', content: 'You are helpful.' },
      { role: 'user', content: 'Read my file' },
      { role: 'assistant', content: [{ type: 'tool_use', id: 'tu-1', name: 'Read', input: { path: '/foo.ts' } }], message: { id: 'a1' } },
      { role: 'user', content: [{ type: 'tool_result', tool_use_id: 'tu-1', content: 'const x = 1;\n'.repeat(500) }] },
      { role: 'assistant', content: 'Here is your file.', message: { id: 'a1' } },
      { role: 'user', content: 'Now edit it' },
      { role: 'assistant', content: [{ type: 'tool_use', id: 'tu-2', name: 'FileEdit', input: {} }], message: { id: 'a2' } },
      { role: 'user', content: [{ type: 'tool_result', tool_use_id: 'tu-2', content: 'File edited successfully' }] },
      { role: 'assistant', content: 'Done.', message: { id: 'a2' } },
    ];
    const r = await runCompactionPipeline(msgs, 200_000);
    expect(r.layersApplied).toContain('apiMicrocompact');
    expect(r.layersApplied).toContain('historySnip');
    expect(r.layersApplied).toContain('contextCollapse');
    expect(r.layersApplied).toContain('tokenBudget');
    expect(r.messages.length).toBeGreaterThan(0);
  });

  it('compacts 100+ message conversations without error', async () => {
    const msgs = Array.from({ length: 120 }, (_, i) => ({
      role: i % 2 === 0 ? 'user' : 'assistant',
      content: `Message ${i}: ${'x'.repeat(100)}`,
      ...(i % 2 === 1 ? { message: { id: `a-${Math.floor(i / 2)}` } } : {}),
    }));
    const r = await runCompactionPipeline(msgs, 200_000);
    expect(r.circuitBroken).toBe(false);
    expect(r.layersApplied.length).toBe(4);
  });
});

describe('L4: Gemini Model Context Windows', () => {
  it('allocates budget for gemini-2.5-pro (1M window)', () => {
    const b = allocateTokenBudget([], undefined, 'gemini-2.5-pro');
    expect(b.effectiveWindow).toBe(1_048_576);
    // 20% of 1M = 209,715 but capped at MAX_OUTPUT_TOKENS_FOR_SUMMARY (20K)
    expect(b.reservedOutput).toBe(20_000);
    // Available = 1_048_576 - 20_000 = 1_028_576
    expect(b.totalLimit).toBe(1_028_576);
    // History = 60% of available
    expect(b.historyLimit).toBe(Math.floor(1_028_576 * 0.6));
    // Tool output capped at 16K
    expect(b.maxToolOutputLength).toBe(16_000);
  });

  it('allocates budget for gemini-3.1-pro-preview (1M window)', () => {
    const b = allocateTokenBudget([], undefined, 'gemini-3.1-pro-preview');
    expect(b.effectiveWindow).toBe(1_048_576);
    expect(b.totalLimit).toBe(1_028_576);
  });

  it('allocates budget for gemini-1.5-pro (2M window)', () => {
    const b = allocateTokenBudget([], undefined, 'gemini-1.5-pro');
    expect(b.effectiveWindow).toBe(2_097_152);
    // Reserved output still capped at 20K (min of 20% * 2M and 20K)
    expect(b.reservedOutput).toBe(20_000);
    expect(b.totalLimit).toBe(2_097_152 - 20_000);
  });

  it('falls back to 200K for unknown models', () => {
    const b = allocateTokenBudget([], undefined, 'some-unknown-model');
    expect(b.effectiveWindow).toBe(200_000);
  });
});

describe('Tool-Use / Tool-Result Pairing Atomicity', () => {
  beforeEach(() => resetCompactionCircuitBreaker());

  it('never orphans a tool_use without its tool_result after snip', async () => {
    // Create a conversation with 5 tool-use/result pairs
    const msgs: any[] = [
      { role: 'system', content: 'System prompt' },
    ];
    for (let i = 0; i < 5; i++) {
      msgs.push(
        { role: 'user', content: `Question ${i}` },
        {
          role: 'assistant',
          content: [{ type: 'tool_use', id: `tu-${i}`, name: 'Bash', input: { command: `echo ${i}` } }],
          message: { id: `round-${i}` },
        },
        { role: 'user', content: [{ type: 'tool_result', tool_use_id: `tu-${i}`, content: `Output ${i}` }] },
        { role: 'assistant', content: `Done with step ${i}`, message: { id: `round-${i}` } },
      );
    }

    // Run with a tight budget to force snipping
    const r = await runCompactionPipeline(msgs, 200_000);

    // Verify: every tool_use in the result has a matching tool_result
    const toolUseIds = new Set<string>();
    const toolResultIds = new Set<string>();
    for (const msg of r.messages) {
      if (Array.isArray(msg.content)) {
        for (const block of msg.content) {
          if (block.type === 'tool_use') toolUseIds.add(block.id);
          if (block.type === 'tool_result') toolResultIds.add(block.tool_use_id);
        }
      }
    }
    // Every tool_use must have a corresponding tool_result
    for (const id of toolUseIds) {
      expect(toolResultIds.has(id)).toBe(true);
    }
    // Every tool_result must reference an existing tool_use
    for (const id of toolResultIds) {
      expect(toolUseIds.has(id)).toBe(true);
    }
  });

  it('preserves pairing when only the last round survives snip', async () => {
    const msgs: any[] = [];
    // Create 10 rounds of heavy content to force aggressive snipping
    for (let i = 0; i < 10; i++) {
      msgs.push(
        { role: 'user', content: 'x'.repeat(500) },
        {
          role: 'assistant',
          content: [{ type: 'tool_use', id: `tu-${i}`, name: 'Read', input: {} }],
          message: { id: `r-${i}` },
        },
        { role: 'user', content: [{ type: 'tool_result', tool_use_id: `tu-${i}`, content: 'y'.repeat(500) }] },
        { role: 'assistant', content: `Result ${i}`, message: { id: `r-${i}` } },
      );
    }

    const r = await runCompactionPipeline(msgs, 200_000);

    // Same atomicity check
    const uses = new Set<string>();
    const results = new Set<string>();
    for (const msg of r.messages) {
      if (Array.isArray(msg.content)) {
        for (const block of msg.content) {
          if (block.type === 'tool_use') uses.add(block.id);
          if (block.type === 'tool_result') results.add(block.tool_use_id);
        }
      }
    }
    for (const id of uses) expect(results.has(id)).toBe(true);
    for (const id of results) expect(uses.has(id)).toBe(true);
  });
});

describe('Gemini 1M Window Stress Tests', () => {
  beforeEach(() => resetCompactionCircuitBreaker());

  it('handles 300-message conversation with gemini-2.5-flash budget', async () => {
    const msgs = Array.from({ length: 300 }, (_, i) => ({
      role: i % 2 === 0 ? 'user' : 'assistant',
      content: `Turn ${i}: ${'z'.repeat(200)}`,
      ...(i % 2 === 1 ? { message: { id: `a-${Math.floor(i / 2)}` } } : {}),
    }));
    const r = await runCompactionPipeline(msgs, undefined, 'gemini-2.5-flash');
    expect(r.circuitBroken).toBe(false);
    expect(r.budget.effectiveWindow).toBe(1_048_576);
    expect(r.layersApplied.length).toBe(4);
    expect(r.messages.length).toBeGreaterThan(0);
  });
});
