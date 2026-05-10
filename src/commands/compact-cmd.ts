import { readFileSync, writeFileSync } from 'node:fs';
import type { Command } from 'commander';
import { logEvent } from '../services/analytics/index.js';
import {
  type CompactionPipelineResult,
  resetCompactionCircuitBreaker,
  runCompactionPipeline,
} from '../services/compact/index.js';

/**
 * Compact CLI Command — Terminal-side 4-Layer Context Compaction
 *
 * Exposes the production compaction pipeline as a CLI tool for diagnostics:
 *   - Read a JSON conversation file and compact it
 *   - Display budget allocation breakdown
 *   - Report layer-by-layer compaction metrics
 *   - Dry-run mode for analysis without side effects
 *   - Write compacted output to disk
 *   - Threshold gate for CI pipeline enforcement
 *
 * Usage:
 *   agnt compact --file conversation.json --model gemini-2.5-pro
 *   agnt compact --file conv.json --window 200000 --json
 *   agnt compact --file conv.json --output compacted.json
 *   agnt compact --file conv.json --threshold 10
 *   agnt compact --budget-only --model claude-sonnet-4-20250514
 */

export interface CompactCommandOptions {
  file?: string;
  model?: string;
  window?: string;
  json?: boolean;
  budgetOnly?: boolean;
  dryRun?: boolean;
  verbose?: boolean;
  output?: string;
  threshold?: string;
  force?: boolean;
}

function formatBudget(budget: Record<string, number>): string {
  const lines: string[] = [];
  lines.push('┌──────────────────────────────────────────────────┐');
  lines.push('│        COMPACTION — Token Budget Breakdown       │');
  lines.push('├──────────────────────────────────────────────────┤');
  lines.push(
    `│ Effective Window:    ${budget.effectiveWindow?.toLocaleString().padStart(12)} tokens`,
  );
  lines.push(
    `│ Reserved Output:     ${budget.reservedOutput?.toLocaleString().padStart(12)} tokens`,
  );
  lines.push(`│ Total Available:     ${budget.totalLimit?.toLocaleString().padStart(12)} tokens`);
  lines.push(`│ History Limit:       ${budget.historyLimit?.toLocaleString().padStart(12)} tokens`);
  lines.push(
    `│ Max Tool Output:     ${budget.maxToolOutputLength?.toLocaleString().padStart(12)} chars`,
  );
  lines.push('└──────────────────────────────────────────────────┘');
  return lines.join('\n');
}

/** Compute char-level reduction percentage */
function computeReductionPct(
  inputMessages: Record<string, unknown>[],
  outputMessages: Record<string, unknown>[],
): number {
  const inputChars = JSON.stringify(inputMessages).length;
  const outputChars = JSON.stringify(outputMessages).length;
  if (inputChars === 0) return 0;
  return ((inputChars - outputChars) / inputChars) * 100;
}

/** Handle --budget-only mode: show allocation and exit */
async function handleBudgetOnly(opts: CompactCommandOptions, totalWindow?: number): Promise<void> {
  const { allocateTokenBudget } = await import('../services/compact/tokenBudget.js');
  const budget = allocateTokenBudget([], totalWindow, opts.model);

  if (opts.json) {
    console.log(JSON.stringify(budget, null, 2));
  } else {
    console.log(`Model: ${opts.model ?? '(default 200K)'}`);
    console.log();
    console.log(formatBudget(budget as unknown as Record<string, number>));
  }
}

/** Handle --dry-run mode: analyze compaction without writing output */
function handleDryRun(
  messages: Record<string, unknown>[],
  result: CompactionPipelineResult,
  durationMs: number,
): void {
  const removed = messages.length - result.messages.length;
  const pct = computeReductionPct(messages, result.messages);

  console.log(formatBudget(result.budget as unknown as Record<string, number>));
  console.log();
  console.log('── DRY RUN — Compaction Diff Summary ──');
  console.log(`  Input messages:    ${messages.length}`);
  console.log(`  Output messages:   ${result.messages.length}`);
  console.log(`  Messages removed:  ${removed}`);
  console.log(`  Char reduction:    ${pct.toFixed(1)}%`);
  if (result.circuitBroken) {
    console.log('  ⚠ Circuit breaker activated — compaction halted.');
  }
  console.log(`\n✓ Dry-run analysis complete in ${durationMs}ms`);

  logEvent('tengu_compact_dry_run', {
    inputMessages: messages.length,
    outputMessages: result.messages.length,
    durationMs,
    reductionPct: pct,
  });
}

