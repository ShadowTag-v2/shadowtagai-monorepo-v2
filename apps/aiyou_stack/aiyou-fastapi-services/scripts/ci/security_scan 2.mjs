#!/usr/bin/env node
/**
 * Security Scan Runner
 *
 * Runs multiple security scanners (npm audit, pip-audit, Semgrep, Bandit)
 * and collects results into a unified JSON output.
 */

import { execSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const RESULTS = [];

function run(cmd, opts = {}) {
  try {
    const result = execSync(cmd, {
      stdio: "pipe",
      encoding: "utf8",
      ...opts,
    });
    RESULTS.push({ cmd, ok: true, output: result });
    return result;
  } catch (error) {
    const output = error.stdout || error.stderr || error.message;
    RESULTS.push({ cmd, ok: false, output });
    return output;
  }
}

function fileExists(filePath) {
  try {
    fs.accessSync(filePath);
    return true;
  } catch {
    return false;
  }
}

async function main() {
  console.log("🔒 Running security scans...\n");

  const hasNode = fileExists("package.json");
  const hasPython = fileExists("requirements.txt") || fileExists("pyproject.toml");

  // Ensure output directory
  fs.mkdirSync(".ci", { recursive: true });

  // Node.js scans
  if (hasNode) {
    console.log("📦 Scanning Node.js dependencies...");
    run("npm audit --json > .ci/npm-audit.json 2>&1 || true");
    run("npx semgrep scan --config=auto --json > .ci/semgrep.json 2>&1 || true");
  }

  // Python scans
  if (hasPython) {
    console.log("🐍 Scanning Python dependencies...");
    run("pip-audit -f json > .ci/pip-audit.json 2>&1 || true");
    run("safety check --json > .ci/safety.json 2>&1 || true");
    run("bandit -r . -f json -o .ci/bandit.json 2>&1 || true");
  }

  // Write combined results
  const outputPath = ".ci/security_scan.json";
  fs.writeFileSync(outputPath, JSON.stringify(RESULTS, null, 2));

  console.log(`\n✅ Security scan complete`);
  console.log(`   Results: ${outputPath}`);

  // Extract high-severity issues for summary
  const issues = [];
  RESULTS.forEach((res) => {
    const lines = (res.output || "").split("\n");
    lines.forEach((line) => {
      if (/critical|high|CVE|ERROR|VULNERABILITY/i.test(line)) {
        issues.push(line.trim());
      }
    });
  });

  if (issues.length > 0) {
    console.log(`\n⚠️  High-severity issues found (${issues.length}):`);
    issues.slice(0, 10).forEach((issue) => console.log(`   - ${issue}`));
    if (issues.length > 10) {
      console.log(`   ... and ${issues.length - 10} more`);
    }
  } else {
    console.log("\n✓ No high-severity issues detected");
  }
}

main().catch((error) => {
  console.error("Security scan error:", error);
  process.exit(1);
});
