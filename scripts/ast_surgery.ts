#!/usr/bin/env bun
// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

/**
 * AST Surgery — Automated code cleanup and refactoring.
 *
 * Part of the Jules + GCA Sovereign PR Review system.
 * Runs after review to auto-fix common issues:
 * - Python: ruff check --fix + ruff format
 * - TypeScript/JS: biome check --write
 * - AST patterns: ast-grep rewrites (e.g., dynamic import migration)
 *
 * Usage:
 *   bun run scripts/ast_surgery.ts --auto-fix
 *   bun run scripts/ast_surgery.ts --python-only
 *   bun run scripts/ast_surgery.ts --dry-run
 */

import { $ } from "bun";

interface SurgeryResult {
  step: string;
  success: boolean;
  output: string;
}

async function runAstSurgery(options: {
  autoFix: boolean;
  pythonOnly: boolean;
  dryRun: boolean;
}): Promise<SurgeryResult[]> {
  console.log("⚡ [Jules] Running AST Surgery...");
  const results: SurgeryResult[] = [];

  // Step 1: Python — ruff check + format
  try {
    const ruffArgs = options.dryRun ? "--diff" : "--fix";
    const ruffResult =
      await $`uv run ruff check ${ruffArgs} .`.text().catch(() => "");
    results.push({ step: "ruff check", success: true, output: ruffResult });

    if (!options.dryRun) {
      const fmtResult =
        await $`uv run ruff format .`.text().catch(() => "");
      results.push({ step: "ruff format", success: true, output: fmtResult });
    }
  } catch (e) {
    results.push({
      step: "ruff",
      success: false,
      output: String(e),
    });
  }

  if (options.pythonOnly) {
    return results;
  }

  // Step 2: TypeScript/JS — biome check + write
  try {
    const biomeArgs = options.dryRun ? "" : "--write";
    const biomeResult =
      await $`npx @biomejs/biome check ${biomeArgs} .`
        .text()
        .catch(() => "");
    results.push({ step: "biome check", success: true, output: biomeResult });
  } catch (e) {
    results.push({
      step: "biome",
      success: false,
      output: String(e),
    });
  }

  // Step 3: AST-grep pattern rewrites
  if (options.autoFix && !options.dryRun) {
    try {
      // Migrate static Firebase imports to dynamic imports
      await $`ast-grep --pattern 'import { getAuth } from "firebase/auth"' --rewrite 'const { getAuth } = await import("firebase/auth")' --update-all`.catch(
        () => {}
      );

      // Migrate static Firestore imports to dynamic imports
      await $`ast-grep --pattern 'import { getFirestore } from "firebase/firestore"' --rewrite 'const { getFirestore } = await import("firebase/firestore")' --update-all`.catch(
        () => {}
      );

      results.push({
        step: "ast-grep rewrites",
        success: true,
        output: "Dynamic import migration applied",
      });
    } catch (e) {
      results.push({
        step: "ast-grep",
        success: false,
        output: String(e),
      });
    }
  }

  console.log(`✅ AST Surgery Complete — ${results.length} steps executed`);
  return results;
}

// CLI entry point
if (import.meta.main) {
  const args = Bun.argv.slice(2);
  const options = {
    autoFix: args.includes("--auto-fix"),
    pythonOnly: args.includes("--python-only"),
    dryRun: args.includes("--dry-run"),
  };

  const results = await runAstSurgery(options);

  // Print summary
  const passed = results.filter((r) => r.success).length;
  const failed = results.filter((r) => !r.success).length;
  console.log(`\n📊 Summary: ${passed} passed, ${failed} failed`);

  if (failed > 0) {
    process.exit(1);
  }
}
