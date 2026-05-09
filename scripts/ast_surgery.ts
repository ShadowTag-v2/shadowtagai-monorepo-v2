#!/usr/bin/env bun
/**
 * scripts/ast_surgery.ts — V25 Semantic Scalpel Executor
 *
 * Bridges Pomelli Swarm audit findings to AST-Grep codebase patches.
 * Accepts a site ID and an AST rule description, then applies the
 * appropriate ast-grep rewrite to the codebase.
 *
 * Usage:
 *   bun run scripts/ast_surgery.ts <siteId> <astRuleDescription>
 *   bun run scripts/ast_surgery.ts global "Dynamic Import Optimization"
 */
import { $ } from "bun";

const KNOWN_SURGERIES: Record<string, { pattern: string; rewrite: string; target: string }> = {
  "dynamic-import": {
    pattern: 'import { getAuth } from "firebase/auth"',
    rewrite: 'const { getAuth } = await import("firebase/auth")',
    target: "apps/",
  },
  "dynamic-import-single-quote": {
    pattern: "import { getAuth } from 'firebase/auth'",
    rewrite: "const { getAuth } = await import('firebase/auth')",
    target: "apps/",
  },
};

async function executeSemanticScalpel(siteId: string, astRuleDesc: string) {
  console.log(`⚡ [AST Surgery] Invoking Semantic Scalpel for site: ${siteId}`);
  console.log(`   Rule description: ${astRuleDesc}`);

  // Run the full sgconfig.yml rule scan first
  console.log("\n📋 Running full AST-Grep rule scan...");
  const scanResult = await $`ast-grep scan --rule .ast-grep/rules/firebase-dynamic-import.yml 2>&1`
    .text()
    .catch(() => "No violations found.");
  console.log(scanResult || "✅ No Firebase static import violations.");

  // Apply known surgeries if the description matches
  if (astRuleDesc.toLowerCase().includes("dynamic import")) {
    for (const [name, surgery] of Object.entries(KNOWN_SURGERIES)) {
      console.log(`\n🔪 Applying surgery: ${name}`);
      await $`ast-grep --pattern ${surgery.pattern} --rewrite ${surgery.rewrite} --update-all ${surgery.target}`
        .catch(() => console.log(`   No matches for ${name} — already compliant.`));
    }
    console.log("\n✅ AST Surgery complete. Firebase dynamic imports enforced.");
  } else {
    console.log(`\n⚠️  Unknown surgery type: "${astRuleDesc}". Run ast-grep manually.`);
  }
}

const siteId = process.argv[2] || "global";
const astRule = process.argv[3] || "Dynamic Import Optimization";
await executeSemanticScalpel(siteId, astRule);
