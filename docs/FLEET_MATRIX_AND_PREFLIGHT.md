# V29 PINNACLE SINGULARITY: THE BICAMERAL FLEET MATRIX

**Temporal Anchor:** Friday, May 16, 2026
**Target Project:** `shadowtag-omega-v4`

## 1. THE FLEET MATRIX (EXHAUSTIVE CENSUS)

The OS operates across two distinct hemispheres to protect Antigravity's strict **100-tool cognitive limit**. Do not attempt to invoke tools assigned to the IDE Tactician.

### HEMISPHERE A: ANTIGRAVITY (TERMINAL ENGINE)
*Tool Count: 99/100 (Safe). Role: Lightning-fast terminal operator, infrastructure architect, and epistemic synthesizer.*

**Native Platform Servers (Injected automatically by Google — NOT in mcp_config.json):**

| # | Server | Tools | Domain |
|---|--------|-------|--------|
| 1 | `StitchMCP` | 14 | Design systems, UI variants, M3 token math |
| 2 | `chrome-devtools-mcp` | 29 | DOM inspection, Lighthouse P100 audits |
| 3 | `cloudrun` | 8 | Direct compute deployment |
| 4 | `firebase-mcp-server` | 36 | State, Auth, Firestore, Firebase Hosting |
| 5 | `google-developer-knowledge` | 3 | Grounded API documentation |
| 6 | `bigquery` | 2 | BigQuery SQL queries |
| 7 | `gcloud` | 1 | gcloud CLI commands |
| 8 | `gemini-memory` | 3 | Memory store/recall/list |
| 9 | `genkit` | 2 | Genkit CLI operations |
| | **Subtotal** | **98** | |

**User Config Server (`~/.gemini/antigravity/mcp_config.json`):**

| # | Server | Tools | Domain |
|---|--------|-------|--------|
| 10 | `sequential-thinking` | 1 | Deep reasoning loop isolation |
| | **Subtotal** | **1** | |

**TOTAL ANTIGRAVITY TOOLS: 99/100** ✅

---

### HEMISPHERE B: CLINE (IDE TACTICIAN)
*Role: Heavy IDE cruiser. Visual codebase management, AST-surgery, Swarm logic, and PR management.*
*Config: `cline_mcp_settings.json` (repo root)*

| # | Server | Domain |
|---|--------|--------|
| 1 | `observability` (13 tools) | OpenTelemetry, Cloud Logging, traces |
| 2 | `storage` (15 tools) | GCS bucket operations |
| 3 | `mcp-toolbox-spanner` (4 tools) | Spanner database healing |
| 4 | `stripe` (31 tools) | Payment operations |
| 5 | `stripe-governor` (31 tools) | Financial ROI validation |
| 6 | `notebooklm-mcp` (39 tools) | 1M-token epistemic memory (uvx) |
| 7 | `antigravity-notebooklm-mcp` | NotebookLM via npx |
| 8 | `jules-mcp-server` (3 tools) | Cloud CI/CD DevOps Commander |
| 9 | `cloud-run` | Cloud Run (Cline duplicate) |
| 10 | `gcloud` | gcloud CLI (Cline instance) |
| 11 | `genkitx` | Genkit extensions (disabled) |

---

## 2. THE 100-TOOL BUDGET RULE

Antigravity has a **hard limit of 100 enabled tools**. If adding a server causes cumulative tool count to exceed 100, it shows red with: `Error: adding this instance with N enabled tools would exceed max limit of 100`.

**Rule:** Only `sequential-thinking` goes in `mcp_config.json`. Everything else either:
- Is platform-injected (servers 1–9), or
- Lives in `cline_mcp_settings.json` (Hemisphere B)

**Previous error (Codex session 2026-05-15):** 17 servers were crammed into `mcp_config.json`, causing 11 servers to fail with tool-limit overflow. Fixed by stripping to 1 user-config server.