/** Output compaction result as JSON */
function outputJsonResult(
  messages: Record<string, unknown>[],
  result: CompactionPipelineResult,
  durationMs: number,
): void {
  console.log(
    JSON.stringify(
      {
        inputMessages: messages.length,
        outputMessages: result.messages.length,
        reduction: messages.length - result.messages.length,
        reductionPct: computeReductionPct(messages, result.messages),
        layersApplied: result.layersApplied,
        circuitBroken: result.circuitBroken,
        budget: result.budget,
        layerTimings: result.layerTimings,
        durationMs,
      },
      null,
      2,
    ),
  );
}

/** Output compaction result as human-readable table */
function outputHumanResult(
  messages: Record<string, unknown>[],
  result: CompactionPipelineResult,
  opts: CompactCommandOptions,
  durationMs: number,
): void {
  console.log(formatBudget(result.budget as unknown as Record<string, number>));
  console.log();

  // Verbose: show per-layer timing breakdown
  if (opts.verbose && result.layerTimings) {
    console.log('── Per-Layer Timing ──');
    for (const [layer, ms] of Object.entries(result.layerTimings)) {
      console.log(`  ${layer.padEnd(22)} ${ms.toFixed(2)}ms`);
    }
    console.log();
  }

  console.log('Layer Execution:');
  for (const layer of result.layersApplied) {
    const timing =
      opts.verbose && result.layerTimings?.[layer]
        ? ` (${result.layerTimings[layer].toFixed(2)}ms)`
        : '';
    console.log(`  ✓ ${layer}${timing}`);
  }
  console.log();
  console.log(`Input:  ${messages.length} messages`);
  console.log(`Output: ${result.messages.length} messages`);
  console.log(`Reduction: ${messages.length - result.messages.length} messages removed`);
  if (result.circuitBroken) {
    console.log('⚠ Circuit breaker activated — compaction halted.');
  }
  console.log(`\n✓ Compaction complete in ${durationMs}ms`);
}

/** Write compacted output to disk */
function writeOutput(outputPath: string, result: CompactionPipelineResult): void {
  writeFileSync(outputPath, JSON.stringify(result.messages, null, 2), 'utf-8');
  console.log(`\n📁 Compacted output written to: ${outputPath}`);
}

/** Enforce --threshold gate: fail if reduction % is below target */
function enforceThreshold(
  messages: Record<string, unknown>[],
  result: CompactionPipelineResult,
  thresholdPct: number,
): boolean {
  const actualPct = computeReductionPct(messages, result.messages);
  if (actualPct < thresholdPct) {
    console.log(
      `\n✗ THRESHOLD FAIL — reduction ${actualPct.toFixed(1)}% < required ${thresholdPct}%`,
    );
    logEvent('tengu_compact_threshold_fail', {
      actualPct,
      thresholdPct,
    });
    return false;
  }
  console.log(`\n✓ THRESHOLD PASS — reduction ${actualPct.toFixed(1)}% ≥ ${thresholdPct}%`);
  return true;
}

/** Emit final telemetry event with layer timings */
function emitCompletionTelemetry(
  messages: Record<string, unknown>[],
  result: CompactionPipelineResult,
  durationMs: number,
): void {
  logEvent('tengu_compact_complete', {
    inputMessages: messages.length,
    outputMessages: result.messages.length,
    durationMs,
    reductionPct: computeReductionPct(messages, result.messages),
    circuitBroken: result.circuitBroken,
    l1_ms: result.layerTimings?.apiMicrocompact,
    l2_ms: result.layerTimings?.historySnip,
    l3_ms: result.layerTimings?.contextCollapse,
    l4_ms: result.layerTimings?.tokenBudget,
  });
}

