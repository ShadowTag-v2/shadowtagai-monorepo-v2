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

## Companion Skills (Constitution v3)

Three skills extracted from Cor.Constitution v3, integrated into the Fleet Vanguard doctrine:

### 1. Google AI Mode Research (`google-ai-mode-research`)
**Path:** `skills/google-ai-mode-research/SKILL.md`
**Trigger:** Before any complex research query where `search_web` or Developer Knowledge MCP returns insufficient results.
**Protocol:** Navigate to google.com → enter query → switch to AI Mode tab → auto-prompt "yes" 9× → extract fully-developed response.
**Integration:** Slot #3 in the Doctrinal Acquisition hierarchy (after Dev Knowledge API and KIs, before raw web search).

### 2. ROC Drill Rehearsal (`roc-drill-rehearsal`)
**Path:** `skills/roc-drill-rehearsal/SKILL.md`
**Trigger:** Before ANY critical operation — deployments, migrations, auth/payment changes, infra provisioning.
**Protocol:** 4-phase military rehearsal: Back-Brief (state intent) → Rock Drill (simulate logic flow) → PCC/PCI (pre-combat checks) → Cross LD (execute only when verified).
**Integration:** Mandatory gate for all STATE B (Clutch) operations. Uses `sequential-thinking` MCP for Phase 2 simulation.

### 3. Doctrinal Acquisition Protocol (`doctrinal-acquisition`)
**Path:** `skills/doctrinal-acquisition/SKILL.md`
**Trigger:** Before any decision based on external knowledge. ALL decisions must cite verified sources.
**Protocol:** 6-tier verification hierarchy: Developer Knowledge API → KIs → Google AI Mode → GCloud Docs → GitHub → Web Search. Refresh cycles: 1 month (volatile), 6 months (stable).
**Integration:** Wraps the Velocity Protocol (K.4) combining all three research protocols for maximum speed. Motto: "Research Once → Save to Bead → Never Re-invent."

## Operational Protocols (from live-engine / toolbelt / shadowtag-laws)

Gap analysis of `.agent/workflows/live-engine.md`, `.agent/docs/toolbelt.md`, and `.agent/rules/shadowtag-laws.md` identified three protocols NOT previously captured in GEMINI.md or skills:

### 4. Session Init Ritual (`/omega-loop` + `/live-engine`)
**Source:** `live-engine.md` §Environment Setup, `shadowtag-laws.md` §0
**Trigger:** Start of every session — before any task work.
**Protocol:**
1. Set env: `GCP_PROJECT_ID=shadowtag-omega-v4`
2. Verify gcloud ADC: `gcloud auth list` (check active account)
3. Start heartbeat: `scripts/omega_auth_daemon.py` (token refresh every 3 min)
4. Sovereign memory sync: `ingest_memory_snapshots.py` (async, non-blocking)
5. Check KIs + beads for ready work
**Note:** `BRAIN_DIR` is per-conversation (`~/.gemini/antigravity/brain/<conversation-id>`), NOT hardcoded.

### 5. Beads Protocol (Institutional Memory)
**Source:** `shadowtag-laws.md` §5
**Trigger:** Start of session (fetch ready work), on bug discovery, on task completion.
**Protocol:**
- **Session Start:** Run `python tools/beads_core.py` to fetch "Ready Work" — never ask "What's next?"
- **Bug Discovery:** Do NOT fix immediately. CREATE a Beads issue via `beads_core.py`, continue current task.
- **Task Completion:** UPDATE Beads status to `closed` with fix summary.
- **Conflict:** If user contradicts Beads plan → ask for confirmation to update.
**Integration:** Beads are the institutional memory layer. KIs are curated distillations. Both persist across sessions.

### 6. Auto-Error-Repair Pipeline
**Source:** `shadowtag-laws.md` §0.3
**Trigger:** Any lint/type/test error during execution.
**Protocol:**
- On error → run `python scripts/auto_error_repair.py` (no approval needed)
- Provider ladder: `gemini` (default) → `openai` → `claude` (future stubs)
- Model: `gemini-3.1-flash-lite-preview` (updated from stale `gemini-2.0-pro` ref)
- Coverage target: ≥98% always, Judge #6 enforced
**Anti-pattern:** Never leave a broken build state. Auto-repair restores it.

## Stale Reference Fixes

The following stale references were identified in the source files:

| File | Stale | Current |
|------|-------|---------|
| `shadowtag-laws.md` §0.3 | `gemini-2.0-pro` | `gemini-3.1-flash-lite-preview` |
| `shadowtag-laws.md` §0 | Hardcoded `BRAIN_DIR` | Per-conversation `~/.gemini/antigravity/brain/<id>` |
| `toolbelt.md` §0 | Hardcoded `BRAIN_DIR` | Per-conversation |
| `live-engine.md` §Environment | `MEGA_PERMA_BRAIN` | Per-conversation |

## Governance Lineage (from Cor.Brain Audit)

Gap analysis of the Cor.Brain Omni-Brain Index (64 plans, 46 walkthroughs, 73 tasks = 183 historical shards) identified 5 operational patterns not previously captured:

