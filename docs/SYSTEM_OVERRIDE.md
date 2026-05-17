# SYSTEM OVERRIDE: V31 SOVEREIGN MERIDIAN — CHERRY-PICK CONSOLIDATION

> **To:** Antigravity Core Engine
> **Project:** `shadowtag-omega-v4`
> **Version:** V31 | **Status:** LOCKED
> **Last Updated:** 2026-05-17

---

## PLATFORM TOOL BUDGET CONSTRAINT

> [!CAUTION]
> **Antigravity enforces a hard limit of 100 tools across ALL enabled MCP servers.**
> Exceeding this limit causes servers to fail with `Error: adding this instance with N enabled tools would exceed max limit of 100`.

### Current Budget

| Plane 1 Server | Tools | Status |
|----------------|-------|--------|
| firebase-mcp-server | 36 | ✅ |
| chrome-devtools-mcp | 29 | ✅ |
| StitchMCP | 14 | ✅ |
| cloudrun | 8 | ✅ |
| google-developer-knowledge | 3 | ✅ |
| sequential-thinking | 1 | ✅ |
| **Total** | **91** | **9 tools headroom** |

### Removed Servers (Budget/Compatibility)

| Server | Tools | Reason | Alternative |
|--------|-------|--------|-------------|
| `gemini-graph-memory` | 9 | Freed for headroom | Cline Plane 2: `gemini-memory` |
| `gemini-web-fetcher` | ~4 | Python server misconfigured as Node.js | Moved to Cline Plane 2 via `uvx` |
| `gemini-github-mcp` | — | Phantom: binary never existed at path | Removed entirely (no replacement needed) |
| `notebooklm-mcp` | 39 | Would bust 100-tool limit | Cline Plane 2: `notebooklm-mcp` |

### Ready-to-Add: `gemini-web-fetcher` (via uvx)

When budget allows, add this to `~/.gemini/antigravity/mcp_config.json`:

```json
"gemini-web-fetcher": {
  "command": "uvx",
  "args": ["--from", "mcp-server-fetch", "mcp-server-fetch"],
  "transport": "stdio"
}
```

**Estimated tools:** ~4. Budget after addition: ~95/100.

---

## THE DUAL-PLANE SOVEREIGN FLEET (18 TOTAL SERVERS)

Tool redundancy is eradicated. The fleet operates across two symbiotic planes.
Namespace collision between the Antigravity host platform and the Cline local configuration
is constitutionally prohibited.

### The Cognitive Cost of Redundancy (arXiv:2512.14982)
When duplicate tool namespaces exist across two planes, the LLM's test-time reasoning
suffers measurable degradation. The model must:
1. **Parse** both tool descriptions (doubled context window consumption)
2. **Deliberate** which identical API to invoke (wasted compute tokens)
3. **Risk** non-deterministic tool selection (different servers, same capability)

The Dual-Plane separation eliminates all three failure modes.

> *"Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away."*

---

## PLANE 1: ANTIGRAVITY INTERNAL HOST (6 Servers, 91 Tools)

**Config:** `~/.gemini/antigravity/mcp_config.json`
**Do NOT duplicate in Cline config. Rely on native host access.**

| # | Server | Tools | Domain |
|---|--------|-------|--------|
| 1 | `StitchMCP` | 14 | Generative UI variants, design systems, screen generation |
| 2 | `chrome-devtools-mcp` | 29 | Browser sensorium — screenshots, DOM, Lighthouse, perf traces |
| 3 | `cloudrun` | 8 | Compute deployment — deploy containers, folders, file contents |
| 4 | `firebase-mcp-server` | 36 | State, auth, hosting — Firestore, Functions, Storage, Config |
| 5 | `google-developer-knowledge` | 3 | Omniscience — Google developer docs search, retrieval, answers |
| 6 | `sequential-thinking` | 1 | Multi-step reasoning, hypothesis verification |

**Total Plane 1:** 91 tools (9 headroom)

### Plane 1 Capabilities That Were Duplicated (Now Purged from Cline)

| Purged Cline Server | Subsumed By (Plane 1) | Reason |
|--------------------|-----------------------|--------|
| `firebase-hippocampus` | `firebase-mcp-server` | Identical Firestore/Auth/Hosting APIs |
| `browser-sensorium` | `chrome-devtools-mcp` | Identical browser automation APIs |
| `stitch-ui-gen` | `StitchMCP` | Identical design system/screen generation |
| `stitch-mcp-server` | `StitchMCP` | Identical Stitch project management |
| `vertex-omniscience` | `google-developer-knowledge` | Identical Google developer docs search |
| `archon-reasoning` | `sequential-thinking` | Identical reasoning chain API |
| `cloud-run` (in gcp-infra) | `cloudrun` | Identical Cloud Run deployment |

---

## PLANE 2: CLINE TACTICAL LOCAL CONFIG (13 Servers)

**Executed purely via local `cline_mcp_settings.json` via Bun/npx/uvx physics.**
Antigravity does NOT probe, start, or manage these servers.

