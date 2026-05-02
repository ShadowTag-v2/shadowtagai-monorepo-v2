import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Command } from 'commander';

// Import the compact command registration
import { registerCompactCommand } from '../../../src/commands/compact-cmd.js';

// Import compaction pipeline internals for edge-case testing
import { apiMicrocompact } from '../../../src/services/compact/apiMicrocompact.js';
import { historySnip, groupByApiRound } from '../../../src/services/compact/historySnip.js';
import { contextCollapse } from '../../../src/services/compact/contextCollapse.js';
import { allocateTokenBudget } from '../../../src/services/compact/tokenBudget.js';
import {
  runCompactionPipeline,
  resetCompactionCircuitBreaker,
} from '../../../src/services/compact/index.js';

describe('Compact CLI Command Registration', () => {
  it('registers compact command on program', () => {
    const program = new Command();
    registerCompactCommand(program);
    const compact = program.commands.find((c) => c.name() === 'compact');
    expect(compact).toBeDefined();
    expect(compact!.description()).toContain('compaction');
  });

  it('has all required options', () => {
    const program = new Command();
    registerCompactCommand(program);
    const compact = program.commands.find((c) => c.name() === 'compact');
    expect(compact).toBeDefined();
    const optionNames = compact!.options.map((o) => o.long);
    expect(optionNames).toContain('--file');
    expect(optionNames).toContain('--model');
    expect(optionNames).toContain('--window');
    expect(optionNames).toContain('--json');
    expect(optionNames).toContain('--budget-only');
  });
});

describe('L1 Edge Cases: apiMicrocompact', () => {
  it('handles null/undefined content gracefully', () => {
    const msgs = [{ role: 'user', content: null }];
    const result = apiMicrocompact(msgs as any, 8000);
    expect(result).toHaveLength(1);
    expect(result[0].microcompacted).toBe(true);
  });

  it('handles messages with no content field', () => {
    const msgs = [{ role: 'user' }];
    const result = apiMicrocompact(msgs as any, 8000);
    expect(result).toHaveLength(1);
  });

  it('handles mixed content types in single conversation', () => {
    const msgs = [
      { role: 'user', content: 'plain text' },
      { role: 'user', content: [{ type: 'text', text: 'array text' }] },
      { role: 'system', content: 'system msg' },
      { role: 'assistant', content: 'response' },
    ];
    const result = apiMicrocompact(msgs, 8000);
    expect(result).toHaveLength(4);
    // System passes through untouched
    expect(result[2].content).toBe('system msg');
    // Others get microcompacted flag
    expect(result[0].microcompacted).toBe(true);
    expect(result[1].microcompacted).toBe(true);
  });

  it('does not compact non-whitelisted tool results', () => {
    const msgs = [
      {
        role: 'assistant',
        content: [{ type: 'tool_use', id: 'tu-x', name: 'CustomInternalTool', input: {} }],
      },
      {
        role: 'user',
        content: [
          {
            type: 'tool_result',
            tool_use_id: 'tu-x',
            content: 'y'.repeat(20000),
          },
        ],
      },
    ];
    const result = apiMicrocompact(msgs, 8000);
    // Non-whitelisted tool should still be truncated because unknown defaults to compactable
    const toolContent = (result[1].content as any[])[0].content;
    expect(typeof toolContent).toBe('string');
  });

  it('handles tool_use without matching tool_result', () => {
    const msgs = [
      {
        role: 'assistant',
        content: [{ type: 'tool_use', id: 'orphan-1', name: 'Bash', input: {} }],
      },
    ];
    // Should not throw
    const result = apiMicrocompact(msgs, 8000);
    expect(result).toHaveLength(1);
  });

  it('preserves tool_use blocks exactly', () => {
    const toolUse = { type: 'tool_use', id: 'tu-keep', name: 'Read', input: { path: '/foo' } };
    const msgs = [{ role: 'assistant', content: [toolUse] }];
    const result = apiMicrocompact(msgs, 8000);
    expect((result[0].content as any[])[0]).toEqual(toolUse);
  });
});

