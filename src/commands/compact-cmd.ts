import type { Command } from 'commander';
import { readFileSync } from 'fs';
import { logEvent } from '../services/analytics/index.js';
import { resetCompactionCircuitBreaker, runCompactionPipeline } from '../services/compact/index.js';

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

export function registerCompactCommand(program: Command) {
  program
    .command('compact')
    .description('4-Layer context compaction pipeline — diagnostics and analysis')
    .option('-f, --file <path>', 'JSON conversation file to compact')
    .option('-m, --model <model>', 'Model identifier for context window sizing')
    .option('-w, --window <size>', 'Override total context window (tokens)')
    .option('--json', 'Output results as JSON')
    .option('--budget-only', 'Show budget allocation without processing messages')
    .action(async (opts: CompactCommandOptions) => {
      const startTime = Date.now();
      console.log('╔══════════════════════════════════════════════════╗');
      console.log('║    COMPACTION — 4-Layer Context Pipeline         ║');
      console.log('╚══════════════════════════════════════════════════╝');
      console.log();

      logEvent('tengu_compact_invoked', {
        model: opts.model ?? 'default',
        budgetOnly: !!opts.budgetOnly,
      });

      try {
        resetCompactionCircuitBreaker();

        const totalWindow = opts.window ? parseInt(opts.window, 10) : undefined;

        // Budget-only mode: just show the allocation
        if (opts.budgetOnly) {
          const { allocateTokenBudget } = await import('../services/compact/tokenBudget.js');
          const budget = allocateTokenBudget([], totalWindow, opts.model);

          if (opts.json) {
            console.log(JSON.stringify(budget, null, 2));
          } else {
            console.log(`Model: ${opts.model ?? '(default 200K)'}`);
            console.log();
            console.log(formatBudget(budget as unknown as Record<string, number>));
          }
          return;
        }

        // Full compaction: requires a conversation file
        if (!opts.file) {
          console.error('✗ --file is required for full compaction (or use --budget-only).');
          process.exitCode = 1;
          return;
        }

        const raw = readFileSync(opts.file, 'utf-8');
        const messages: Record<string, unknown>[] = JSON.parse(raw);

        if (!Array.isArray(messages)) {
          console.error('✗ Input file must contain a JSON array of messages.');
          process.exitCode = 1;
          return;
        }

        console.log(`Input: ${opts.file} (${messages.length} messages)`);
        console.log(`Model: ${opts.model ?? '(default 200K)'}`);
        console.log();

        const result = await runCompactionPipeline(messages, totalWindow, opts.model);
        const durationMs = Date.now() - startTime;

        if (opts.json) {
          console.log(
            JSON.stringify(
              {
                inputMessages: messages.length,
                outputMessages: result.messages.length,
                reduction: messages.length - result.messages.length,
                layersApplied: result.layersApplied,
                circuitBroken: result.circuitBroken,
                budget: result.budget,
                durationMs,
              },
              null,
              2,
            ),
          );
        } else {
          console.log(formatBudget(result.budget as unknown as Record<string, number>));
          console.log();
          console.log('Layer Execution:');
          for (const layer of result.layersApplied) {
            console.log(`  ✓ ${layer}`);
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

        logEvent('tengu_compact_complete', {
          inputMessages: messages.length,
          outputMessages: result.messages.length,
          durationMs,
          circuitBroken: result.circuitBroken,
        });
      } catch (e: any) {
        logEvent('tengu_compact_error', { error: e.message });
        console.error('Compaction failed:', e.message);
        process.exitCode = 1;
      }
    });
}
