/**
 * Demo widget - Complete end-to-end demonstration
 * Shows: request → governance → routing → patch → apply
 */

import * as fs from "node:fs/promises";
import * as path from "node:path";
import { createGovernance } from "./core/governance.js";
import { createPatcher } from "./core/patcher.js";
import { CopilotRouter } from "./core/router.js";
import type { CopilotRequest, RouterConfig } from "./core/schema.js";

async function main() {
  console.log("🚀 Universal Copilot Demo\n");
  console.log("=".repeat(60));

  // Configuration
  const useMock = process.env.USE_MOCK === "1";
  const enableGovernance = process.env.ENABLE_GOVERNANCE !== "0";

  const config: RouterConfig = {
    defaultProvider: useMock ? "mock" : "auto",
    enableGovernance,
    corInstanceId: process.env.COR_INSTANCE_ID || "copilot-demo",
    rateLimitRps: 6.6,
    rateLimitConcurrent: 2,
    providers: {
      mock: {},
      openai: {
        apiKey: process.env.OPENAI_API_KEY,
        model: "gpt-4o-2024-08-06",
      },
      anthropic: {
        apiKey: process.env.ANTHROPIC_API_KEY,
        model: "claude-sonnet-4-20250514",
      },
    },
  };

  // Initialize router with governance
  const governance = enableGovernance ? createGovernance(useMock) : undefined;
  const router = new CopilotRouter(config, governance);
  const patcher = createPatcher();

  console.log("\nConfiguration:");
  console.log(`  Provider: ${config.defaultProvider}`);
  console.log(`  Governance: ${enableGovernance ? "enabled" : "disabled"}`);
  console.log(`  Available providers: ${router.getAvailableProviders().join(", ")}`);
  console.log("=".repeat(60) + "\n");

  // Test file
  const testFile = path.join(process.cwd(), "tests", "fixtures", "sample.ts");

  // Ensure fixtures directory exists
  await fs.mkdir(path.dirname(testFile), { recursive: true });

  // Create sample file if it doesn't exist
  const sampleCode = `export function calculateTotal(items: number[]): number {
  let total = 0;
  for (let i = 0; i < items.length; i++) {
    total += items[i];
  }
  return total;
}`;

  try {
    await fs.access(testFile);
  } catch {
    await fs.writeFile(testFile, sampleCode, "utf-8");
    console.log(`Created test file: ${testFile}\n`);
  }

  // Read current code
  const currentCode = await fs.readFile(testFile, "utf-8");

  // Create request
  const request: CopilotRequest = {
    selection: {
      filePath: testFile,
      language: "typescript",
      code: currentCode,
    },
    intent: "optimize",
    modelPref: config.defaultProvider,
    maxTokens: 800,
    temperature: 0.2,
  };

  console.log("Request:");
  console.log(`  File: ${request.selection.filePath}`);
  console.log(`  Intent: ${request.intent}`);
  console.log(`  Language: ${request.selection.language}`);
  console.log(`\nOriginal code:\n${currentCode}\n`);
  console.log("=".repeat(60));

  try {
    // Route request
    console.log("\n⚙️  Processing request...\n");
    const response = await router.route(request);

    console.log("Response:");
    console.log(`  Provider: ${response.provider}`);
    console.log(`  Latency: ${response.latencyMs}ms`);
    console.log(`  Tokens: ${response.tokensUsed}`);

    if (response.governanceDecision) {
      console.log(`\nGovernance Decision:`);
      console.log(`  Approved: ${response.governanceDecision.approved}`);
      console.log(`  Risk Level: ${response.governanceDecision.riskLevel}`);
    }

    if (response.patch.explanation) {
      console.log(`\nExplanation: ${response.patch.explanation}`);
    }

    console.log(`\nUnified Diff:\n${response.patch.unifiedDiff}\n`);
    console.log("=".repeat(60));

    // Apply patch (dry run first)
    console.log("\n📝 Applying patch (dry run)...\n");
    const dryRunResult = await patcher.applyPatch(
      response.patch.filePath,
      response.patch.unifiedDiff,
      { dryRun: true, createBackup: false },
    );

    if (dryRunResult.success) {
      console.log(`✅ Dry run successful: ${dryRunResult.linesChanged} lines would change`);

      // Apply for real
      console.log("\n📝 Applying patch...\n");
      const result = await patcher.applyPatch(response.patch.filePath, response.patch.unifiedDiff, {
        createBackup: true,
      });

      if (result.success) {
        console.log(`✅ Patch applied successfully!`);
        console.log(`   Lines changed: ${result.linesChanged}`);
        if (result.backup) {
          console.log(`   Backup created: ${result.backup}`);
        }

        // Show new code
        const newCode = await fs.readFile(testFile, "utf-8");
        console.log(`\nNew code:\n${newCode}\n`);
      } else {
        console.error(`❌ Failed to apply patch: ${result.error}`);
      }
    } else {
      console.error(`❌ Dry run failed: ${dryRunResult.error}`);
    }

    // Show statistics
    console.log("=".repeat(60));
    console.log("\nRouter Statistics:");
    const stats = router.getStats();
    console.log(`  Total requests: ${stats.totalRequests}`);
    console.log(`  Successful: ${stats.successfulRequests}`);
    console.log(`  Failed: ${stats.failedRequests}`);
    console.log(`  Governance rejections: ${stats.governanceRejections}`);
    console.log(`  Average latency: ${Math.round(stats.averageLatencyMs)}ms`);
    console.log(`  Provider usage:`, stats.providerUsage);
  } catch (error: unknown) {
    console.error("\n❌ Error:", error.message);
    if (error.code) {
      console.error(`   Code: ${error.code}`);
    }
    if (error.retryable) {
      console.error(`   Retryable: yes`);
    }
    process.exit(1);
  }

  console.log("\n" + "=".repeat(60));
  console.log("✨ Demo complete!");
}

// Run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    console.error("Fatal error:", error);
    process.exit(1);
  });
}

export { main };
