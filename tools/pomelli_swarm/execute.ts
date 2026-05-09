/**
 * V23 Pomelli Swarm Executor
 * Task 18: NotebookLM + Pomelli integration for autonomous web auditing.
 * Queries NotebookLM for brand guidelines, then dispatches swarm across targets.
 *
 * Uses the `nlm` binary (notebooklm-mcp-cli, installed via uv) for direct
 * NotebookLM MCP queries. Falls back to hardcoded ground truth on failure.
 */

import { $ } from "bun";
import { POMELLI_TARGET_MATRIX, type SwarmTarget } from "./targets";

const GROUND_TRUTH_FALLBACK =
  "NOTEBOOK_TRUTH: P100 Lighthouse strictly enforced. Dynamic Firebase imports via initAuthManager(app) only. HSTS preload mandatory. reCAPTCHA Enterprise for App Check. Zero third-party cookies on initial load.";

/**
 * Query NotebookLM via the `nlm` CLI binary.
 * Protocol: nlm → stdio MCP → NotebookLM API → grounded response.
 * Gracefully degrades to GROUND_TRUTH_FALLBACK if nlm is unavailable.
 */
async function queryNotebookLM(query: string): Promise<string> {
  console.log(`🧠 [NotebookLM] Querying via nlm binary: "${query}"`);
  try {
    // nlm is installed at /opt/homebrew/bin/nlm via `uv tool install notebooklm-mcp-cli`
    // The correct invocation is `nlm query "<prompt>"` — NOT the old broken
    // `uvx --from notebooklm-mcp-cli notebooklm-mcp query` which was a phantom subcommand.
    const result = await $`nlm query ${query}`.timeout(15_000).text();
    const trimmed = result.trim();
    return trimmed || GROUND_TRUTH_FALLBACK;
  } catch (err) {
    console.warn(`⚠️ nlm query failed, using ground truth fallback. Error: ${err}`);
    return GROUND_TRUTH_FALLBACK;
  }
}

interface AuditResult {
  target: SwarmTarget;
  brandGuidelines: string;
  optimizations: string[];
  patchQueued: boolean;
}

export async function executeSwarmAudit(): Promise<AuditResult[]> {
  console.log(`🐝 Unleashing Pomelli Swarm across the V23 Fleet...`);

  const brandGuidelines = await queryNotebookLM(
    "What are the strict UX, auth, and 12-task KAIROS guidelines for shadowtag-omega-v4?",
  );

  const results: AuditResult[] = [];

  for (const site of POMELLI_TARGET_MATRIX) {
    console.log(`\n🔍 Flash-Lite Swarm analyzing: ${site.url} (${site.id})`);

    const auditResult: AuditResult = {
      target: site,
      brandGuidelines,
      optimizations: [],
      patchQueued: false,
    };

    // Lighthouse audit via Chrome DevTools MCP
    try {
      const lighthouse =
        await $`bunx --bun mcp-cli call chrome-devtools-mcp lighthouse_audit --url "${site.url}"`
          .timeout(60_000)
          .text();

      if (lighthouse.includes("performance")) {
        auditResult.optimizations.push(`Lighthouse audit completed for ${site.id}`);
      }
    } catch {
      auditResult.optimizations.push(`Lighthouse deferred for ${site.id} (DevTools offline)`);
    }

    // Check for AST rewrite opportunities
    const needsOptimization =
      site.lighthouseBaseline.performance < 100 ||
      site.lighthouseBaseline.accessibility < 100;

    if (needsOptimization) {
      console.log(
        `⚡ Optimization opportunity detected for ${site.id}. Queueing AST-Grep patch.`,
      );
      auditResult.patchQueued = true;

      const patchDir = ".jules_queue";
      await $`mkdir -p ${patchDir}`.quiet().catch(() => {});
      await Bun.write(
        `${patchDir}/${site.id}_patch_${Date.now()}.json`,
        JSON.stringify({
          siteId: site.id,
          url: site.url,
          astRule: "Dynamic Import Optimization",
          baseline: site.lighthouseBaseline,
          timestamp: Date.now(),
        }),
      );
    }

    results.push(auditResult);
  }

  // NotebookLM audio overview generation (deferred in CI, best-effort in local)
  console.log(`\n🎙️ Triggering Audio Overview generation via nlm...`);
  await $`nlm audio-overview create`
    .timeout(30_000)
    .quiet()
    .catch(() => console.log("⚠️ Audio overview deferred (nlm offline or no notebook bound)."));

  console.log(`\n✅ Pomelli Swarm audit complete. ${results.length} properties analyzed.`);
  return results;
}

if (import.meta.main) {
  await executeSwarmAudit();
}
