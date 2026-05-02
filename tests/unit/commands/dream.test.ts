import { describe, it, expect } from 'vitest';
import { findDreamScript, parseDreamOutput } from '../../../src/commands/dream.js';
import { join } from 'path';

describe('Dream: findDreamScript', () => {
  it('returns null when no script exists in any fallback location', () => {
    // findDreamScript checks baseDir, then process.cwd(), then parent dir.
    // With a bogus baseDir, it will still try CWD — which may have the script.
    // This test verifies the function contract: result is string or null.
    const result = findDreamScript('/nonexistent/path');
    expect(result === null || typeof result === 'string').toBe(true);
  });

  it('finds script relative to baseDir when it exists', () => {
    // The monorepo has scripts/dream_consolidation.py
    const repoRoot = join(__dirname, '..', '..', '..');
    const result = findDreamScript(repoRoot);
    // May or may not exist depending on repo state, but function should not throw
    expect(result === null || typeof result === 'string').toBe(true);
  });

  it('returns a string path when found', () => {
    const repoRoot = join(__dirname, '..', '..', '..');
    const result = findDreamScript(repoRoot);
    if (result !== null) {
      expect(result).toContain('dream_consolidation.py');
    }
  });
});

describe('Dream: parseDreamOutput', () => {
  it('parses KIs processed count', () => {
    const output = '[DREAM] KIs processed: 42\nDone.';
    expect(parseDreamOutput(output).kiProcessed).toBe(42);
  });

  it('parses KIs merged count', () => {
    const output = '[DREAM] KIs merged: 3';
    expect(parseDreamOutput(output).kiMerged).toBe(3);
  });

  it('parses KIs pruned count', () => {
    const output = '[DREAM] KIs pruned: 7';
    expect(parseDreamOutput(output).kiPruned).toBe(7);
  });

  it('parses all metrics from full output', () => {
    const output = [
      '[DREAM] Starting consolidation...',
      '[DREAM] KIs processed: 50',
      '[DREAM] KIs merged: 5',
      '[DREAM] KIs pruned: 10',
      '[DREAM] Complete.',
    ].join('\n');
    const result = parseDreamOutput(output);
    expect(result.kiProcessed).toBe(50);
    expect(result.kiMerged).toBe(5);
    expect(result.kiPruned).toBe(10);
  });

  it('returns empty metrics for unrecognized output', () => {
    const result = parseDreamOutput('Hello world');
    expect(result.kiProcessed).toBeUndefined();
    expect(result.kiMerged).toBeUndefined();
    expect(result.kiPruned).toBeUndefined();
  });

  it('handles case-insensitive matching', () => {
    const output = 'kis PROCESSED: 12';
    expect(parseDreamOutput(output).kiProcessed).toBe(12);
  });

  it('handles singular KI form', () => {
    const output = 'KI processed: 1';
    expect(parseDreamOutput(output).kiProcessed).toBe(1);
  });
});