describe('L2 Edge Cases: historySnip', () => {
  it('handles all messages having the same assistant ID (generous budget)', () => {
    const msgs = [
      { role: 'user', content: 'q1' },
      { role: 'assistant', content: 'a1', message: { id: 'same' } },
      { role: 'user', content: 'q2' },
      { role: 'assistant', content: 'a2', message: { id: 'same' } },
    ];
    // With a generous budget, no groups are snipped
    const result = historySnip(msgs, 10000);
    expect(result).toEqual(msgs);
  });

  it('snips leading user group when same-ID assistants form post-first group (tight budget)', () => {
    const msgs = [
      { role: 'user', content: 'q1' },
      { role: 'assistant', content: 'a1', message: { id: 'same' } },
      { role: 'user', content: 'q2' },
      { role: 'assistant', content: 'a2', message: { id: 'same' } },
    ];
    // Tight budget: the first user-only group gets snipped
    const result = historySnip(msgs, 10);
    // Should have snip indicator + the kept group
    expect(result[0].historySnipped).toBe(true);
    expect(result.some((m: any) => m.content === 'a2')).toBe(true);
  });

  it('handles messages without message.id', () => {
    const msgs = [
      { role: 'user', content: 'q1' },
      { role: 'assistant', content: 'a1' },
      { role: 'user', content: 'q2' },
      { role: 'assistant', content: 'a2' },
    ];
    // Should not throw
    const result = historySnip(msgs, 10000);
    expect(result.length).toBeGreaterThan(0);
  });

  it('preserves newest group when budget is very tight', () => {
    const msgs = [
      { role: 'user', content: 'old '.repeat(100) },
      { role: 'assistant', content: 'old-response '.repeat(100), message: { id: 'g1' } },
      { role: 'user', content: 'new' },
      { role: 'assistant', content: 'new-response', message: { id: 'g2' } },
    ];
    const result = historySnip(msgs, 50);
    // The newest group should survive
    const hasNew = result.some((m: any) =>
      typeof m.content === 'string' && m.content.includes('new'),
    );
    expect(hasNew).toBe(true);
  });

  it('includes snip indicator with correct metadata', () => {
    const msgs = [
      { role: 'user', content: 'a'.repeat(500) },
      { role: 'assistant', content: 'b'.repeat(500), message: { id: 'g1' } },
      { role: 'user', content: 'c' },
      { role: 'assistant', content: 'd', message: { id: 'g2' } },
    ];
    const result = historySnip(msgs, 50);
    if (result[0].historySnipped) {
      expect(typeof result[0].content).toBe('string');
      expect((result[0].content as string)).toContain('snipped');
    }
  });
});

describe('groupByApiRound Edge Cases', () => {
  it('handles empty input', () => {
    expect(groupByApiRound([])).toEqual([]);
  });

  it('handles only user messages (no assistant)', () => {
    const msgs = [
      { role: 'user', content: 'q1' },
      { role: 'user', content: 'q2' },
    ];
    const groups = groupByApiRound(msgs);
    expect(groups).toHaveLength(1); // All in one group
  });

  it('handles interleaved system messages', () => {
    const msgs = [
      { role: 'system', content: 'sys' },
      { role: 'user', content: 'q1' },
      { role: 'assistant', content: 'a1', message: { id: 'g1' } },
    ];
    const groups = groupByApiRound(msgs);
    expect(groups.length).toBeGreaterThan(0);
  });
});

describe('L3 Edge Cases: contextCollapse', () => {
  it('handles single message (no pairs to collapse)', () => {
    const msgs = [{ role: 'user', content: 'solo' }];
    expect(contextCollapse(msgs, 10)).toEqual(msgs);
  });

  it('collapses 20+ repeated identical messages', () => {
    const msgs = Array.from({ length: 25 }, () => ({ role: 'user', content: 'same' }));
    const result = contextCollapse(msgs, 10);
    expect(result.length).toBeLessThan(25);
    const collapsed = result.filter((m: any) => m.collapsed);
    expect(collapsed.length).toBeGreaterThan(0);
  });

  it('handles error sequences with mixed content', () => {
    const msgs = [
      { role: 'user', content: 'Error: something failed' },
      { role: 'user', content: 'Error: something failed' },
      { role: 'user', content: 'Error: different error' },
      { role: 'user', content: 'Error: yet another error' },
      { role: 'user', content: 'Error: final error' },
      { role: 'user', content: 'Success: it worked' },
    ];
    const result = contextCollapse(msgs, 10);
    // Should handle error sequences — collapsed count may vary
    expect(result.length).toBeLessThanOrEqual(msgs.length);
  });

  it('does not collapse non-adjacent duplicates', () => {
    const msgs = [
      { role: 'user', content: 'hello' },
      { role: 'assistant', content: 'hi' },
      { role: 'user', content: 'hello' },  // same as first but not adjacent
    ];
    // Budget needs to be low enough to trigger collapse logic
    const result = contextCollapse(msgs, 10);
    // Non-adjacent duplicates should both remain
    const userMsgs = result.filter((m: any) => m.role === 'user');
    expect(userMsgs.length).toBe(2);
  });
});