| # | Server | Runtime | Domain |
|---|--------|---------|--------|
| 7 | `observability` | bunx | Genkit MCP observability |
| 8 | `storage-cdn` | npx | Cloud Storage operations |
| 9 | `stripe-governor` | npx | Stripe financial governor |
| 10 | `notebooklm-mcp` | uvx | NotebookLM epistemic memory |
| 11 | `jules-delegation` | node | Jules async agent delegation |
| 12 | `semantic-scalpel` | npx | AST-Grep semantic code surgery |
| 13 | `pomelli-swarm` | Bun | Pomelli AI brand content swarm |
| 14 | `workspace-intake` | Bun | Google Workspace webhook listener |
| 15 | `bigquery-mcp-server` | HTTP | BigQuery analytics (Google hosted) |
| 16 | `maps-grounding-lite-mcp` | HTTP | Maps grounding context (Google hosted) |
| 17 | `container-mcp-server` | HTTP | GKE container management (Google hosted) |
| 18 | `compute-mcp-server` | HTTP | GCE compute management (Google hosted) |
| 19 | `gemini-web-fetcher` | uvx | Web page fetching via mcp-server-fetch |

---

## ANTI-DUPLICATION LAW

### The Rule
If Antigravity provides a capability natively (Plane 1), Cline MUST NOT instantiate a local
server for the same capability (Plane 2). The inverse also holds: if Cline provides a
tactical server, Antigravity MUST NOT attempt to duplicate or manage it.

### The Rationale
When both Antigravity and Cline expose identical tool names (e.g., two `take_screenshot`
tools, two `deploy_cloud_run` tools), the underlying LLM experiences **tool-choice paralysis**.
It burns test-time compute tokens deliberating over which identical API to invoke.
Redundancy is noise. We eliminate the noise.

### Enforcement
- Before adding ANY new MCP server, check both manifests:
  - Antigravity native: `~/.gemini/antigravity/mcp_config.json`
  - Cline local: `cline_mcp_settings.json`
- If the capability already exists in either plane, the addition is **DENIED**.
- Violations are logged to `.beads/issues.jsonl` with severity `ARCHITECTURE_DRIFT`.
- **Budget check:** Verify tool count stays ≤100 before adding any Plane 1 server.

### Server Addition Decision Tree
```
Want to add server X?
  └─ Does Antigravity already provide this capability (Plane 1)?
      ├─ YES → DENIED. Use native Antigravity tool.
      └─ NO → Does Cline already provide this capability (Plane 2)?
          ├─ YES → DENIED. Enhance existing server.
          └─ NO → Will adding to Plane 1 exceed 100-tool limit?
              ├─ YES → Add to Cline config (Plane 2) instead.
              └─ NO → APPROVED. Add to mcp_config.json (Plane 1).
                      Antigravity host additions require platform team approval.
```

### Drift Detection Protocol
Run on every boot (OMNI-BOOT Section 0C):
```bash
PLANE1_TOOLS="StitchMCP chrome-devtools-mcp cloudrun firebase-mcp-server google-developer-knowledge sequential-thinking"
CLINE_CFG="$HOME/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
for srv in $PLANE1_TOOLS; do
  grep -qi "$srv" "$CLINE_CFG" 2>/dev/null && echo "❌ DRIFT: $srv" && exit 1
done
```

---

## CLINE CONFIG REFERENCE

The canonical `cline_mcp_settings.json` for Plane 2:

```json
{
  "mcpServers": {
    "observability": {
      "command": "bunx",
      "args": ["--bun", "@google-cloud/observability-mcp"],
      "transport": "stdio"
    },
    "storage-cdn": {
      "command": "npx",
      "args": ["-y", "@google-cloud/storage-mcp"],
      "transport": "stdio"
    },
    "stripe-governor": {
      "command": "npx",
      "args": ["-y", "@stripe/mcp"],
      "transport": "stdio"
    },
    "notebooklm-mcp": {
      "command": "uvx",
      "args": ["--from", "notebooklm-mcp-cli", "notebooklm-mcp"],
      "transport": "stdio"
    },
    "jules-delegation": {
      "command": "node",
      "args": ["/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/antigravity-jules-orchestration/index.js"],
      "transport": "stdio"
    },
    "semantic-scalpel": {
      "command": "npx",
      "args": ["-y", "ast-grep-mcp"],
      "transport": "stdio"
    },
    "pomelli-swarm": {
      "command": "bun",
      "args": ["run", "--cwd", "/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/external_repos/flpomp-team", "dev"],
      "transport": "stdio"
    },
    "workspace-intake": {
      "command": "bun",
      "args": ["run", "/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/tools/workspace-intake/index.ts"],
      "transport": "stdio"
    },
    "bigquery-mcp-server": {
      "httpUrl": "https://bigquery.googleapis.com/mcp",
      "authProviderType": "google_credentials",
      "oauth": { "scopes": ["https://www.googleapis.com/auth/bigquery"] },
      "timeout": 30000,
      "headers": { "x-goog-user-project": "shadowtag-omega-v4" }
    },
    "maps-grounding-lite-mcp": {
      "httpUrl": "https://mapstools.googleapis.com/mcp",
      "headers": { "X-Goog-Api-Key": "${GOOGLE_DESIGN_API_KEY}" }
    },
    "container-mcp-server": {
      "httpUrl": "https://container.googleapis.com/mcp",
      "authProviderType": "google_credentials",
      "oauth": { "scopes": ["https://www.googleapis.com/auth/cloud-platform"] },
      "timeout": 30000,
      "headers": { "x-goog-user-project": "shadowtag-omega-v4" }
    },
    "compute-mcp-server": {
      "httpUrl": "https://compute.googleapis.com/mcp",
      "authProviderType": "google_credentials",
      "oauth": { "scopes": ["https://www.googleapis.com/auth/compute"] },
      "timeout": 30000,
      "headers": { "x-goog-user-project": "shadowtag-omega-v4" }
    }
  }
}
```

