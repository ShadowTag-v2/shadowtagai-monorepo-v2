/**
 * compact-e2e.test.ts — End-to-End CLI Integration Tests
 *
 * Exercises the full compact command lifecycle through Commander,
 * using the real fixture file and validating output format, flags,
 * and telemetry side-effects.
 */

import { mkdtempSync, readFileSync, writeFileSync, unlinkSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { Command } from 'commander';
import { registerCompactCommand } from '../../../src/commands/compact-cmd.js';

// Mock analytics to avoid side-effects in tests
vi.mock('../../../src/services/analytics/index.js', () => ({
  logEvent: vi.fn(),
}));

const FIXTURE_PATH = join(__dirname, '../../fixtures/conversation.json');

/** Create a Commander program with compact registered and run it */
async function runCompactCli(args: string[]): Promise<{ exitCode: number | undefined; output: string }> {
  const program = new Command();
  program.exitOverride(); // Throw instead of process.exit
  registerCompactCommand(program);

  const chunks: string[] = [];
  const origLog = console.log;
  const origError = console.error;
  console.log = (...logArgs: unknown[]) => chunks.push(logArgs.map(String).join(' '));
  console.error = (...errArgs: unknown[]) => chunks.push(`[ERROR] ${errArgs.map(String).join(' ')}`);

  process.exitCode = undefined; // Clean slate before each CLI run
  let exitCode: number | undefined;
  try {
    await program.parseAsync(['node', 'agnt', ...args]);
    exitCode = process.exitCode ?? 0;
  } catch (e: unknown) {
    if (e instanceof Error && 'exitCode' in e) {
      exitCode = (e as { exitCode: number }).exitCode;
    } else {
      exitCode = 1;
    }
  } finally {
    console.log = origLog;
    console.error = origError;
    process.exitCode = undefined; // Reset
  }

  return { exitCode, output: chunks.join('\n') };
}

describe('compact CLI — E2E integration', () => {
  beforeEach(() => {
    process.exitCode = undefined;
  });

  afterEach(() => {
    process.exitCode = undefined;
  });

  it('should compact a fixture file with default options', async () => {
    const { exitCode, output } = await runCompactCli(['compact', '--file', FIXTURE_PATH]);
    expect(exitCode).toBe(0);
    expect(output).toContain('COMPACTION — 4-Layer Context Pipeline');
    expect(output).toContain('Token Budget Breakdown');
    expect(output).toContain('Layer Execution:');
    expect(output).toContain('tokenBudget');
    expect(output).toContain('apiMicrocompact');
    expect(output).toContain('Compaction complete in');
  });

  it('should output JSON when --json flag is used', async () => {
    const { exitCode, output } = await runCompactCli(['compact', '--file', FIXTURE_PATH, '--json']);
    expect(exitCode).toBe(0);
    // The JSON output starts after the header
    const jsonStart = output.indexOf('{');
    expect(jsonStart).toBeGreaterThan(-1);
    const parsed = JSON.parse(output.slice(jsonStart));
    expect(parsed).toHaveProperty('inputMessages');
    expect(parsed).toHaveProperty('outputMessages');
    expect(parsed).toHaveProperty('layersApplied');
    expect(parsed).toHaveProperty('layerTimings');
    expect(parsed).toHaveProperty('reductionPct');
    expect(parsed.layersApplied).toContain('tokenBudget');
    expect(parsed.layersApplied).toContain('apiMicrocompact');
  });

  it('should show verbose per-layer timing', async () => {
    const { exitCode, output } = await runCompactCli([
      'compact',
      '--file',
      FIXTURE_PATH,
      '--verbose',
    ]);
    expect(exitCode).toBe(0);
    expect(output).toContain('Per-Layer Timing');
    expect(output).toContain('ms');
  });

  it('should support dry-run mode', async () => {
    const { exitCode, output } = await runCompactCli([
      'compact',
      '--file',
      FIXTURE_PATH,
      '--dry-run',
    ]);
    expect(exitCode).toBe(0);
    expect(output).toContain('DRY RUN');
    expect(output).toContain('Compaction Diff Summary');
    expect(output).toContain('Input messages:');
    expect(output).toContain('Output messages:');
    expect(output).toContain('Char reduction:');
  });

  it('should show budget-only without a file', async () => {
    const { exitCode, output } = await runCompactCli([
      'compact',
      '--budget-only',
      '--model',
      'gemini-2.5-pro',
    ]);
    expect(exitCode).toBe(0);
    expect(output).toContain('Token Budget Breakdown');
    expect(output).toContain('Effective Window');
  });

  it('should write compacted output to --output path', async () => {
    const tmpDir = mkdtempSync(join(tmpdir(), 'compact-e2e-'));
    const outputPath = join(tmpDir, 'compacted.json');

    const { exitCode } = await runCompactCli([
      'compact',
      '--file',
      FIXTURE_PATH,
      '--output',
      outputPath,
    ]);
    expect(exitCode).toBe(0);

    const written = readFileSync(outputPath, 'utf-8');
    const parsed = JSON.parse(written);
    expect(Array.isArray(parsed)).toBe(true);
    expect(parsed.length).toBeGreaterThan(0);

    // Cleanup
    unlinkSync(outputPath);
  });

  it('should pass threshold gate when reduction is above target', async () => {
    // Fixture can expand during compaction (image placeholders, whitespace normalization),
    // so use a large negative threshold that any run will exceed
    const { exitCode, output } = await runCompactCli([
      'compact',
      '--file',
      FIXTURE_PATH,
      '--threshold',
      '-100',
    ]);
    expect(exitCode).toBe(0);
    expect(output).toContain('THRESHOLD PASS');
  });

  it('should fail threshold gate when reduction is below target', async () => {
    // 99% threshold should fail on a small fixture
    const { exitCode, output } = await runCompactCli([
      'compact',
      '--file',
      FIXTURE_PATH,
      '--threshold',
      '99',
    ]);
    expect(exitCode).toBe(1);
    expect(output).toContain('THRESHOLD FAIL');
  });

  it('should fail gracefully when no file is provided', async () => {
    const { exitCode } = await runCompactCli(['compact']);
    expect(exitCode).toBe(1);
  });

  it('should handle custom window size', async () => {
    const { exitCode, output } = await runCompactCli([
      'compact',
      '--file',
      FIXTURE_PATH,
      '--window',
      '50000',
    ]);
    expect(exitCode).toBe(0);
    expect(output).toContain('Token Budget Breakdown');
  });

  it('should combine --verbose --json flags', async () => {
    const { exitCode, output } = await runCompactCli([
      'compact',
      '--file',
      FIXTURE_PATH,
      '--json',
      '--verbose',
    ]);
    expect(exitCode).toBe(0);
    const jsonStart = output.indexOf('{');
    const parsed = JSON.parse(output.slice(jsonStart));
    expect(parsed.layerTimings).toBeDefined();
    expect(typeof parsed.layerTimings.tokenBudget).toBe('number');
  });
});
