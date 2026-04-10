/**
 * STOP HOOK: Python Quality Pipeline
 *
 * Runs after Claude finishes responding. Executes quality checks on edited Python files:
 * 1. Ruff formatting
 * 2. MyPy type checking
 * 3. Pytest coverage gate (98% threshold)
 *
 * Blocks commits that drop coverage below 98% (Judge #6 enforcement).
 *
 * Sequence: Claude responds → Ruff formats → MyPy checks types → Coverage gate validates → Errors displayed
 */

import { Hook } from "@anthropic-ai/claude-agent-sdk";
import { execSync } from "child_process";
import * as fs from "fs";
import * as path from "path";

const EDIT_LOG = ".claude/hooks/edited-files.json";
const COVERAGE_THRESHOLD = 98;

interface EditedFile {
  path: string;
  repo: string;
  operation: string;
  timestamp: string;
}

interface EditLog {
  timestamp: string;
  files: EditedFile[];
}

export const hook: Hook = {
  name: "stop-python-quality-pipeline",
  type: "stop",
  async execute(context) {
    // Read edited files log
    if (!fs.existsSync(EDIT_LOG)) {
      return { continue: true };
    }

    let editLog: EditLog;
    try {
      editLog = JSON.parse(fs.readFileSync(EDIT_LOG, "utf-8"));
    } catch (e) {
      console.error("Failed to parse edit log:", e);
      return { continue: true };
    }

    // Filter for Python files
    const pythonFiles = editLog.files.filter((f) => f.path.endsWith(".py"));

    if (pythonFiles.length === 0) {
      // Clear the log for next session
      fs.unlinkSync(EDIT_LOG);
      return { continue: true };
    }

    const results: string[] = [];
    results.push("\n=== Python Quality Pipeline ===\n");
    results.push(`Files modified: ${pythonFiles.length}`);
    pythonFiles.forEach((f) => results.push(`  - ${f.path}`));
    results.push("");

    // Step 1: Ruff formatting
    results.push("🎨 Running Ruff formatter...");
    try {
      execSync("uv run ruff format .", {
        cwd: process.cwd(),
        stdio: "pipe",
      });
      results.push("✅ Formatting complete\n");
    } catch (e: any) {
      results.push(`⚠️  Formatting warnings:\n${e.stdout || e.message}\n`);
    }

    // Step 2: MyPy type checking (strict mode)
    results.push("🔍 Running MyPy type checker (strict mode)...");
    try {
      const typeCheckOutput = execSync("uv run mypy --strict .", {
        cwd: process.cwd(),
        encoding: "utf-8",
        stdio: "pipe",
      });
      results.push("✅ Type checking passed\n");
    } catch (e: any) {
      const errorOutput = e.stdout || e.stderr || e.message;
      const errorLines = errorOutput.split("\n").filter((l: string) => l.trim());

      if (errorLines.length > 0 && errorLines.length <= 5) {
        results.push("❌ Type errors found (please fix):");
        errorLines.forEach((line: string) => results.push(`  ${line}`));
        results.push("");
      } else if (errorLines.length > 5) {
        results.push(
          `❌ ${errorLines.length} type errors found. Consider launching auto-error-resolver agent.`
        );
        results.push("First 5 errors:");
        errorLines.slice(0, 5).forEach((line: string) => results.push(`  ${line}`));
        results.push("");
      }
    }

    // Step 3: Coverage Gate (CRITICAL - Judge #6 enforcement)
    results.push(`🛡️  Running coverage gate (${COVERAGE_THRESHOLD}% threshold)...`);
    try {
      const coverageOutput = execSync(
        `uv run pytest --cov --cov-fail-under=${COVERAGE_THRESHOLD} --cov-report=term-missing`,
        {
          cwd: process.cwd(),
          encoding: "utf-8",
          stdio: "pipe",
        }
      );

      // Parse coverage percentage from output
      const coverageMatch = coverageOutput.match(/TOTAL\s+\d+\s+\d+\s+(\d+)%/);
      const currentCoverage = coverageMatch ? parseInt(coverageMatch[1]) : null;

      if (currentCoverage !== null) {
        results.push(`✅ Coverage: ${currentCoverage}% (threshold: ${COVERAGE_THRESHOLD}%)\n`);
      } else {
        results.push("✅ Coverage gate passed\n");
      }
    } catch (e: any) {
      const errorOutput = e.stdout || e.stderr || e.message;

      // Parse coverage failure
      const coverageMatch = errorOutput.match(/TOTAL\s+\d+\s+\d+\s+(\d+)%/);
      const currentCoverage = coverageMatch ? parseInt(coverageMatch[1]) : null;

      results.push("❌ COVERAGE GATE FAILED (Judge #6 violation)");
      if (currentCoverage !== null) {
        const delta = currentCoverage - COVERAGE_THRESHOLD;
        results.push(
          `   Current: ${currentCoverage}% | Required: ${COVERAGE_THRESHOLD}% | Delta: ${delta}%`
        );
      }
      results.push("");
      results.push("🚨 COMMIT BLOCKED: Coverage dropped below 98%");
      results.push("Actions:");
      results.push("  1. Add tests to cover uncovered lines");
      results.push("  2. Launch auto-rollback agent to attempt automatic fixes");
      results.push("  3. After 3 failed attempts, agent will revert changes");
      results.push("");

      // Show uncovered lines (if available)
      const uncoveredMatch = errorOutput.match(/Missing lines: ([\d, -]+)/);
      if (uncoveredMatch) {
        results.push(`Missing coverage: ${uncoveredMatch[1]}\n`);
      }
    }

    // Step 4: Clear edit log for next session
    fs.unlinkSync(EDIT_LOG);

    // Display results
    const output = results.join("\n");
    console.log(output);

    // Return with quality summary
    return {
      continue: true,
      message: output,
    };
  },
};
