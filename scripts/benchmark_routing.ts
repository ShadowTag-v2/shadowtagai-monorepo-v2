/**
 * V23 Task 8: Benchmark auto_route() latency
 * Target: < 5ms keyword, < 20ms semantic
 */

import { autoRoute } from "../tools/cognitive_router/dispatch";
import { setRuntimeOverride, clearRuntimeOverrides } from "../config/feature_flags";

const ITERATIONS = 500;
const WARM_UP = 10;

async function benchmarkKeywordRouting(): Promise<number> {
  // Warm up
  for (let i = 0; i < WARM_UP; i++) {
    await autoRoute("deploy the service");
  }

  const start = performance.now();
  for (let i = 0; i < ITERATIONS; i++) {
    await autoRoute("deploy the service");
  }
  return (performance.now() - start) / ITERATIONS;
}

async function benchmarkSemanticRouting(): Promise<number> {
  setRuntimeOverride("SEMANTIC_ROUTING", true);

  // Warm up
  for (let i = 0; i < WARM_UP; i++) {
    await autoRoute("what should I do about the complex database issue");
  }

  const start = performance.now();
  for (let i = 0; i < ITERATIONS; i++) {
    await autoRoute("what should I do about the complex database issue");
  }
  const avg = (performance.now() - start) / ITERATIONS;
  clearRuntimeOverrides();
  return avg;
}

export async function benchmarkAutoRouting() {
  console.log(`⚡ [Benchmark] Running ${ITERATIONS} iterations...`);

  const keywordMs = await benchmarkKeywordRouting();
  const semanticMs = await benchmarkSemanticRouting();

  console.log(`⚡ [Benchmark] Keyword routing:  ${keywordMs.toFixed(3)}ms avg (target: <5ms)`);
  console.log(`⚡ [Benchmark] Semantic routing: ${semanticMs.toFixed(3)}ms avg (target: <20ms)`);

  const keywordPass = keywordMs < 5;
  const semanticPass = semanticMs < 20;

  console.log(`⚡ [Benchmark] Keyword:  ${keywordPass ? "✅ PASS" : "❌ FAIL"}`);
  console.log(`⚡ [Benchmark] Semantic: ${semanticPass ? "✅ PASS" : "❌ FAIL"}`);

  return { keywordMs, semanticMs, keywordPass, semanticPass };
}

if (import.meta.main) {
  await benchmarkAutoRouting();
}
