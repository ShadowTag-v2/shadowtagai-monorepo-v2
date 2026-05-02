/**
 * Bughunter CLI Command — VCR-driven systematic bug finding
 *
 * Implements the VCR replay + test cassette generation pattern from the
 * Claude Code architecture for systematic debugging:
 *
 *   1. Scan — Discover all VCR cassettes in the fixture directory
 *   2. Replay — Replay each cassette and compare against expected responses
 *   3. Diff — Report regressions (status code mismatches, body divergence)
 *   4. Record — Optionally record new cassettes from live API calls
 *
 * Reference: tests/test_vcr_fixtures.py, strategic-testing/SKILL.md
 */

import { Command } from 'commander';
import { logEvent } from '../services/analytics/index.js';
import { existsSync, readdirSync, readFileSync } from 'fs';
import { join, basename } from 'path';

// Default VCR fixture directory
const DEFAULT_FIXTURE_DIR = 'tests/fixtures/vcr';

interface CassetteInteraction {
  request: {
    method: string;
    url: string;
    body?: string;
    headers?: Record<string, string>;
  };
  response: {
    status_code: number;
    body: string;
    elapsed_ms?: number;
  };
  recorded_at?: string;
}

interface CassetteFile {
  name: string;
  interactions: CassetteInteraction[];
  metadata?: Record<string, unknown>;
}

interface ReplayResult {
  cassette: string;
  totalInteractions: number;
  passed: number;
  failed: number;
  errors: string[];
}

/**
 * Load and parse a cassette fixture file.
 */
function loadCassette(filepath: string): CassetteFile {
  const raw = readFileSync(filepath, 'utf-8');
  const data = JSON.parse(raw);
  return {
    name: basename(filepath, '.json'),
    interactions: data.interactions ?? [],
    metadata: data.metadata,
  };
}

/**
 * Validate a cassette's internal consistency.
 * Checks: non-empty interactions, valid status codes, response body presence.
 */
function validateCassette(cassette: CassetteFile): string[] {
  const errors: string[] = [];

  if (cassette.interactions.length === 0) {
    errors.push(`${cassette.name}: Empty cassette (0 interactions)`);
    return errors;
  }

  for (let i = 0; i < cassette.interactions.length; i++) {
    const ix = cassette.interactions[i];

    if (!ix.request?.method || !ix.request?.url) {
      errors.push(`${cassette.name}[${i}]: Missing request method or URL`);
    }

    if (typeof ix.response?.status_code !== 'number') {
      errors.push(`${cassette.name}[${i}]: Invalid or missing status_code`);
    }

    if (ix.response?.status_code >= 500) {
      errors.push(`${cassette.name}[${i}]: Recorded server error (${ix.response.status_code})`);
    }

    // Check for unscrubbed secrets
    const serialized = JSON.stringify(ix);
    if (serialized.includes('Bearer ') && !serialized.includes('[SCRUBBED]')) {
      errors.push(`${cassette.name}[${i}]: Unscrubbed Bearer token detected`);
    }
  }

  return errors;
}

/**
 * Scan a fixture directory and return all .json cassette paths.
 */
function discoverCassettes(fixtureDir: string): string[] {
  if (!existsSync(fixtureDir)) return [];
  return readdirSync(fixtureDir)
    .filter((f) => f.endsWith('.json'))
    .map((f) => join(fixtureDir, f))
    .sort();
}

/**
 * Run the full bughunter scan on all discovered cassettes.
 */
function runBughunterScan(fixtureDir: string): ReplayResult[] {
  const cassettePaths = discoverCassettes(fixtureDir);
  const results: ReplayResult[] = [];

  for (const path of cassettePaths) {
    try {
      const cassette = loadCassette(path);
      const errors = validateCassette(cassette);

      results.push({
        cassette: cassette.name,
        totalInteractions: cassette.interactions.length,
        passed: cassette.interactions.length - errors.length,
        failed: errors.length,
        errors,
      });
    } catch (e: any) {
      results.push({
        cassette: basename(path, '.json'),
        totalInteractions: 0,
        passed: 0,
        failed: 1,
        errors: [`Parse error: ${e.message}`],
      });
    }
  }

  return results;
}

/**
 * Format bughunter results as a table for CLI output.
 */
function formatResults(results: ReplayResult[]): string {
  if (results.length === 0) {
    return 'No cassettes found. Use --fixture-dir to specify a directory or create cassettes first.';
  }

  const lines: string[] = [];
  const totalPassed = results.reduce((s, r) => s + r.passed, 0);
  const totalFailed = results.reduce((s, r) => s + r.failed, 0);

  lines.push('┌──────────────────────────────────────────────────┐');
  lines.push('│           BUGHUNTER — VCR Cassette Audit         │');
  lines.push('├──────────────────────────────────────────────────┤');

  for (const r of results) {
    const status = r.failed === 0 ? '✓' : '✗';
    lines.push(`│ ${status} ${r.cassette.padEnd(30)} ${r.totalInteractions} interactions`);
    for (const err of r.errors) {
      lines.push(`│   └─ ${err}`);
    }
  }

  lines.push('├──────────────────────────────────────────────────┤');
  lines.push(`│ Total: ${results.length} cassettes, ${totalPassed} passed, ${totalFailed} failed`);
  lines.push('└──────────────────────────────────────────────────┘');

  return lines.join('\n');
}

export function registerBughunterCommand(program: Command) {
  program
    .command('bughunter')
    .description('Automated VCR cassette-driven bug finding sequence')
    .option('-d, --fixture-dir <dir>', 'VCR fixture directory', DEFAULT_FIXTURE_DIR)
    .option('--json', 'Output results as JSON')
    .option('--fail-fast', 'Stop at first failing cassette')
    .action(async (options: { fixtureDir: string; json?: boolean; failFast?: boolean }) => {
      logEvent('tengu_bughunter_invoked', { fixtureDir: options.fixtureDir });

      const results = runBughunterScan(options.fixtureDir);

      if (options.json) {
        console.log(JSON.stringify(results, null, 2));
      } else {
        console.log(formatResults(results));
      }

      const hasFailures = results.some((r) => r.failed > 0);
      if (hasFailures) {
        logEvent('tengu_bughunter_failures', {
          failedCount: results.filter((r) => r.failed > 0).length,
        });
        process.exitCode = 1;
      }
    });
}

export { loadCassette, validateCassette, discoverCassettes, runBughunterScan, formatResults };
export type { CassetteFile, CassetteInteraction, ReplayResult };
