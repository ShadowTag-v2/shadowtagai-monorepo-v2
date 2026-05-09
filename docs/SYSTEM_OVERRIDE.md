# UPHILLSNOWBALL SOVEREIGN OS v16 — SYSTEM OVERRIDE MANIFESTO

> Version: 16.0 | Status: LOCKED | Date: 2026-05-09

## Architecture

The Sovereign OS operates as a biological neural network metaphor mapped onto cloud infrastructure:

```
┌──────────────────────────────────────────────────────────────┐
│                    SOVEREIGN OS v16                          │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐ │
│  │ PREFRONTAL │  │ MOTOR      │  │ SENSORY CORTEX         │ │
│  │ CORTEX     │  │ CORTEX     │  │                        │ │
│  │            │  │            │  │ • Observability MCP    │ │
│  │ • Gemini   │  │ • Cloud    │  │ • Design MCP           │ │
│  │   Memory   │  │   Run MCP  │  │ • Spanner Healer       │ │
│  │ • File     │  │ • gcloud   │  │ • Telemetry Healer     │ │
│  │   Search   │  │   MCP      │  │                        │ │
│  └─────┬──────┘  └─────┬──────┘  └────────────┬───────────┘ │
│        │               │                      │             │
│        └───────────┬────┴──────────────────────┘             │
│                    │                                         │
│        ┌───────────▼───────────┐                             │
│        │ HIPPOCAMPUS           │                             │
│        │                       │                             │
│        │ • Firestore State     │                             │
│        │ • Checkpoint/Resume   │                             │
│        │ • Skill Registry      │                             │
│        └───────────┬───────────┘                             │
│                    │                                         │
│        ┌───────────▼───────────┐                             │
│        │ AUTONOMIC NERVOUS     │                             │
│        │ SYSTEM                │                             │
│        │                       │                             │
│        │ • FinOps Governor     │                             │
│        │ • MCP Watchdog        │                             │
│        │ • Self-Healing Loop   │                             │
│        └───────────────────────┘                             │
└──────────────────────────────────────────────────────────────┘
```

## MCP Fleet Manifest (v16)

### Antigravity Engine (10 servers — `antigravity-mcp-config.json`)

| # | Server | Transport | Tools | Domain |
|---|--------|-----------|-------|--------|
| 1 | StitchMCP | stdio | 12 | Design systems, screen generation |
| 2 | chrome-devtools-mcp | stdio | 29 | Browser automation, Lighthouse |
| 3 | firebase-mcp-server | stdio | 45 | Auth, Firestore, Hosting, Functions |
| 4 | google-developer-knowledge | stdio | 3 | Google developer docs |
| 5 | sequential-thinking | stdio | 1 | Multi-step reasoning |

### Cline Sidecar (9 servers — `cline_mcp_settings.json`)

| # | Server | Transport | Tools | Status |
|---|--------|-----------|-------|--------|
| 1 | uphill-design-mcp | StreamableHTTP | 5 | ✅ ACTIVE |
| 2 | uphill-gcloud-infra | stdio | 1+ | ✅ ACTIVE |
| 3 | uphill-observability | stdio | 10 | ✅ ACTIVE |
| 4 | uphill-cloud-run | stdio | 4 | ✅ ACTIVE |
| 5 | uphill-storage-cdn | stdio | 6 | ✅ ACTIVE |
| 6 | uphill-notebooklm | stdio | 4 | ✅ ACTIVE |
| 7 | uphill-epistemic-memory | stdio | 7 | ✅ ACTIVE |
| 8 | uphill-cognitive-telemetry | stdio | — | ⏸ DISABLED |
| 9 | uphill-economic-engine | stdio | — | ⏸ DISABLED |

**Total: 19 servers, 100+ tools across dual engines.**

## 7-Step Cognitive Workflow

1. **PERCEIVE** — Design MCP + Observability scans the environment
2. **REMEMBER** — Firestore Hippocampus retrieves agent state
3. **PLAN** — Sequential Thinking structures multi-step approach
4. **DESIGN** — Design MCP generates color schemes, fonts, icons
5. **EXECUTE** — Cloud Run + gcloud MCP deploys infrastructure
6. **HEAL** — Spanner Healer + Telemetry Healer fix anomalies
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

## Design MCP Integration

The Google Design MCP (`design.googleapis.com/mcp`) serves as the headless design engine:

- **No API key required** — open access
- **5 tools**: `generate_color_scheme`, `search_icons`, `icons_instructions`, `search_fonts`, `describe_font`
- **Transport**: StreamableHTTP (remote SSE, not local stdio)
- **Use**: Material Design palettes, Google Fonts metadata, Material Symbols search

### Inspector Command
```bash
npx @modelcontextprotocol/inspector https://design.googleapis.com/mcp
```

## Security Invariants

- Rule 00: Immutable Infrastructure — no destructive file operations
- Secrets: GCP Secret Manager only — no `.env`, no hardcoded keys
- IPv4-first: `NODE_OPTIONS=--dns-result-order=ipv4first` on all Node.js MCP servers
- Proxy clear: `HTTP_PROXY=""`, `HTTPS_PROXY=""` to prevent IDE proxy interference
- Epistemic Airgap: Never pass proprietary identifiers to public search
