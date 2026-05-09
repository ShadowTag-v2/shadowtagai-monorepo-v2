# UPHILLSNOWBALL SOVEREIGN OS v18 — ISOMORPHIC GRAPHQL ASCENSION

> Version: 18.0 | Status: LOCKED | Date: 2026-05-09

## Architecture — Distributed Swarm

V18 evolves V17's distributed swarm into a **unified isomorphic architecture** powered by the
**Kriasoft Triad** (react-starter-kit, graphql-starter-kit, react-firebase-starter). Legacy
Node.js/Python dependencies are replaced with native Bun implementations. The enterprise registry
(`.bunfig.toml`) routes private packages through Google Artifact Registry.

```
┌──────────────────────────────────────────────────────────────────┐
│                    SOVEREIGN OS v18                               │
│            "Isomorphic GraphQL Ascension"                        │
│                                                                   │
│  ┌─────────────────────────────┐  ┌────────────────────────────┐ │
│  │ LOCAL AGENT (Cline)         │  │ CLOUD AGENT (Jules)        │ │
│  │                             │  │                            │ │
│  │ • Reasoning / Planning      │  │ • CI/CD Orchestration      │ │
│  │ • Stitch Generative UI      │  │ • Cloud Run Deployment     │ │
│  │ • Design MCP (Aesthetic)    │  │ • Spanner DDL Migrations   │ │
│  │ • SheetJS Tabular Intake    │  │ • Security Scanning        │ │
│  │ • Code Generation           │  │ • Lighthouse Audits        │ │
│  │                             │  │                            │ │
│  │ Runtime: Bun 1.3.11         │  │ Runtime: GitHub Actions    │ │
│  │ Transport: stdio/HTTP       │  │ Transport: jules-action    │ │
│  └──────────┬──────────────────┘  └──────────┬─────────────────┘ │
│             │                                │                    │
│             └──────────┬─────────────────────┘                    │
│                        │                                          │
│  ┌─────────────────────▼──────────────────────────────────────┐  │
│  │ HIPPOCAMPUS (State Layer)                                   │  │
│  │                                                             │  │
│  │ • Firestore Checkpoint/Resume     • Gemini File Memory      │  │
│  │ • Skill Registry (247 active)     • KI Corpus (20+ items)   │  │
│  └─────────────────────┬──────────────────────────────────────┘  │
│                        │                                          │
│  ┌─────────────────────▼──────────────────────────────────────┐  │
│  │ AUTONOMIC NERVOUS SYSTEM                                    │  │
│  │                                                             │  │
│  │ • FinOps Governor           • MCP Watchdog                  │  │
│  │ • Self-Healing Loop         • Telemetry Healer              │  │
│  │ • Repo Doctor (Score: A)    • Dream Consolidation           │  │
│  └─────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

V18 adopts Bun as the **exclusive** JavaScript/TypeScript runtime with the Hono v4 gateway.

| Dimension | V17 (Bun-First) | V18 (Bun-Native) |
|-----------|-----------------|-------------------|
| API framework | Direct handlers | Hono v4 + GraphQL Yoga |
| MCP server boot | `bunx --bun <pkg>` | `bunx --bun <pkg>` |
| Package registry | Public NPM | Enterprise `.bunfig.toml` + Artifact Registry |
| Backend pattern | Script-based | Kriasoft isomorphic GraphQL |
| Cold start | ~12ms | ~12ms |
| Memory allocator | mimalloc | mimalloc |

**Migration rule**: Cline sidecar servers migrate to `bunx --bun` where the package supports it.
Antigravity engine servers remain as-is (platform-managed, not user-configurable).

## MCP Fleet Manifest (v17)

### Antigravity Engine (5 servers — `antigravity-mcp-config.json`)

| # | Server | Transport | Tools | Domain |
|---|--------|-----------|-------|--------|
| 1 | StitchMCP | stdio | 12 | Design systems, screen generation |
| 2 | chrome-devtools-mcp | stdio | 29 | Browser automation, Lighthouse |
| 3 | firebase-mcp-server | stdio | 45 | Auth, Firestore, Hosting, Functions |
| 4 | google-developer-knowledge | stdio | 3 | Google developer docs |
| 5 | sequential-thinking | stdio | 1 | Multi-step reasoning |

### Cline Sidecar (9 servers — `cline_mcp_settings.json`)

| # | Server | Runtime | Tools | Status |
|---|--------|---------|-------|--------|
| 1 | uphill-design-mcp | StreamableHTTP | 5 | ✅ ACTIVE |
| 2 | uphill-gcloud-infra | bunx | 1+ | ✅ ACTIVE |
| 3 | uphill-observability | bunx | 10 | ✅ ACTIVE |
| 4 | uphill-cloud-run | bunx | 4 | ✅ ACTIVE |
| 5 | uphill-storage-cdn | bunx | 6 | ✅ ACTIVE |
| 6 | uphill-epistemic-memory | bun | 7 | ✅ ACTIVE |
| 7 | uphill-notebooklm | bunx | 4 | ✅ ACTIVE |
| 8 | uphill-cognitive-telemetry | bunx | — | ⏸ DISABLED |
| 9 | uphill-economic-engine | bunx | — | ⏸ DISABLED |

**Total: 14 servers, 100+ tools across dual engines.**

## Archon Delegation Doctrine

The Archon pattern replaces the God-Agent anti-pattern. The local agent NEVER runs
`gcloud builds submit` or bash deployment scripts directly.

```
Local Agent (Cline)                    Cloud Agent (Jules)
────────────────────                   ───────────────────
1. Generate code                       4. Receive push event
2. Run local tests                     5. Authenticate via WIF
3. git push → GitHub ──────────────→   6. Run jules-skills
                                       7. Deploy to Cloud Run
                                       8. Post deployment URL
