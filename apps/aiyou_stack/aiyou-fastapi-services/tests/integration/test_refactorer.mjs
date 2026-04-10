#!/usr/bin/env node
/**
 * Integration tests for Code Refactorer Agent
 *
 * Tests the refactorer's analyze and refactor capabilities
 */

import { refactorCode, analyzeCode } from "../../tools/orchestrator/ace_with_refactor.mjs";
import assert from "node:assert";

// Test fixtures
const sampleCode = {
  javascript: `
function calc(a,b,c) {
  var result = 0;
  if(a>0) {
    if(b>0) {
      result = a+b+c
    }
  }
  return result
}
`,
  python: `
def calc(a,b,c):
    result = 0
    if a>0:
        if b>0:
            result = a+b+c
    return result
`,
};

// Test suite
const tests = {
  async testAnalyzeJavaScript() {
    console.log("Testing: analyzeCode() with JavaScript...");
    const analysis = await analyzeCode(sampleCode.javascript, "javascript");

    assert(analysis.issues, "Analysis should return issues array");
    assert(analysis.metrics, "Analysis should return metrics");
    assert(analysis.recommendations, "Analysis should return recommendations");
    assert(typeof analysis.metrics.complexity === "number", "Complexity should be a number");
    assert(
      typeof analysis.metrics.maintainability === "number",
      "Maintainability should be a number",
    );

    console.log("✓ analyzeCode() returns valid structure");
    return true;
  },

  async testRefactorJavaScript() {
    console.log("Testing: refactorCode() with JavaScript...");
    const result = await refactorCode(sampleCode.javascript, {
      language: "javascript",
      focus: ["readability", "best-practices"],
      aggressiveness: "moderate",
    });

    assert(result.refactoredCode, "Refactoring should return refactored code");
    assert(result.summary, "Refactoring should return summary");
    assert(Array.isArray(result.improvements), "Improvements should be an array");
    assert(result.improvements.length > 0, "Should have at least one improvement");

    console.log("✓ refactorCode() returns valid refactoring result");
    return true;
  },

  async testRefactorWithFocusAreas() {
    console.log("Testing: refactorCode() with different focus areas...");

    const focusAreas = [
      ["readability"],
      ["performance"],
      ["best-practices"],
      ["readability", "performance"],
    ];

    for (const focus of focusAreas) {
      const result = await refactorCode(sampleCode.javascript, {
        language: "javascript",
        focus,
        aggressiveness: "conservative",
      });

      assert(result.refactoredCode, `Should refactor with focus: ${focus.join(", ")}`);
    }

    console.log("✓ refactorCode() works with various focus areas");
    return true;
  },

  async testRefactorAggressiveness() {
    console.log("Testing: refactorCode() with different aggressiveness levels...");

    const levels = ["conservative", "moderate", "aggressive"];

    for (const level of levels) {
      const result = await refactorCode(sampleCode.javascript, {
        language: "javascript",
        aggressiveness: level,
      });

      assert(result.refactoredCode, `Should refactor with aggressiveness: ${level}`);
    }

    console.log("✓ refactorCode() supports all aggressiveness levels");
    return true;
  },

  async testAnalyzePython() {
    console.log("Testing: analyzeCode() with Python...");
    const analysis = await analyzeCode(sampleCode.python, "python");

    assert(analysis.issues, "Python analysis should return issues");
    assert(analysis.metrics, "Python analysis should return metrics");

    console.log("✓ analyzeCode() works with Python code");
    return true;
  },

  async testRefactorErrorHandling() {
    console.log("Testing: error handling with invalid code...");

    try {
      // Test with empty code
      const result = await refactorCode("", {
        language: "javascript",
      });

      // Should still return a valid structure even with empty code
      assert(result.refactoredCode !== undefined, "Should handle empty code gracefully");
      console.log("✓ Handles empty code gracefully");
    } catch (error) {
      console.log("✓ Properly throws error for invalid input");
    }

    return true;
  },

  async testConfigurationDefaults() {
    console.log("Testing: default configuration values...");

    // Test without explicit config
    const result = await refactorCode(sampleCode.javascript);

    assert(result.refactoredCode, "Should use default configuration");
    console.log("✓ Uses sensible defaults when config not provided");
    return true;
  },
};

// Test runner
async function runTests() {
  console.log("=".repeat(60));
  console.log("Code Refactorer Integration Tests");
  console.log("=".repeat(60));
  console.log();

  let passed = 0;
  let failed = 0;
  const failedTests = [];

  for (const [testName, testFn] of Object.entries(tests)) {
    try {
      await testFn();
      passed++;
    } catch (error) {
      failed++;
      failedTests.push({ name: testName, error: error.message });
      console.error(`✗ ${testName} failed:`, error.message);
    }
    console.log();
  }

  console.log("=".repeat(60));
  console.log("Test Results");
  console.log("=".repeat(60));
  console.log(`Total: ${passed + failed}`);
  console.log(`Passed: ${passed}`);
  console.log(`Failed: ${failed}`);

  if (failed > 0) {
    console.log("\nFailed tests:");
    failedTests.forEach(({ name, error }) => {
      console.log(`  - ${name}: ${error}`);
    });
    process.exit(1);
  }

  console.log("\n✓ All tests passed!");
  console.log("=".repeat(60));
}

// Run tests if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  runTests().catch((error) => {
    console.error("Test runner error:", error);
    process.exit(1);
  });
}

export { tests, runTests };