### 7. Omni-Brain Lineage Audit
**Source:** Cor.Brain §1 "Omni-Brain Index Review"
**Trigger:** Monthly, or when Dream Consolidation daemon detects divergence.
**Protocol:** Inventory all historical implementation plans, walkthroughs, and task matrices. Verify each maps to a current KI, active skill, or archived bead. Flag orphaned shards for consolidation or deletion.
**Tooling:** `mega_brain_compiler.py` generates the master index; Dream Consolidation daemon runs the nightly prune cycle.

### 8. Thread Recovery / Four-Corners Audit
**Source:** Cor.Brain "Exhaustive Four-Corners Thread Audit — Definitive Recovery"
**Trigger:** After any agent context loss, session crash, or when KI summaries show gaps.
**Protocol:** Exhaustively scan all conversation logs (`brain/<id>/`) for unrecovered plans, walkthroughs, and decisions. Recover actionable items into KIs. Tag recovered items with `[RECOVERED]` provenance.
**Anti-pattern:** Never assume context persisted — verify against logs.

### 9. Apex Synchronization Ceremony
**Source:** Cor.Brain "Execution Plan: The Apex Synchronization"
**Trigger:** End of any major work session, before `f1 gca`.
**Protocol (5 steps):**
1. **Index:** Verify all session artifacts are indexed in KIs
2. **Invariants Check:** Confirm GEMINI.md + AGENTS.md immutable zones are unchanged
3. **Janitor:** Run `scripts/finish_changes.py` (formatter + index.lock clear + staging)
4. **Auth Push:** `git push` via GitHub App JWT (SSH primary, `scripts/auth_github_app.py`)
5. **Pipeline Ignite:** Verify daemon fleet is running (Dream Consolidation, Loop Steward, KAIROS)
**Integration:** Combines ROC Drill Phase 4 (Cross LD) with Session Init in reverse. The "lock" to Session Init's "unlock."

## God Mode Operations & Workspace Isolation

### 10. God Mode Admin (`god_mode_admin.py`)
**Source:** toolbelt §4, live-engine §God Mode
**Location:** `scripts/god_mode_admin.py`
**Launch:**
```bash
export GCP_PROJECT_ID='shadowtag-omega-v4'
/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.venv/bin/python scripts/god_mode_admin.py
```
**Full Command Reference:**

| Command | Purpose |
|---------|---------|
| `help` | List all commands |
| `status` | Show engine state, queue depth, scheduled jobs |
| `sync` | Git pull --ff-only + repo sync |
| `shell <cmd>` | Execute arbitrary shell command |
| `json {"task":"..."}` | Submit structured task payload |
| `commit` | Stage + commit current changes |
| `rollback` | Revert last commit |
| `memw` | Write to persistent memory |
| `mems` | Search persistent memory |
| `artifact` | Create/manage artifacts |
| `stop` | Graceful shutdown |

**Background jobs:** `sync_repo` (every 600s), `health_snapshot` (every 120s)
**Dependency note:** Install `asyncpg` for full capability: `pip install asyncpg`

### 11. GCA God Mode Bridge (`gca_god_mode_bridge.py`)
**Source:** Historical session log
**Location:** `tools/gca_god_mode_bridge.py`
**Protocol:** Wraps God Mode admin in a non-interactive bridge for agent tool calls:
```bash
python3 tools/gca_god_mode_bridge.py status
python3 tools/gca_god_mode_bridge.py json '{"task": "do something"}'
```
**Mechanics:** Starts Velocity Engine → transmits payload → reads output → graceful shutdown (no hang).

### 12. Workspace Isolation Config
**Source:** Historical session log
**Workspace file:** `Monorepo-Uphillsnowball/pnkln.code-workspace`
**Strict mode config:** `~/.antigravity/config.json`
```json
{
  "strictMode": true,
  "allowNonWorkspaceFileAccess": false
}
```
**Effect:** Agent ignores files outside workspace context + `.gitignore` contents. Eliminates path-traversal jumps.
**Rule:** Always launch Antigravity pointing to this workspace, not a parent directory.

### 13. Service Account Registry
**Source:** live-engine.md, GEMINI.md secrets doctrine

| Account | Purpose |
|---------|---------|
| `shadowtag-core-run-sa@shadowtag-omega-v4.iam.gserviceaccount.com` | Cloud Run services (primary) |
| `counselconduit-sa@shadowtag-omega-v4.iam.gserviceaccount.com` | CounselConduit prod |
| `counselconduit-staging-sa@shadowtag-omega-v4.iam.gserviceaccount.com` | CounselConduit staging |
| `767252945109-compute@developer.gserviceaccount.com` | Compute default (token refresh every 3 min) |

### 14. MCP Toolbox Config
**Source:** Historical session log
**Path:** `/Users/pikeymickey/aiyou-stack/ShadowTag-v2/database_tools.yaml`
**UI Action:** When prompted for "Tools Config Path" in the UI, paste the absolute path above.
