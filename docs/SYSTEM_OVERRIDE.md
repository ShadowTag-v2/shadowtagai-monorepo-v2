# SYSTEM OVERRIDE: V26 SYMBIOTIC ALIGNMENT — DUAL-PLANE FLEET SEPARATION

> **To:** Antigravity Core Engine
> **Project:** `shadowtag-omega-v4`
> **Version:** V26 | **Status:** LOCKED
> **Last Updated:** 2026-05-15

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

## PLANE 1: ANTIGRAVITY INTERNAL HOST (6 Servers)

**Do NOT duplicate in Cline config. Rely on native host access.**

| # | Server | Tools | Domain |
|---|--------|-------|--------|
| 1 | `StitchMCP` | 14 | Generative UI variants, design systems, screen generation |
| 2 | `chrome-devtools-mcp` | 29 | Browser sensorium — screenshots, DOM, Lighthouse, perf traces |
| 3 | `cloudrun` | 8 | Compute deployment — deploy containers, folders, file contents |
| 4 | `firebase-mcp-server` | 36 | State, auth, hosting — Firestore, Functions, Storage, Config |
| 5 | `google-developer-knowledge` | 3 | Omniscience — Google developer docs search, retrieval, answers |
| 6 | `sequential-thinking` | 1 | Multi-step reasoning, hypothesis verification |

**Total Plane 1:** 91 tools

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

## PLANE 2: CLINE TACTICAL LOCAL CONFIG (12 Servers)

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
  - Antigravity native: `antigravity-mcp-config.json`
  - Cline local: `cline_mcp_settings.json`
- If the capability already exists in either plane, the addition is **DENIED**.
- Violations are logged to `.beads/issues.jsonl` with severity `ARCHITECTURE_DRIFT`.

### Server Addition Decision Tree
```
Want to add server X?
  └─ Does Antigravity already provide this capability (Plane 1)?
      ├─ YES → DENIED. Use native Antigravity tool.
      └─ NO → Does Cline already provide this capability (Plane 2)?
          ├─ YES → DENIED. Enhance existing server.
          └─ NO → APPROVED. Add to Cline config (Plane 2).
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

> **Constitutional Status:** LOCKED.
> Modifications require STATE B (Clutch) approval and 8-Agent Board Synthesis.
>
> **Version History:**
> - V26 (2026-05-15): Initial dual-plane separation. 7 redundant servers purged.
> - V26.1 (2026-05-15): Added cognitive cost rationale, drift detection protocol, server addition decision tree.
