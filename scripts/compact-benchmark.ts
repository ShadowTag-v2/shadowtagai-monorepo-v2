#!/usr/bin/env npx tsx
/**
 * compact-benchmark.ts — CI Performance Regression Tracking
 *
 * Generates synthetic conversations of varying sizes and measures
 * compaction pipeline throughput. Outputs a JSON report suitable
 * for CI comparison between runs.
 *
 * Usage:
 *   npx tsx scripts/compact-benchmark.ts
 *   npx tsx scripts/compact-benchmark.ts --sizes 100,500,1000,2000
 *   npx tsx scripts/compact-benchmark.ts --iterations 5
 *   npx tsx scripts/compact-benchmark.ts --output bench-results.json
 *
 * Exit codes:
 *   0 — all benchmarks within expected thresholds
 *   1 — regression detected (>2x baseline)
 */

import { writeFileSync } from "node:fs";
import { join } from "node:path";
import {
  resetCompactionCircuitBreaker,
  runCompactionPipeline,
} from "../src/services/compact/index.js";

// ─── Config ──────────────────────────────────────────────────────────

interface BenchConfig {
  sizes: number[];
  iterations: number;
  outputPath: string | null;
  /** Max ms per 1000 messages before flagging regression */
  regressionThresholdMs: number;
}

function parseArgs(): BenchConfig {
  const args = process.argv.slice(2);
  const config: BenchConfig = {
    sizes: [50, 100, 250, 500, 1000, 2000],
    iterations: 3,
    outputPath: null,
    regressionThresholdMs: 100, // 100ms per 1000 messages
  };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--sizes" && args[i + 1]) {
      config.sizes = args[i + 1].split(",").map(Number);
      i++;
    } else if (args[i] === "--iterations" && args[i + 1]) {
      config.iterations = parseInt(args[i + 1], 10);
      i++;
    } else if (args[i] === "--output" && args[i + 1]) {
      config.outputPath = args[i + 1];
      i++;
    }
  }
  return config;
}

// ─── Synthetic Data Generator ────────────────────────────────────────

function generateSyntheticConversation(messageCount: number): Record<string, unknown>[] {
  const messages: Record<string, unknown>[] = [];

  for (let i = 0; i < messageCount; i++) {
    const role = i % 2 === 0 ? "user" : "assistant";

    if (role === "user") {
      messages.push({
        role: "user",
        content: `Message ${i}: ${generateRealisticContent(i)}`,
      });
    } else {
      // Every 5th assistant message includes a tool_use block
      if (i % 10 === 1) {
        messages.push({
          role: "assistant",
          content: [
            {
              type: "tool_use",
              id: `toolu_${i}`,
              name: "write_to_file",
              input: {
                path: `/src/file_${i}.ts`,
                content: "x".repeat(500 + (i % 300)),
              },
            },
          ],
        });
        messages.push({
          role: "user",
          content: [
            {
              type: "tool_result",
              tool_use_id: `toolu_${i}`,
              content: `Tool output for iteration ${i}: ${"result_data ".repeat(50)}`,
            },
          ],
        });
      } else {
        messages.push({
          role: "assistant",
          content: `Response ${i}: ${generateRealisticContent(i)}`,
        });
      }
    }
  }
  return messages;
}

function generateRealisticContent(seed: number): string {
  const templates = [
    "I need to refactor the authentication module to support OAuth2 PKCE flow.",
    "The database migration failed because the column type mismatch on user_sessions.",
    "Let me analyze the performance trace to identify the bottleneck in the API gateway.",
    "Here is the updated configuration for the Kubernetes deployment manifest.",
    "The circuit breaker is tripping because the upstream service has >500ms p99 latency.",
    "We should add retry logic with exponential backoff for the payment webhook handler.",
    "The test coverage for the notification service dropped below 80% after the refactor.",
    "I found a race condition in the WebSocket connection manager during reconnection.",
  ];
  return templates[seed % templates.length];
}

// ─── Benchmark Runner ────────────────────────────────────────────────

interface BenchmarkResult {
  messageCount: number;
  iterations: number;
  avgDurationMs: number;
  minDurationMs: number;
  maxDurationMs: number;
  p95DurationMs: number;
  msPerThousandMessages: number;
  avgReductionPct: number;
  avgOutputMessages: number;
  layerTimings: Record<string, number>;
  regression: boolean;
}