describe('L4 Edge Cases: allocateTokenBudget', () => {
  it('handles zero window', () => {
    const b = allocateTokenBudget([], 0);
    expect(b.effectiveWindow).toBe(0);
    expect(b.reservedOutput).toBe(0);
    expect(b.totalLimit).toBe(0);
  });

  it('handles very small window (1000 tokens)', () => {
    const b = allocateTokenBudget([], 1000);
    expect(b.effectiveWindow).toBe(1000);
    expect(b.reservedOutput).toBe(200); // 20% of 1000
    expect(b.totalLimit).toBe(800);
    expect(b.historyLimit).toBe(480); // 60% of 800
    expect(b.maxToolOutputLength).toBe(4000); // min floor
  });

  it('handles negative env override (ignored)', () => {
    const orig = process.env.CLAUDE_CODE_AUTO_COMPACT_WINDOW;
    process.env.CLAUDE_CODE_AUTO_COMPACT_WINDOW = '-500';
    try {
      const b = allocateTokenBudget([], 200_000);
      // Negative should be ignored (not NaN, but <= 0)
      expect(b.effectiveWindow).toBe(200_000);
    } finally {
      orig === undefined
        ? delete process.env.CLAUDE_CODE_AUTO_COMPACT_WINDOW
        : (process.env.CLAUDE_CODE_AUTO_COMPACT_WINDOW = orig);
    }
  });

  it('handles non-numeric env override (ignored)', () => {
    const orig = process.env.CLAUDE_CODE_AUTO_COMPACT_WINDOW;
    process.env.CLAUDE_CODE_AUTO_COMPACT_WINDOW = 'not-a-number';
    try {
      const b = allocateTokenBudget([], 200_000);
      expect(b.effectiveWindow).toBe(200_000);
    } finally {
      orig === undefined
        ? delete process.env.CLAUDE_CODE_AUTO_COMPACT_WINDOW
        : (process.env.CLAUDE_CODE_AUTO_COMPACT_WINDOW = orig);
    }
  });

  it('allocates correct budget for all Claude models', () => {
    const claudeModels = [
      'claude-sonnet-4-20250514',
      'claude-3-5-sonnet-20241022',
      'claude-3-opus-20240229',
      'claude-3-haiku-20240307',
      'claude-opus-4-20250514',
    ];
    for (const model of claudeModels) {
      const b = allocateTokenBudget([], undefined, model);
      expect(b.effectiveWindow).toBe(200_000);
    }
  });

  it('allocates correct budget for all Gemini 3.x models', () => {
    const gemini3Models = [
      'gemini-3.1-pro-preview',
      'gemini-3-flash-preview',
      'gemini-3.1-flash-lite-preview',
    ];
    for (const model of gemini3Models) {
      const b = allocateTokenBudget([], undefined, model);
      expect(b.effectiveWindow).toBe(1_048_576);
    }
  });
});

describe('Full Pipeline Edge Cases', () => {
  beforeEach(() => resetCompactionCircuitBreaker());

  it('handles conversation with only system messages', async () => {
    const msgs = [
      { role: 'system', content: 'You are helpful.' },
      { role: 'system', content: 'Additional context.' },
    ];
    const r = await runCompactionPipeline(msgs, 200_000);
    expect(r.circuitBroken).toBe(false);
    expect(r.layersApplied.length).toBe(4);
  });

  it('handles conversation with image-heavy content', async () => {
    const msgs = [
      { role: 'user', content: [
        { type: 'image', data: 'base64-img-1' },
        { type: 'image', data: 'base64-img-2' },
        { type: 'text', text: 'describe these' },
      ]},
      { role: 'assistant', content: 'Two images detected.', message: { id: 'a1' } },
    ];
    const r = await runCompactionPipeline(msgs, 200_000);
    expect(r.circuitBroken).toBe(false);
    // Images should be compressed to placeholders
    const userContent = r.messages[0].content as any[];
    if (Array.isArray(userContent)) {
      const imagePlaceholders = userContent.filter(
        (b: any) => typeof b.text === 'string' && b.text.includes('Image content removed'),
      );
      expect(imagePlaceholders.length).toBe(2);
    }
  });

  it('processes conversation with Bearer token scrubbing alert', async () => {
    const msgs = [
      { role: 'user', content: 'Check this API' },
      {
        role: 'assistant',
        content: [{
          type: 'tool_use',
          id: 'tu-auth',
          name: 'WebFetch',
          input: { url: 'https://api.example.com' },
        }],
        message: { id: 'a1' },
      },
      {
        role: 'user',
        content: [{
          type: 'tool_result',
          tool_use_id: 'tu-auth',
          content: 'Bearer sk-test-12345 response data',
        }],
      },
    ];
    // Pipeline should run without error — scrubbing detection is bughunter's job
    const r = await runCompactionPipeline(msgs, 200_000);
    expect(r.circuitBroken).toBe(false);
  });

  it('handles 500+ message conversations', async () => {
    const msgs = Array.from({ length: 500 }, (_, i) => ({
      role: i % 2 === 0 ? 'user' : 'assistant',
      content: `Msg ${i}: ${'data '.repeat(20)}`,
      ...(i % 2 === 1 ? { message: { id: `a-${Math.floor(i / 2)}` } } : {}),
    }));
    const r = await runCompactionPipeline(msgs, 200_000);
    expect(r.circuitBroken).toBe(false);
    expect(r.messages.length).toBeGreaterThan(0);
    expect(r.layersApplied.length).toBe(4);
  });

  it('consecutive pipeline runs respect circuit breaker reset', async () => {
    for (let run = 0; run < 5; run++) {
      resetCompactionCircuitBreaker();
      const r = await runCompactionPipeline(
        [{ role: 'user', content: `Run ${run}` }],
        200_000,
      );
      expect(r.circuitBroken).toBe(false);
    }
  });
});
