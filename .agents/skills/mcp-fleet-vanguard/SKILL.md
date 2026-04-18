---
name: mcp-fleet-vanguard
description: "Enforces Zero-Blind Execution across the 5-server MCP fleet. All Firebase, browser, design, and knowledge operations route exclusively through MCP servers. Capability ownership lives in antigravity-mcp-config.json — not this skill. This skill enforces the routing discipline, secrets hygiene, and self-healing loop."
---

# MCP Fleet Vanguard (v11.0)

Enforces strict "Zero-Blind Execution" rules. Design operations, Firebase deployments, browser testing, and knowledge lookups route EXCLUSIVELY through the MCP fleet — never raw bash fallbacks.

## Session Invariants (Active Until MEMORY UNLOCK)

These invariants MUST be mirrored verbatim before any repo-wide action:

1. `AGENTS.md` is canonical contract. `antigravity-mcp-config.json` is canonical MCP truth.
2. No second source of truth. No committed secrets. No complecting orthogonal concerns.
3. All MCP servers MUST be used (Firebase, Chrome DevTools, Stitch, Developer Knowledge, Sequential Thinking).
4. `GEMINI.md` defines operator invariants, NOT capability ownership or routing.
5. Capability ownership lives ONLY in `antigravity-mcp-config.json`.
6. Prompt repetition applies ONLY to non-reasoning tiers (Oracle Studio, model_router, Vent Mode, Autoresearch Triad).
7. Secrets only via [GCP Secret Manager](https://docs.cloud.google.com/code/docs/vscode/secret-manager) for production. Local dev uses `.env` (gitignored, kernel-locked). No hardcoded keys in source or config.

## When to Use

- At the start of any conversation or new task
- **Before EACH tool call** involving Firebase, browser devtools, design tokens, screen generation, or SDK documentation
- Whenever a terminal command fails or an MCP server appears crashed
- Before any repo-wide action (mirror invariants first)

## Pre-flight Integrity Check (5-Server Fleet)

Before proceeding, verify the MCP fleet is installed, ONLINE, and prioritized:

| # | Server | Transport | Tools | Purpose | Status |
|---|--------|-----------|-------|---------|--------|
| 1 | `StitchMCP` | Remote (mcp-remote → stitch.googleapis.com) | ~12 | Design tokens, screen generation, UI structure, brand assets | verify |
| 2 | `chrome-devtools-mcp` | Local (node) | ~25 | Browser inspection, DOM queries, console, network, screenshots | verify |
| 3 | `firebase-mcp-server` | Local (npx) | ~45 | Hosting, Auth, Storage, Functions, Firestore, App Hosting | verify |
| 4 | `google-developer-knowledge` | Remote (mcp-remote → developerknowledge.googleapis.com) | ~3 | SDK docs, API references, developer knowledge | verify |
| 5 | `sequential-thinking` | Local (node) | ~1 | Formal step-by-step reasoning for multi-step decisions | verify |

**Total budget:** ~86 tools (under 100 ceiling)

**Canonical config:** `antigravity-mcp-config.json` (repo truth — SOLE authority for capability ownership)
**Mirror:** `~/.gemini/antigravity/mcp_config.json` (editor runtime — mirrors repo truth)

### CRITICAL: Node PATH Fix

All `command` entries MUST use the absolute nvm path:
```
/Users/pikeymickey/.nvm/versions/node/v24.14.1/bin/node
```
Or for npx:
```
/Users/pikeymickey/.nvm/versions/node/v24.14.1/bin/npx
```
Bare `npx` WILL FAIL with `exec: "npx": executable file not found in $PATH`.

Every server entry MUST include:
```json
"env": {
  "PATH": "/Users/pikeymickey/.nvm/versions/node/v24.14.1/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin",
  "HOME": "/Users/pikeymickey"
}
```

## Capability Routing — Delegated to MCP Config

> **CRITICAL:** This skill does NOT define capability ownership or routing tables.
> Capability ownership lives ONLY in `antigravity-mcp-config.json`.
> `GEMINI.md` defines operator invariants, NOT routing.

### The Single Rule

If an operation CAN be performed by an MCP server, it MUST be. The operation MUST NOT fall back to raw terminal commands.

| Domain | MCP Server | Fallback Allowed? |
|--------|-----------|-------------------|
| Design & Media | StitchMCP | ❌ NO |
| Firebase & Hosting | firebase-mcp-server | ❌ NO |
| Browser Testing | chrome-devtools-mcp | ❌ NO |
| SDK Documentation | google-developer-knowledge | ❌ NO |
| Multi-Step Reasoning | sequential-thinking | ❌ NO |
| Git operations | `run_command` | ✅ YES — git is local, not MCP |
| Python/Go scripts | `run_command` | ✅ YES — local execution |
| Linting (ruff/vulture) | `run_command` | ✅ YES — local tools |
| Package management | `run_command` | ✅ YES — brew/pip/npm |

### What This Means In Practice

- To deploy → use `firebase-mcp-server`, never `firebase deploy` in terminal
- To screenshot → use `chrome-devtools-mcp`, never external tools
- To look up API docs → use `google-developer-knowledge`, never `search_web` for Google APIs
- To generate UI → use `StitchMCP`, never hand-code from memory
- To reason through architecture → use `sequential-thinking`, never ad-hoc bullet lists

## Secrets Doctrine

### Production (Cloud Run, deployed services)
- **ONLY** [GCP Secret Manager](https://docs.cloud.google.com/code/docs/vscode/secret-manager)
- Cloud Run services access secrets via `valueFrom.secretKeyRef`
- Service accounts need `roles/secretmanager.secretAccessor`
- Upload script: `bash scripts/upload_secrets_to_gcp.sh`
- Google services (Vertex AI, Firestore, Translate) use **ADC** — NO API keys needed

### Local Development (MCP servers, local scripts)
- `.env` (repo root, gitignored, `chflags uchg` kernel-locked)
- MCP config uses `${VAR}` references that resolve from environment at startup
- AI blindfolds: `.aiexclude`, `.geminiignore`, `.clineignore`, `.rooignore` all exclude `.env`
- Validate: `bash scripts/validate_env.sh`

### NEVER
- Hardcoded keys in source files
- Hardcoded keys in committed config files (e.g., `antigravity-mcp-config.json`)
- API keys in logs, chat, or frontend code
- `STRIPE_PUBLISHABLE_KEY` is the ONLY exception (public by design, frontend only)

## The Self-Healing Loop

If any server is dead, missing, or unresponsive:

1. **HALT** — do NOT report failure or proceed with workaround
2. Check `antigravity-mcp-config.json` (repo truth) for the server entry
3. Verify the `command` uses absolute node/npx path (not bare `npx`)
4. Verify `env.PATH` includes `/Users/pikeymickey/.nvm/versions/node/v24.14.1/bin`
5. For remote servers (StitchMCP, google-developer-knowledge): verify API key env var is set
6. Re-verify against the fleet table above
7. Only then proceed with the original task

## Design Workflow (Cor.Build via Stitch)

The correct pipeline for all UI/visual work:

```
StitchMCP: create_project
  → StitchMCP: generate_screen_from_text (full page design)
  → StitchMCP: edit_screens (iterate on design)
  → StitchMCP: get_screen → download HTML
  → Chrome DevTools MCP: test in browser
  → Firebase MCP: deploy to hosting
```

## Stitch SDK Reference

Cloned to: `.stitch-sdk/` in monorepo root
NPM package: `@google/stitch-sdk`
MCP endpoint: `https://stitch.googleapis.com/mcp`

Key tools:
- `create_project` — Create a new Stitch project
- `generate_screen_from_text` — Generate UI screen from prompt
- `edit_screens` — Edit existing screen with prompt
- `get_screen` — Retrieve screen HTML + screenshot
- `list_projects` — List all projects
- `createDesignSystem` — Create design system tokens
- `listDesignSystems` — List design systems
- `variants` — Generate design variants with creative range

## 100-Tool Ceiling Management

The Antigravity editor enforces a **hard 100-tool limit** across all connected MCP servers.

Current allocation:
| Server | Tools | Notes |
|--------|-------|-------|
| StitchMCP | ~12 | Design generation |
| chrome-devtools-mcp | ~25 | Browser testing |
| firebase-mcp-server | ~45 | Full Firebase suite |
| google-developer-knowledge | ~3 | Doc search |
| sequential-thinking | ~1 | Reasoning |
| **Total** | **~86** | **14 tools headroom** |

To add more servers, use `disabledTools` array in the config to selectively disable unused tools from existing servers.

## Prompt Repetition Scope

Per arXiv 2512.14982 (Leviathan, Kalman, Matias — Google Research):

- **APPLY TO**: Oracle Studio stages, CounselConduit model_router, Vent Mode, Autoresearch Triad
- **DO NOT APPLY TO**: Reasoning/thinking models (Gemini thinking, Claude extended thinking, DeepSeek-R1)
- **Effect**: 1–8% accuracy boost with zero additional output tokens or latency
