import type { Command } from 'commander';
import { existsSync, mkdirSync, writeFileSync } from 'fs';
import { dirname, join } from 'path';
import { logEvent } from '../services/analytics/index.js';

/**
 * Ultraplan — 5-Phase Deep Planning Protocol (STATE B Speculation)
 *
 * Implements the CCR session planning pipeline:
 *   Phase 1: Problem Decomposition    — gather requirements, constraints
 *   Phase 2: Solution Architecture    — propose approach, alternatives
 *   Phase 3: Risk Assessment          — identify blockers, mitigations
 *   Phase 4: Implementation Plan      — step-by-step tasks with owners
 *   Phase 5: Validation Criteria      — define "done", acceptance tests
 *
 * Output is a structured markdown plan written to --plan-file (default: TASK.md).
 * This is the terminal-side counterpart of the browser PlanModal flow.
 */

export interface PlanPhase {
  name: string;
  description: string;
  status: 'pending' | 'active' | 'complete' | 'skipped';
  content: string;
  durationMs?: number;
}

export interface UltraplanResult {
  phases: PlanPhase[];
  totalDurationMs: number;
  outputFile: string;
  timestamp: string;
}

const PHASE_DEFINITIONS: Array<{ name: string; description: string }> = [
  {
    name: 'Problem Decomposition',
    description: 'Gather requirements, constraints, and scope boundaries.',
  },
  {
    name: 'Solution Architecture',
    description: 'Propose approach, evaluate alternatives, select strategy.',
  },
  {
    name: 'Risk Assessment',
    description: 'Identify blockers, dependencies, failure modes, and mitigations.',
  },
  {
    name: 'Implementation Plan',
    description: 'Define step-by-step tasks with owners, estimates, and checkpoints.',
  },
  {
    name: 'Validation Criteria',
    description: 'Specify acceptance tests, "definition of done", and verification steps.',
  },
];

/**
 * Generate the plan phases. In a full CCR session, this would poll the
 * remote agent's ExitPlanMode tool results. In standalone mode, it
 * scaffolds the plan structure for manual fill-in.
 */
export function generatePlanScaffold(topic?: string): PlanPhase[] {
  return PHASE_DEFINITIONS.map((def, i) => ({
    name: def.name,
    description: def.description,
    status: 'pending' as const,
    content: topic
      ? `## Phase ${i + 1}: ${def.name}\n\n> ${def.description}\n\n**Topic:** ${topic}\n\n<!-- Fill in details -->\n`
      : `## Phase ${i + 1}: ${def.name}\n\n> ${def.description}\n\n<!-- Fill in details -->\n`,
  }));
}

/**
 * Render phases to markdown.
 */
export function renderPlanMarkdown(phases: PlanPhase[], topic?: string): string {
  const header = [
    `# Ultraplan — Deep Planning Document`,
    ``,
    `**Generated:** ${new Date().toISOString()}`,
    `**Mode:** STATE B Speculation`,
    topic ? `**Topic:** ${topic}` : '',
    `**Phases:** ${phases.length}`,
    ``,
    `---`,
    ``,
  ]
    .filter(Boolean)
    .join('\n');

  const body = phases
    .map((p, i) => {
      const statusIcon =
        p.status === 'complete'
          ? '✅'
          : p.status === 'active'
            ? '🔄'
            : p.status === 'skipped'
              ? '⏭️'
              : '⏳';
      return [
        `## Phase ${i + 1}: ${p.name} ${statusIcon}`,
        ``,
        `> ${p.description}`,
        ``,
        p.content || '<!-- No content yet -->',
        ``,
        p.durationMs != null ? `*Duration: ${p.durationMs}ms*` : '',
        ``,
      ]
        .filter(Boolean)
        .join('\n');
    })
    .join('\n---\n\n');

  return header + body;
}

export function registerUltraplanCommand(program: Command) {
  program
    .command('ultraplan')
    .description('Deep planning mode (STATE B Speculation) — 5-phase plan interview')
    .option('-t, --topic <topic>', 'Planning topic or problem statement')
    .option('-o, --plan-file <path>', 'Output file path for the plan', 'TASK.md')
    .option('--dry-run', 'Generate scaffold without writing to disk')
    .action(async (opts) => {
      const startTime = Date.now();
      console.log('╔══════════════════════════════════════════════════╗');
      console.log('║        ULTRAPLAN — STATE B Speculation           ║');
      console.log('║        5-Phase Deep Planning Protocol            ║');
      console.log('╚══════════════════════════════════════════════════╝');
      console.log();

      logEvent('tengu_ultraplan_invoked', { topic: opts.topic || 'unspecified' });

      try {
        console.log('Transitioning to STATE B: Clutch...');
        console.log();

        const phases = generatePlanScaffold(opts.topic);

        // In standalone mode, scaffold all phases immediately
        for (let i = 0; i < phases.length; i++) {
          const phase = phases[i];
          phase.status = 'active';
          console.log(`  [Phase ${i + 1}/${phases.length}] ${phase.name}...`);
          const phaseStart = Date.now();

          // Mark complete (in CCR mode, this would wait for remote agent)
          phase.status = 'complete';
          phase.durationMs = Date.now() - phaseStart;
        }

        const markdown = renderPlanMarkdown(phases, opts.topic);

        if (opts.dryRun) {
          console.log('\n--- DRY RUN OUTPUT ---\n');
          console.log(markdown);
        } else {
          const outPath = opts.planFile;
          const dir = dirname(outPath);
          if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
          writeFileSync(outPath, markdown, 'utf-8');
          console.log(`\n✓ Plan written to: ${outPath}`);
        }

        const totalDuration = Date.now() - startTime;
        logEvent('tengu_ultraplan_complete', {
          phases: phases.length,
          durationMs: totalDuration,
          outputFile: opts.planFile,
        });

        console.log(`\nUltraplan complete in ${totalDuration}ms.`);
      } catch (e: any) {
        logEvent('tengu_ultraplan_error', { error: e.message });
        console.error('Ultraplan execution failed:', e.message);
        process.exitCode = 1;
      }
    });
}
