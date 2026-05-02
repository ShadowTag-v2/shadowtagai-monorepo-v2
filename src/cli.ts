#!/usr/bin/env node
/**
 * AGNT CLI — Commander-based entrypoint for the ShadowTag Agent Runtime.
 *
 * Registers all custom commands:
 *   - bughunter: VCR cassette-driven bug finding
 *   - compact: 4-layer context compaction pipeline diagnostics
 *   - dream: Memory consolidation (AutoDream)
 *   - ultraplan: Deep planning mode (STATE B Speculation)
 *
 * Usage:
 *   npx tsx src/cli.ts bughunter --fixture-dir tests/fixtures/vcr
 *   npx tsx src/cli.ts compact --budget-only --model gemini-2.5-pro
 *   npx tsx src/cli.ts dream
 *   npx tsx src/cli.ts ultraplan
 *   npx tsx src/cli.ts --help
 */

import { Command } from 'commander';
import { registerBughunterCommand } from './commands/bughunter.js';
import { registerCompactCommand } from './commands/compact-cmd.js';
import { registerDreamCommand } from './commands/dream.js';
import { registerUltraplanCommand } from './commands/ultraplan.js';

const program = new Command();

program.name('agnt').description('ShadowTag Agent Runtime CLI — AGNT v11.2').version('11.2.0');

// Register all commands
registerBughunterCommand(program);
registerCompactCommand(program);
registerDreamCommand(program);
registerUltraplanCommand(program);

// Parse and execute
program.parseAsync(process.argv).catch((err: Error) => {
  console.error(`Fatal: ${err.message}`);
  process.exit(1);
});
