#!/usr/bin/env node
/**
 * Security Auto-Fix Runner (Codemender-style)
 *
 * Attempts safe, minimal fixes for known vulnerabilities:
 * - npm audit fix (conservative)
 * - pip-audit --fix
 * - Update lock files
 *
 * Sets HAS_CHANGES=true in GITHUB_ENV if changes were made.
 */

import { execSync } from "node:child_process";
import fs from "node:fs";

let hasChanges = false;

function tryRun(cmd, description) {
  try {
    console.log(`🔧 ${description}...`);
    execSync(cmd, { stdio: "inherit" });
    hasChanges = true;
    return true;
  } catch (error) {
    console.log(`   ⚠️ Failed (continuing): ${error.message}`);
    return false;
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
  console.log("🛠️  Running security auto-fix...\n");

  // Node.js fixes
  if (fileExists("package.json")) {
    console.log("📦 Node.js security fixes:");

    // Conservative: only patch/minor bumps, no breaking changes
    tryRun("npm audit fix --only=prod --force=false", "npm audit fix (conservative)");

    // Refresh lock file if it exists
    if (fileExists("package-lock.json")) {
      tryRun("npm install", "Refresh package-lock.json");
    }
  }

  // Python fixes
  if (fileExists("requirements.txt")) {
    console.log("\n🐍 Python security fixes:");

    // pip-audit can auto-fix some vulnerabilities
    tryRun("pip-audit --fix || true", "pip-audit --fix");

    // Optionally: pin known vulnerable packages
    // (In practice, you'd parse pip-audit output and update requirements.txt)
  }

  // Write environment variable for CI
  const envFile = process.env.GITHUB_ENV || ".ci/env.tmp";
  const envValue = `HAS_CHANGES=${hasChanges}\n`;

  fs.appendFileSync(envFile, envValue);
  process.stdout.write(envValue);

  if (hasChanges) {
    console.log("\n✅ Auto-fix applied changes");
    console.log("   Review with: git diff");
  } else {
    console.log("\n✓ No auto-fixable issues found");
  }
}

main().catch((error) => {
  console.error("Auto-fix error:", error);
  process.exit(1);
});
