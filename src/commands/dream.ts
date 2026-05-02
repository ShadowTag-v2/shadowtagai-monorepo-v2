import { Command } from 'commander';
import { execSync, type ExecSyncOptionsWithStringEncoding } from 'child_process';
import { existsSync } from 'fs';
import { join } from 'path';
import { logEvent } from '../services/analytics/index.js';

/**
 * Dream — AutoDream Memory Consolidation
 *
 * Wraps the dream_consolidation.py daemon for on-demand invocation.
 * The consolidation pipeline:
 *   1. Orient   — scan knowledge directory for stale/conflicting KIs
 *   2. Gather   — collect session artifacts from recent conversations
 *   3. Consolidate — merge overlapping KIs, resolve contradictions
 *   4. Prune    — remove superseded items, update metadata timestamps
 *
 * Can run in --dry-run mode (orient+gather only, no writes).
 */

export interface DreamResult {
  success: boolean;
  output: string;
  durationMs: number;
  kiProcessed?: number;
  kiMerged?: number;
  kiPruned?: number;
}

/**
 * Find the dream consolidation script. Checks multiple locations
 * in the monorepo hierarchy.
 */
export function findDreamScript(baseDir?: string): string | null {
  const candidates = [
    baseDir ? join(baseDir, 'scripts', 'dream_consolidation.py') : null,
    join(process.cwd(), 'scripts', 'dream_consolidation.py'),
    join(process.cwd(), '..', 'scripts', 'dream_consolidation.py'),
  ].filter(Boolean) as string[];

  for (const candidate of candidates) {
    if (existsSync(candidate)) return candidate;
  }
  return null;
}

/**
 * Parse dream consolidation output for metrics.
 * Expected format includes lines like:
 *   [DREAM] KIs processed: 42
 *   [DREAM] KIs merged: 3
 *   [DREAM] KIs pruned: 7
 */
export function parseDreamOutput(output: string): Partial<DreamResult> {
  const metrics: Partial<DreamResult> = {};

  const processedMatch = output.match(/KIs?\s*processed:\s*(\d+)/i);
  if (processedMatch) metrics.kiProcessed = parseInt(processedMatch[1], 10);

  const mergedMatch = output.match(/KIs?\s*merged:\s*(\d+)/i);
  if (mergedMatch) metrics.kiMerged = parseInt(mergedMatch[1], 10);

  const prunedMatch = output.match(/KIs?\s*pruned:\s*(\d+)/i);
  if (prunedMatch) metrics.kiPruned = parseInt(prunedMatch[1], 10);

  return metrics;
}

export function registerDreamCommand(program: Command) {
  program
    .command('dream')
    .description('Memory consolidation (AutoDream) — orient, gather, consolidate, prune')
    .option('--dry-run', 'Run orient+gather only, no writes')
    .option('--ki-dir <path>', 'Custom knowledge items directory')
    .option('--base-dir <path>', 'Base directory for script resolution')
    .action(async (opts) => {
      const startTime = Date.now();
      console.log('╔══════════════════════════════════════════════════╗');
      console.log('║          AUTODREAM — Memory Consolidation        ║');
      console.log('╚══════════════════════════════════════════════════╝');
      console.log();

      logEvent('tengu_dream_invoked', { dryRun: !!opts.dryRun });

      try {
        const scriptPath = findDreamScript(opts.baseDir);
        if (!scriptPath) {
          console.error('✗ dream_consolidation.py not found.');
          console.error('  Expected at: scripts/dream_consolidation.py');
          console.error('  Ensure the script exists in the monorepo.');
          logEvent('tengu_dream_error', { error: 'script_not_found' });
          process.exitCode = 1;
          return;
        }

        console.log(`Script: ${scriptPath}`);
        if (opts.dryRun) console.log('Mode: DRY RUN (orient+gather only)');
        console.log();

        const args: string[] = [];
        if (opts.dryRun) args.push('--dry-run');
        if (opts.kiDir) args.push('--ki-dir', opts.kiDir);

        const execOpts: ExecSyncOptionsWithStringEncoding = {
          encoding: 'utf-8',
          timeout: 300_000, // 5 minute timeout
          env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' },
        };

        console.log('Running consolidation pipeline...');
        console.log('  [1/4] Orient  — scanning knowledge directory');
        console.log('  [2/4] Gather  — collecting session artifacts');
        console.log('  [3/4] Consolidate — merging overlapping KIs');
        console.log('  [4/4] Prune   — removing superseded items');
        console.log();

        const output = execSync(
          `python3 "${scriptPath}" ${args.join(' ')}`,
          execOpts,
        );

        const metrics = parseDreamOutput(output);
        const durationMs = Date.now() - startTime;

        console.log(output);
        console.log('─'.repeat(50));
        console.log(`✓ AutoDream complete in ${durationMs}ms`);

        if (metrics.kiProcessed != null) console.log(`  KIs processed: ${metrics.kiProcessed}`);
        if (metrics.kiMerged != null) console.log(`  KIs merged:    ${metrics.kiMerged}`);
        if (metrics.kiPruned != null) console.log(`  KIs pruned:    ${metrics.kiPruned}`);

        logEvent('tengu_dream_complete', {
          durationMs,
          ...metrics,
        });
      } catch (e: any) {
        const durationMs = Date.now() - startTime;
        logEvent('tengu_dream_error', { error: e.message, durationMs });
        console.error('AutoDream consolidation failed:', e.message);
        if (e.stderr) console.error(e.stderr);
        process.exitCode = 1;
      }
    });
}
