/**
 * compact-benchmark.ts — CI Performance Regression Tracker
 *
 * Generates synthetic conversations of varying sizes and profiles
 * the compaction pipeline, producing a machine-readable benchmark report.
 *
 * Usage:
 *   npx tsx tests/benchmarks/compact-benchmark.ts
 *   npx tsx tests/benchmarks/compact-benchmark.ts --sizes 100,500,1000
 *   npx tsx tests/benchmarks/compact-benchmark.ts --json
 *
 * CI Integration:
 *   Add to CI pipeline to detect performance regressions.
 *   Exits with code 1 if any benchmark exceeds the P95_CEILING_MS threshold.
 */

import { runCompactionPipeline, resetCompactionCircuitBreaker } from '../../src/services/compact/index.js';

// Performance ceiling: fail if any run exceeds this (ms)
const P95_CEILING_MS = 500;

interface BenchmarkResult {
  messageCount: number;
  iterations: number;
  avgMs: number;
  minMs: number;
  maxMs: number;
  p95Ms: number;
  avgReductionPct: number;
  layerTimings: Record<string, number>;
}

/** Generate a synthetic conversation with realistic tool_use/tool_result pairs */
function generateSyntheticConversation(messageCount: number): Record<string, unknown>[] {
  const messages: Record<string, unknown>[] = [];
  const tools = ['Read', 'Grep', 'View', 'Search', 'Bash', 'Write', 'Edit', 'ListDir'];

  for (let i = 0; i < messageCount; i++) {
    const round = Math.floor(i / 4);

    if (i % 4 === 0) {
      // User message
      messages.push({
        role: 'user',
        content: `Request #${round}: Perform operation ${round} on the codebase. ${'x'.repeat(50 + (i % 200))}`,
      });
    } else if (i % 4 === 1) {
      // Assistant with tool_use
      const toolName = tools[round % tools.length];
      messages.push({
        role: 'assistant',
        content: [
          {
            type: 'tool_use',
            id: `tu-${round}`,
            name: toolName,
            input: { path: `/src/file-${round}.ts`, query: `search-${round}` },
          },
        ],
        message: { id: `g${round}` },
      });
    } else if (i % 4 === 2) {
      // Tool result (deliberately verbose to exercise microcompact)
      const outputSize = 200 + (round % 5) * 500;
      messages.push({
        role: 'user',
        content: [
          {
            type: 'tool_result',
            tool_use_id: `tu-${round}`,
            content: `${'Line of output content for tool result. '.repeat(outputSize / 40)}`,
          },
        ],
      });
    } else {
      // Assistant summary
      messages.push({
        role: 'assistant',
        content: `Analysis complete for round ${round}. Found ${round * 3} items. ${'Summary detail. '.repeat(5 + (round % 10))}`,
        message: { id: `g${round}` },
      });
    }
  }

  // Add some duplicate error messages to exercise contextCollapse
  for (let i = 0; i < Math.min(10, messageCount / 10); i++) {
    messages.push({
      role: 'user',
      content: 'Error: ENOENT: no such file or directory, open /src/missing.ts',
    });
  }

  return messages;
}

/** Run a single benchmark iteration */
async function benchmarkIteration(
  messages: Record<string, unknown>[],
): Promise<{ durationMs: number; reductionPct: number; layerTimings: Record<string, number> }> {
  resetCompactionCircuitBreaker();
  const start = performance.now();
  const result = await runCompactionPipeline(messages);
  const durationMs = performance.now() - start;

  const inputChars = JSON.stringify(messages).length;
  const outputChars = JSON.stringify(result.messages).length;
  const reductionPct = inputChars > 0 ? ((inputChars - outputChars) / inputChars) * 100 : 0;

  return {
    durationMs,
    reductionPct,
    layerTimings: result.layerTimings ?? {},
  };
}

/** Compute percentile from sorted array */
function percentile(sorted: number[], p: number): number {
  const idx = Math.ceil((p / 100) * sorted.length) - 1;
  return sorted[Math.max(0, idx)];
}