async function runBenchmark(
  messageCount: number,
  iterations: number,
  regressionThresholdMs: number,
): Promise<BenchmarkResult> {
  const durations: number[] = [];
  const reductions: number[] = [];
  const outputCounts: number[] = [];
  const allLayerTimings: Record<string, number[]> = {};

  for (let iter = 0; iter < iterations; iter++) {
    const messages = generateSyntheticConversation(messageCount);
    resetCompactionCircuitBreaker();

    const t0 = performance.now();
    const result = await runCompactionPipeline(messages, 200_000, "gemini-2.5-pro");
    const elapsed = performance.now() - t0;

    durations.push(elapsed);
    outputCounts.push(result.messages.length);

    const inputChars = JSON.stringify(messages).length;
    const outputChars = JSON.stringify(result.messages).length;
    reductions.push(inputChars > 0 ? ((inputChars - outputChars) / inputChars) * 100 : 0);

    if (result.layerTimings) {
      for (const [layer, ms] of Object.entries(result.layerTimings)) {
        if (!allLayerTimings[layer]) allLayerTimings[layer] = [];
        allLayerTimings[layer].push(ms);
      }
    }
  }

  durations.sort((a, b) => a - b);
  const p95Idx = Math.min(Math.floor(durations.length * 0.95), durations.length - 1);

  const avgDuration = durations.reduce((a, b) => a + b, 0) / durations.length;
  const msPerK = (avgDuration / messageCount) * 1000;

  const avgLayerTimings: Record<string, number> = {};
  for (const [layer, times] of Object.entries(allLayerTimings)) {
    avgLayerTimings[layer] = times.reduce((a, b) => a + b, 0) / times.length;
  }

  return {
    messageCount,
    iterations,
    avgDurationMs: Math.round(avgDuration * 100) / 100,
    minDurationMs: Math.round(durations[0] * 100) / 100,
    maxDurationMs: Math.round(durations[durations.length - 1] * 100) / 100,
    p95DurationMs: Math.round(durations[p95Idx] * 100) / 100,
    msPerThousandMessages: Math.round(msPerK * 100) / 100,
    avgReductionPct:
      Math.round((reductions.reduce((a, b) => a + b, 0) / reductions.length) * 100) / 100,
    avgOutputMessages: Math.round(outputCounts.reduce((a, b) => a + b, 0) / outputCounts.length),
    layerTimings: avgLayerTimings,
    regression: msPerK > regressionThresholdMs,
  };
}

// ─── Main ────────────────────────────────────────────────────────────

async function main() {
  const config = parseArgs();

  console.log("╔══════════════════════════════════════════════════╗");
  console.log("║   COMPACT BENCHMARK — Pipeline Perf Regression  ║");
  console.log("╚══════════════════════════════════════════════════╝");
  console.log();
  console.log(`Sizes: ${config.sizes.join(", ")}`);
  console.log(`Iterations per size: ${config.iterations}`);
  console.log(`Regression threshold: ${config.regressionThresholdMs}ms / 1K messages`);
  console.log();

  const results: BenchmarkResult[] = [];
  let hasRegression = false;

  for (const size of config.sizes) {
    process.stdout.write(`  Benchmarking ${size} messages... `);
    const result = await runBenchmark(size, config.iterations, config.regressionThresholdMs);
    results.push(result);

    const status = result.regression ? "⚠ REGRESSION" : "✓ OK";
    if (result.regression) hasRegression = true;

    console.log(
      `${status} — avg ${result.avgDurationMs.toFixed(1)}ms, ` +
        `${result.msPerThousandMessages.toFixed(1)}ms/1K msgs, ` +
        `reduction ${result.avgReductionPct.toFixed(1)}%`,
    );
  }

  console.log();

  // Summary table
  console.log("┌─────────┬───────────┬────────────┬─────────────┬───────────┬──────────┐");
  console.log("│  Msgs   │  Avg (ms) │  P95 (ms)  │  ms/1K msgs │  Red. %   │  Status  │");
  console.log("├─────────┼───────────┼────────────┼─────────────┼───────────┼──────────┤");

  for (const r of results) {
    const status = r.regression ? "⚠ FAIL" : "  OK  ";
    console.log(
      `│ ${String(r.messageCount).padStart(6)}  │ ${r.avgDurationMs.toFixed(1).padStart(8)}  │ ${r.p95DurationMs.toFixed(1).padStart(9)}  │ ${r.msPerThousandMessages.toFixed(1).padStart(10)}  │ ${r.avgReductionPct.toFixed(1).padStart(8)}  │ ${status} │`,
    );
  }

  console.log("└─────────┴───────────┴────────────┴─────────────┴───────────┴──────────┘");

  // Write JSON report
  const report = {
    timestamp: new Date().toISOString(),
    nodeVersion: process.version,
    config,
    results,
    hasRegression,
  };

  if (config.outputPath) {
    writeFileSync(config.outputPath, JSON.stringify(report, null, 2), "utf-8");
    console.log(`\n📁 Report written to: ${config.outputPath}`);
  } else {
    const defaultPath = join(
      process.cwd(),
      `compact-bench-${new Date().toISOString().replace(/[:.]/g, "-")}.json`,
    );
    writeFileSync(defaultPath, JSON.stringify(report, null, 2), "utf-8");
    console.log(`\n📁 Report written to: ${defaultPath}`);
  }

  if (hasRegression) {
    console.log("\n✗ REGRESSION DETECTED — pipeline performance exceeds threshold");
    process.exitCode = 1;
  } else {
    console.log("\n✓ All benchmarks within acceptable thresholds");
  }
}

main().catch((_err: Error) => {
  process.exitCode = 1;
});
