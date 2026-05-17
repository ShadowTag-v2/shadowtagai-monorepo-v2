/**
 * Autonomous AST Patcher — V25 Pinnacle
 * Reads queued patches from .jules_queue/ and applies them via AST-Grep.
 * Called by the Jules CI workflow and the omega_sync.sh master loop.
 */

import { $ } from "bun";
import { readdirSync, readFileSync } from "fs";

const QUEUE_DIR = ".jules_queue";

interface PatchPayload {
  action: string;
  astRule: string;
  site_id?: string;
  timestamp?: string;
}

async function applyQueuedPatches() {
  let files: string[];
  try {
    files = readdirSync(QUEUE_DIR).filter((f) => f.endsWith(".json"));
  } catch {
    console.log("📭 No .jules_queue/ directory — nothing to patch.");
    return;
  }

  if (files.length === 0) {
    console.log("📭 Patch queue empty — all sites at optimum.");
    return;
  }

  console.log(`🔧 Processing ${files.length} queued AST patches...`);

  for (const patchFile of files) {
    const fullPath = `${QUEUE_DIR}/${patchFile}`;
    try {
      const data: PatchPayload = JSON.parse(readFileSync(fullPath, "utf8"));
      console.log(`  → Applying patch: ${patchFile} (action: ${data.action})`);

      if (data.astRule && data.astRule.includes("AST_REWRITE_RULE:")) {
        // Extract pattern and rewrite from the AST rule string
        const ruleLines = data.astRule.split("\n");
        const patternLine = ruleLines.find((l) => l.startsWith("pattern:"));
        const rewriteLine = ruleLines.find((l) => l.startsWith("rewrite:"));

        if (patternLine && rewriteLine) {
          const pattern = patternLine.replace("pattern:", "").trim();
          const rewrite = rewriteLine.replace("rewrite:", "").trim();

          const result =
            await $`bunx ast-grep run --pattern ${pattern} --rewrite ${rewrite} --update-all apps/`.nothrow();
          if (result.exitCode === 0) {
            console.log(`  ✅ Patch applied: ${patchFile}`);
          } else {
            console.warn(`  ⚠️ AST-grep returned exit ${result.exitCode} for ${patchFile}`);
          }
        } else {
          console.warn(`  ⚠️ Malformed AST rule in ${patchFile}, skipping.`);
        }
      } else {
        console.log(`  ℹ️ No actionable AST rule in ${patchFile}, archiving.`);
      }

      // Archive processed patch (immutable infrastructure — no delete)
      const archiveDir = `${QUEUE_DIR}/_processed`;
      await $`mkdir -p ${archiveDir}`.nothrow();
      await $`mv ${fullPath} ${archiveDir}/${patchFile}`.nothrow();
    } catch (err) {
      console.error(`  ❌ Failed to process ${patchFile}:`, err);
    }
  }

  console.log("✅ All queued patches processed.");
}

if (import.meta.main) {
  applyQueuedPatches();
}