/** Full compaction lifecycle: read → pipeline → output → threshold → telemetry */
async function handleFullCompaction(
  opts: CompactCommandOptions,
  totalWindow?: number,
): Promise<void> {
  if (!opts.file) {
    process.exitCode = 1;
    return;
  }

  const raw = readFileSync(opts.file, 'utf-8');
  const messages: Record<string, unknown>[] = JSON.parse(raw);

  if (!Array.isArray(messages)) {
    process.exitCode = 1;
    return;
  }

  const t0 = performance.now();
  const result = await runCompactionPipeline(messages, totalWindow, opts.model);
  const durationMs = Math.round(performance.now() - t0);

  // Dry-run mode: analyze only, no output writing
  if (opts.dryRun) {
    handleDryRun(messages, result, durationMs);
    return;
  }

  // Full output: JSON or human-readable
  if (opts.json) {
    outputJsonResult(messages, result, durationMs);
  } else {
    outputHumanResult(messages, result, opts, durationMs);
  }

  // Write compacted output to disk if --output specified
  if (opts.output) {
    writeOutput(opts.output, result);
  }

  // Threshold gate: fail if reduction is below target (bypassed by --force)
  if (opts.threshold && !opts.force) {
    const thresholdPct = parseFloat(opts.threshold);
    if (!Number.isNaN(thresholdPct)) {
      const passed = enforceThreshold(messages, result, thresholdPct);
      if (!passed) {
        process.exitCode = 1;
      }
    }
  } else if (opts.threshold && opts.force) {
    const thresholdPct = parseFloat(opts.threshold);
    if (!Number.isNaN(thresholdPct)) {
      const actualPct = computeReductionPct(messages, result.messages);
      console.log(
        `\n⚡ FORCE MODE — threshold check skipped (${actualPct.toFixed(1)}% vs ${thresholdPct}% target)`,
      );
    }
  }

  // Emit completion telemetry with per-layer timings
  emitCompletionTelemetry(messages, result, durationMs);
}

export function registerCompactCommand(program: Command) {
  program
    .command('compact')
    .description('4-Layer context compaction pipeline — diagnostics and analysis')
    .option('-f, --file <path>', 'JSON conversation file to compact')
    .option('-m, --model <model>', 'Model identifier for context window sizing')
    .option('-w, --window <size>', 'Override total context window (tokens)')
    .option('-o, --output <path>', 'Write compacted JSON to file')
    .option('-t, --threshold <pct>', 'Fail if char reduction % is below this target')
    .option('--json', 'Output results as JSON')
    .option('--budget-only', 'Show budget allocation without processing messages')
    .option('--dry-run', 'Analyze compaction without writing output (diff summary)')
    .option('--verbose', 'Show per-layer timing breakdown')
    .option('--force', 'Bypass circuit breaker and threshold gates')
    .action(async (opts: CompactCommandOptions) => {
      console.log('╔══════════════════════════════════════════════════╗');
      console.log('║    COMPACTION — 4-Layer Context Pipeline         ║');
      console.log('╚══════════════════════════════════════════════════╝');
      console.log();

      logEvent('tengu_compact_invoked', {
        model: opts.model ?? 'default',
        budgetOnly: !!opts.budgetOnly,
        dryRun: !!opts.dryRun,
        verbose: !!opts.verbose,
        hasOutput: !!opts.output,
        threshold: opts.threshold ? parseFloat(opts.threshold) : undefined,
      });

      try {
        if (opts.force) {
          resetCompactionCircuitBreaker();
        } else {
          resetCompactionCircuitBreaker();
        }
        const totalWindow = opts.window ? parseInt(opts.window, 10) : undefined;

        if (opts.budgetOnly) {
          await handleBudgetOnly(opts, totalWindow);
          return;
        }

        await handleFullCompaction(opts, totalWindow);
      } catch (e: unknown) {
        const errMsg = e instanceof Error ? e.message : String(e);
        logEvent('tengu_compact_error', { error: errMsg });
        process.exitCode = 1;
      }
    });
}