---

## DAEMON FLEET REGISTRY

Autonomous background processes that maintain workspace hygiene.

| Daemon | Script | Schedule | Purpose |
|--------|--------|----------|---------|
| Dream Consolidation | `scripts/dream_consolidation.py` | Nightly | KI maintenance: orient → gather → consolidate → prune |
| Loop Steward | `scripts/loop_steward.py` | 5-min cycles | Autonomous task continuation with idle scaling |
| KAIROS | `scripts/kairos_daemon.py` | Background | Proactive suggestion engine with Gemini 3.x inference |
| pnkln-evolve | `scripts/pnkln_evolve.py` | Background | Recursive self-improvement loop |
| Omni-Autolint | `scripts/gca_autolint_daemon.py` | Daily 3-5AM | Secure lint+push via GitHub App tokens, beads audit trail |

### Daemon Health Check

```bash
# Verify daemon scripts exist and are executable
for d in dream_consolidation loop_steward kairos_daemon pnkln_evolve gca_autolint_daemon; do
  [ -f "scripts/${d}.py" ] && echo "✅ $d" || echo "❌ $d MISSING"
done
```

---

> **Constitutional Status:** LOCKED.
> Modifications require STATE B (Clutch) approval and 8-Agent Board Synthesis.
>
> **Version History:**
> - V26 (2026-05-15): Initial dual-plane separation. 7 redundant servers purged.
> - V26.1 (2026-05-15): Added cognitive cost rationale, drift detection protocol, server addition decision tree.
> - V26.2 (2026-05-15): **100-tool platform constraint documented.** Plane 1 reduced from 7→6 servers (91 tools, 9 headroom). Removed `gemini-graph-memory` (Cline has equivalent), `gemini-web-fetcher` (module mismatch, now ready-to-add via `uvx`), `notebooklm-mcp` (budget overflow, lives on Cline Plane 2). Config source corrected to `~/.gemini/antigravity/mcp_config.json`. Decision tree updated with budget check step.
> - V26.3 (2026-05-15): **Cline config hardened.** Hardcoded Maps API key replaced with `${GOOGLE_DESIGN_API_KEY}`. Phantom `gemini-github-mcp` removed (binary never existed). `gemini-web-fetcher` migrated from broken Bun→uvx and moved to Plane 2. 3 path drifts fixed (`mono-fresh` → `Monorepo-Uphillsnowball`). Stale `pyproject.toml` ruff config removed (line-length 100 vs 150 conflict). 2,836 lint violations fixed (142 I001, 754 T201, 1896 D400/D415, 44 F401/F841).
> - V30 (2026-05-16): **Cleanup cascade.** 10 malformed `prompt_repeat.py` copies fixed (multiline default arg → escaped `\n`). Notebook schema reformatted. Biome 2.4.13 formatted 663 TS/JS files. Ruff dead-import fixes (F401). Judge6 timeout 30→50ms. Tracked `.pyc` removed. Daemon fleet registry added. 14/14 Stripe webhook tests passing. Firestore rules verified (9 collections, field-level restrictions). dotenv usage audited (18 references flagged in non-production code).
> - V31 (2026-05-17): **Cherry-pick consolidation.** Feature branch `fix/v26.3-dual-plane-hardening` had 13 commits but 4 mass-reformat bombs (7943+6901+4171+1983 files) caused 2738 merge conflicts. Solution: abort merge, cherry-pick 8 surgical commits (30 files total). Cherry-picks: E741 lint fixes, auth push URL fix, AG-UI+A2A mesh+Darwinian Gate, bicameral MCP split+Stripe tests, /healthz endpoint, TS compilation+IAM, test pollution fix, datetime.utcnow→datetime.now(UTC)+genai SDK. Test suite: **3688 passed, 35 skipped, 0 failures** (6m10s). Gitleaks: 1118 findings (all in third-party vendored code — yarn, labs/gemini-cookbook, external_sdks). Firestore rules verified (12 collections, zero open-write). Cloud Run /healthz: HTTP 404 (not yet deployed with new endpoint). Biome incremental: 1961 TS/JS files auto-fixed. Ruff: 2 F401 unused imports removed. `uphillsnowball` remote deleted. Sandbox `firestore_schema.py` cherry-picked for Phase 3.
