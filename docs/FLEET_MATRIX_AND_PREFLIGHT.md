---
version: "V30"
status: LOCKED
date: 2026-05-18
---

# Bicameral OS Fleet Matrix — V30

> **Anti-Duplication Law:** If Antigravity provides a capability (Plane 1), Cline MUST NOT instantiate a local server for the same capability. Drift detection runs on every boot. Flutter development is handled natively by `dart-mcp`; a separate Flutter server is explicitly prohibited.

---

### Plane 1 — Antigravity Internal Host (6 Servers, 91 Tools)

| # | Server | Tools | Domain |
|---|--------|-------|--------|
| 1 | `StitchMCP` | 14 | Generative UI, design systems, screen generation |
| 2 | `chrome-devtools-mcp` | 29 | Browser sensorium — DOM, screenshots, Lighthouse, perf |
| 3 | `cloudrun` | 8 | Compute deployment — containers, folders, file contents |
| 4 | `firebase-mcp-server` | 36 | Firestore, Auth, Hosting, Functions, Storage |
| 5 | `google-developer-knowledge` | 3 | Google developer docs search, retrieval, answers |
| 6 | `sequential-thinking` | 1 | Multi-step reasoning, hypothesis verification |

---

### Plane 2 — Cline Tactical Local (17 Servers)

| # | Server | Purpose |
|---|--------|---------|
| 1 | `observability` | Cloud Logging query + error triage |
| 2 | `storage-cdn` | Cloud Storage for WASM Edge/CDN delivery |
| 3 | `stripe-governor` | FinOps governor — reads products, revenue, subscriptions |
| 4 | `notebooklm-mcp` | Epistemic memory via `uvx` CLI (notebooklm-py v0.3.4) |
| 5 | `jules-delegation` | Local tunnel for dispatching async cloud delegation to Jules |
| 6 | `semantic-scalpel` | AST-Grep wrapper for structural codebase mutations |
| 7 | `pomelli-swarm` | A/B testing and UI optimization fleet control |
| 8 | `workspace-intake` | Actively polls Google Drive for PRDs |
| 9 | `bigquery-mcp-server` | Financial ledger and ROI analytics |
| 10 | `maps-grounding-lite-mcp` | Geo-grounding for location intelligence |
| 11 | `container-mcp-server` | Docker/container management |
| 12 | `compute-mcp-server` | GCE compute instance management |
| 13 | `gemini-graph-memory` | Sovereign memory — graph-based knowledge persistence |
| 14 | `gemini-github-mcp` | GitHub API operations via Gemini |
| 15 | `gemini-web-fetcher` | Web content extraction and scraping |
| 16 | `dart-mcp` | Dart language server (`dart language-server --protocol=lsp`) — handles Flutter natively |
| 17 | `spanner-mcp` | Global Spanner DDL, live mutation capture |

---

### Preflight Integrity Check

On every session boot, verify:

```bash
# Plane 1 — Antigravity (platform-managed, no manual check needed)
# Plane 2 — Cline tactical
jq '.mcpServers | keys | length' "$HOME/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
# Expected: 17
```

### Drift Detection Rules

1. If a server appears in Cline but NOT in this manifest → FLAG as unauthorized
2. If a server appears in Antigravity AND Cline → VIOLATION of Anti-Duplication Law
3. If tool count exceeds 100 on Plane 1 → Move lowest-priority server to Plane 2
4. `gemini-graph-memory` is a Plane 2 (Cline) server ONLY. It is NOT a native Antigravity platform server.

---

*V30 Census locked 2026-05-18T12:25 PDT. 23 total servers across both planes.*
