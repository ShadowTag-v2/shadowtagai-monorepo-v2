#!/usr/bin/env node
/**
 * HYPERAGENT STEALTH VALIDATION TEST
 * ===================================
 * Tests: Bot detection, latency, extraction accuracy
 *
 * REQUIREMENTS:
 *   export GEMINI_API_KEY="your-key"  # or GOOGLE_API_KEY
 *   # OR
 *   export OPENAI_API_KEY="your-key"
 *   # OR
 *   export ANTHROPIC_API_KEY="your-key"
 *
 * USAGE:
 *   node hyperagent-stealth-test.js
 *
 * COST ESTIMATE:
 *   ~$0.01-0.05 per test run (depends on LLM)
 */

const { HyperAgent } = require("@hyperbrowser/agent");

// Determine which provider to use based on available env vars
function getLLMConfig() {
  if (process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY) {
    return {
      provider: "gemini",
      model: "gemini-2.0-flash-exp", // Cheapest, fastest
      apiKey: process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY,
    };
  }
  if (process.env.OPENAI_API_KEY) {
    return {
      provider: "openai",
      model: "gpt-4o-mini", // Cheapest OpenAI
      apiKey: process.env.OPENAI_API_KEY,
    };
  }
  if (process.env.ANTHROPIC_API_KEY) {
    return {
      provider: "anthropic",
      model: "claude-3-haiku-20240307", // Cheapest Claude
      apiKey: process.env.ANTHROPIC_API_KEY,
    };
  }
  throw new Error("No LLM API key found. Set GEMINI_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY");
}

async function runTests() {
  const llmConfig = getLLMConfig();
  console.log(`\n═══════════════════════════════════════════════════════════════`);
  console.log(`  HYPERAGENT STEALTH TEST`);
  console.log(`  Provider: ${llmConfig.provider} | Model: ${llmConfig.model}`);
  console.log(`═══════════════════════════════════════════════════════════════\n`);

  const agent = new HyperAgent({
    llm: llmConfig,
    // Local browser - no Hyperbrowser cloud
  });

  const results = {
    tests: [],
    totalTime: 0,
    passed: 0,
    failed: 0,
  };

  try {
    // ─────────────────────────────────────────────────────────────
    // TEST 1: Bot Detection (SannySoft)
    // ─────────────────────────────────────────────────────────────
    console.log("[TEST 1] Bot Detection Check (bot.sannysoft.com)...");
    const t1Start = Date.now();

    const botTest = await agent.executeTask(
      "Go to https://bot.sannysoft.com and wait for tests to complete. " +
        "Return a JSON object with keys 'passed' and 'failed', each containing " +
        "an array of test names that passed or failed.",
    );

    const t1Time = Date.now() - t1Start;
    results.tests.push({
      name: "Bot Detection",
      time: t1Time,
      result: botTest.output || botTest,
    });
    console.log(`  ✓ Completed in ${t1Time}ms\n`);

    // ─────────────────────────────────────────────────────────────
    // TEST 2: Structured Extraction
    // ─────────────────────────────────────────────────────────────
    console.log("[TEST 2] Structured Data Extraction (Hacker News)...");
    const t2Start = Date.now();

    const page = await agent.newPage();
    await page.goto("https://news.ycombinator.com");

    const hnData = await page.extract(
      "Extract the top 5 story titles and their point counts as JSON array",
    );

    const t2Time = Date.now() - t2Start;
    results.tests.push({
      name: "Data Extraction",
      time: t2Time,
      result: hnData.output || hnData,
    });
    console.log(`  ✓ Completed in ${t2Time}ms\n`);

    // ─────────────────────────────────────────────────────────────
    // TEST 3: Multi-Step Task
    // ─────────────────────────────────────────────────────────────
    console.log("[TEST 3] Multi-Step Navigation...");
    const t3Start = Date.now();

    const multiStep = await agent.executeTask(
      "Go to https://example.com, click the 'More information...' link, " +
        "and tell me what domain the link points to.",
    );

    const t3Time = Date.now() - t3Start;
    results.tests.push({
      name: "Multi-Step",
      time: t3Time,
      result: multiStep.output || multiStep,
    });
    console.log(`  ✓ Completed in ${t3Time}ms\n`);

    // ─────────────────────────────────────────────────────────────
    // SUMMARY
    // ─────────────────────────────────────────────────────────────
    results.totalTime = results.tests.reduce((a, t) => a + t.time, 0);

    console.log(`═══════════════════════════════════════════════════════════════`);
    console.log(`  RESULTS SUMMARY`);
    console.log(`═══════════════════════════════════════════════════════════════`);
    console.log(`  Total Time: ${results.totalTime}ms (${(results.totalTime / 1000).toFixed(1)}s)`);
    console.log(`  Avg per Task: ${Math.round(results.totalTime / results.tests.length)}ms`);
    console.log(`───────────────────────────────────────────────────────────────`);

    results.tests.forEach((t, i) => {
      console.log(`\n  [${i + 1}] ${t.name} (${t.time}ms):`);
      const output =
        typeof t.result === "string"
          ? t.result.substring(0, 500)
          : JSON.stringify(t.result, null, 2).substring(0, 500);
      console.log(`      ${output.replace(/\n/g, "\n      ")}`);
    });

    console.log(`\n═══════════════════════════════════════════════════════════════`);
    console.log(`  VERDICT`);
    console.log(`═══════════════════════════════════════════════════════════════`);

    const avgTime = results.totalTime / results.tests.length;
    if (avgTime < 5000) {
      console.log(`  ⚡ FAST: Avg ${Math.round(avgTime)}ms per task`);
    } else if (avgTime < 15000) {
      console.log(`  ⏱️  ACCEPTABLE: Avg ${Math.round(avgTime)}ms per task`);
    } else {
      console.log(`  🐢 SLOW: Avg ${Math.round(avgTime)}ms per task (LLM latency?)`);
    }

    console.log(`\n  Suitable for: Scraping, QA, Data Collection`);
    console.log(`  NOT for: Real-time (<100ms), Judge #6 SLA paths`);
    console.log(`═══════════════════════════════════════════════════════════════\n`);
  } catch (error) {
    console.error("\n❌ TEST FAILED:", error.message);
    console.error(error.stack);
  } finally {
    await agent.closeAgent();
  }

  return results;
}

// Run if called directly
if (require.main === module) {
  runTests()
    .then(() => process.exit(0))
    .catch((e) => {
      console.error(e);
      process.exit(1);
    });
}

module.exports = { runTests };
