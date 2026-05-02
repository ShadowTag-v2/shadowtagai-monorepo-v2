import { readFileSync } from 'node:fs';
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
 *
 * Usage:
 *   agnt compact --file conversation.json --model gemini-2.5-pro
 *   agnt compact --file conv.json --window 200000 --json
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
  const inputChars = JSON.stringify(messages).length;
  const outputChars = JSON.stringify(result.messages).length;
  const charReduction = inputChars - outputChars;
  const pct = inputChars > 0 ? ((charReduction / inputChars) * 100).toFixed(1) : '0.0';

  console.log(formatBudget(result.budget as unknown as Record<string, number>));
  console.log();
  console.log('── DRY RUN — Compaction Diff Summary ──');
  console.log(`  Input messages:    ${messages.length}`);
  console.log(`  Output messages:   ${result.messages.length}`);
  console.log(`  Messages removed:  ${removed}`);
  console.log(`  Char reduction:    ${charReduction} (${pct}%)`);
  if (result.circuitBroken) {
    console.log('  ⚠ Circuit breaker activated — compaction halted.');
  }
  console.log(`\n✓ Dry-run analysis complete in ${durationMs}ms`);

  logEvent('tengu_compact_dry_run', {
    inputMessages: messages.length,
    outputMessages: result.messages.length,
    durationMs,
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
    circuitBroken: result.circuitBroken,
    l1_ms: result.layerTimings?.apiMicrocompact,
    l2_ms: result.layerTimings?.historySnip,
    l3_ms: result.layerTimings?.contextCollapse,
    l4_ms: result.layerTimings?.tokenBudget,
  });
}

export function registerCompactCommand(program: Command) {
  program
    .command('compact')
    .description('4-Layer context compaction pipeline — diagnostics and analysis')
    .option('-f, --file <path>', 'JSON conversation file to compact')
    .option('-m, --model <model>', 'Model identifier for context window sizing')
    .option('-w, --window <size>', 'Override total context window (tokens)')
    .option('--json', 'Output results as JSON')
    .option('--budget-only', 'Show budget allocation without processing messages')
    .option('--dry-run', 'Analyze compaction without writing output (diff summary)')
    .option('--verbose', 'Show per-layer timing breakdown')
    .action(async (opts: CompactCommandOptions) => {
      const startTime = Date.now();
      console.log('╔══════════════════════════════════════════════════╗');
      console.log('║    COMPACTION — 4-Layer Context Pipeline         ║');
      console.log('╚══════════════════════════════════════════════════╝');
      console.log();

      logEvent('tengu_compact_invoked', {
        model: opts.model ?? 'default',
        budgetOnly: !!opts.budgetOnly,
        dryRun: !!opts.dryRun,
        verbose: !!opts.verbose,
      });

      try {
        resetCompactionCircuitBreaker();
        const totalWindow = opts.window ? parseInt(opts.window, 10) : undefined;

        if (opts.budgetOnly) {
          await handleBudgetOnly(opts, totalWindow);
          return;
        }

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

        console.log(`Input: ${opts.file} (${messages.length} messages)`);
        console.log(`Model: ${opts.model ?? '(default 200K)'}`);
        if (opts.dryRun) console.log('Mode:  DRY RUN (no output written)');
        if (opts.verbose) console.log('Mode:  VERBOSE (per-layer timing enabled)');
        console.log();

        const result = await runCompactionPipeline(messages, totalWindow, opts.model);
        const durationMs = Date.now() - startTime;

        if (opts.dryRun) {
          handleDryRun(messages, result, durationMs);
          return;
        }

        if (opts.json) {
          outputJsonResult(messages, result, durationMs);
        } else {
          outputHumanResult(messages, result, opts, durationMs);
        }

        emitCompletionTelemetry(messages, result, durationMs);
      } catch (e: unknown) {
        const errMsg = e instanceof Error ? e.message : String(e);
        logEvent('tengu_compact_error', { error: errMsg });
        console.error('Compaction failed:', errMsg);
        process.exitCode = 1;
      }
    });
}