/** Run benchmark suite for a given message count */
async function runBenchmark(messageCount: number, iterations = 5): Promise<BenchmarkResult> {
  const messages = generateSyntheticConversation(messageCount);
  const durations: number[] = [];
  const reductions: number[] = [];
  const layerAccum: Record<string, number[]> = {};

  for (let i = 0; i < iterations; i++) {
    const result = await benchmarkIteration(messages);
    durations.push(result.durationMs);
    reductions.push(result.reductionPct);

    for (const [layer, ms] of Object.entries(result.layerTimings)) {
      if (!layerAccum[layer]) layerAccum[layer] = [];
      layerAccum[layer].push(ms);
    }
  }

  durations.sort((a, b) => a - b);
  const avgLayerTimings: Record<string, number> = {};
  for (const [layer, timings] of Object.entries(layerAccum)) {
    avgLayerTimings[layer] = timings.reduce((a, b) => a + b, 0) / timings.length;
  }

  return {
    messageCount,
    iterations,
    avgMs: durations.reduce((a, b) => a + b, 0) / durations.length,
    minMs: durations[0],
    maxMs: durations[durations.length - 1],
    p95Ms: percentile(durations, 95),
    avgReductionPct: reductions.reduce((a, b) => a + b, 0) / reductions.length,
    layerTimings: avgLayerTimings,
  };
}

/** Format benchmark results as a table */
function formatTable(results: BenchmarkResult[]): string {
  const lines: string[] = [];
  lines.push('╔══════════════════════════════════════════════════════════════════════════╗');
  lines.push('║           COMPACT BENCHMARK — CI Performance Regression Tracker        ║');
  lines.push('╠══════════════════════════════════════════════════════════════════════════╣');
  lines.push(
    '║ Messages │  Avg(ms)  │  Min(ms)  │  Max(ms)  │  P95(ms)  │ Reduction ║',
  );
  lines.push(
    '╠══════════╪═══════════╪═══════════╪═══════════╪═══════════╪═══════════╣',
  );

  for (const r of results) {
    lines.push(
      `║ ${String(r.messageCount).padStart(8)} │ ${r.avgMs.toFixed(2).padStart(9)} │ ${r.minMs.toFixed(2).padStart(9)} │ ${r.maxMs.toFixed(2).padStart(9)} │ ${r.p95Ms.toFixed(2).padStart(9)} │ ${r.avgReductionPct.toFixed(1).padStart(8)}% ║`,
    );
  }

  lines.push('╚══════════════════════════════════════════════════════════════════════════╝');
  return lines.join('\n');
}

// Main execution
async function main() {
  const args = process.argv.slice(2);
  const jsonMode = args.includes('--json');

  // Parse --sizes flag (default: 50, 100, 250, 500, 1000)
  const sizesIdx = args.indexOf('--sizes');
  const sizes =
    sizesIdx >= 0 && args[sizesIdx + 1]
      ? args[sizesIdx + 1].split(',').map(Number)
      : [50, 100, 250, 500, 1000];

  const results: BenchmarkResult[] = [];
  let failed = false;

  for (const size of sizes) {
    if (!jsonMode) {
      process.stdout.write(`Benchmarking ${size} messages... `);
    }
    const result = await runBenchmark(size);
    results.push(result);

    if (!jsonMode) {
      console.log(`${result.avgMs.toFixed(2)}ms avg (p95: ${result.p95Ms.toFixed(2)}ms)`);
    }

    if (result.p95Ms > P95_CEILING_MS) {
      failed = true;
      if (!jsonMode) {
        console.log(`  ✗ REGRESSION: P95 ${result.p95Ms.toFixed(2)}ms > ceiling ${P95_CEILING_MS}ms`);
      }
    }
  }

  if (jsonMode) {
    console.log(JSON.stringify({ results, p95CeilingMs: P95_CEILING_MS, passed: !failed }, null, 2));
  } else {
    console.log();
    console.log(formatTable(results));
    console.log();

    // Layer breakdown for largest run
    const largest = results[results.length - 1];
    console.log(`Layer breakdown (${largest.messageCount} messages):`);
    for (const [layer, ms] of Object.entries(largest.layerTimings)) {
      console.log(`  ${layer.padEnd(22)} ${ms.toFixed(3)}ms`);
    }
    console.log();

    if (failed) {
      console.log(`✗ BENCHMARK FAILED — P95 ceiling exceeded (${P95_CEILING_MS}ms)`);
    } else {
      console.log(`✓ BENCHMARK PASSED — all P95 values under ${P95_CEILING_MS}ms`);
    }
  }

  process.exit(failed ? 1 : 0);
}

main().catch((err) => {
  console.error('Benchmark failed:', err);
  process.exit(1);
});