```

**Workflow**: `.github/workflows/jules-ci.yml`
**Skills repo**: `google-labs-code/jules-skills`
**Action**: `google-labs-code/jules-action@v1`

## Intake Channels

### Prose Intent (Google Docs)
Decoded via `Buffer.from(base64, 'base64').toString('utf-8')`.
Routed to Gemini File Memory for vector search.

### Tabular Ledger (Excel/CSV — NEW in V17)
Parsed via SheetJS (`xlsx` package) in `tools/workspace-listener/webhook_handler.ts`.
Converts `.xlsx`/`.csv` to structured CSV, then uploads to Gemini File API.

### Visual Design (Stitch)
Material 3 UI variants generated programmatically via `stitch-sdk`.
React components use `react-starter-kit` as the isomorphic chassis.

## 7-Step Cognitive Workflow (V17)

1. **PERCEIVE** — Design MCP + Observability scans the environment
2. **REMEMBER** — Firestore Hippocampus retrieves agent state
3. **PLAN** — Sequential Thinking structures multi-step approach
4. **DESIGN** — Stitch MCP generates M3 UI variants; Design MCP provides tokens
5. **EXECUTE** — Cloud Run + gcloud MCP deploys infrastructure
6. **DELEGATE** — Jules CI/CD handles async cloud mutations
7. **GOVERN** — FinOps Governor enforces cost circuit breakers

## Neuroplasticity Protocol

The OS acquires new capabilities at runtime:

```bash
# Acquire from Google Skills ecosystem
npx skills add google/skills --skill <skill-name>

# Acquire from Vercel Skills ecosystem
npx skills add vercel-labs/skills --skill <skill-name>

# Local fallback search
grep -rl "<capability>" external_repos/google-skills/ external_repos/vercel-skills/
```

### External Repos — Reference Leverage (v17 — 17 repos)

| Group | Repos | Purpose |
|-------|-------|---------|
| Google Labs | stitch-skills, stitch-sdk, jules-skills, jules-sdk, jules-action, jules-awesome-list, action-setup | Generative UI + Cloud CI/CD |
| Bun Ecosystem | bun, awesome-bun, mimalloc, zig, libuv, homebrew-bun | Runtime physics upgrade |
| Tools | sheetjs, react-starter-kit, Archon | Tabular intake, UI chassis, multi-agent patterns |
| Cline | prompts | Host neuroplasticity reference |

## Security Invariants

- Rule 00: Immutable Infrastructure — no destructive file operations
- Secrets: GCP Secret Manager only — no `.env`, no hardcoded keys
- IPv4-first: `NODE_OPTIONS=--dns-result-order=ipv4first` on all MCP servers
- Proxy clear: `HTTP_PROXY=""`, `HTTPS_PROXY=""` to prevent IDE proxy interference
- Epistemic Airgap: Never pass proprietary identifiers to public search
- WIF: Workload Identity Federation for all GitHub Actions → GCP auth
