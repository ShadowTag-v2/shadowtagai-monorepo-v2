# ANTIGRAVITY_CONTROL_PLANE.md — v2.0

> **Status:** LOCKED — Canonical control plane specification for the UphillSnowball monorepo.
>
> **Last updated:** 2026-04-27

---

## Core Thesis

**Antigravity is a control plane, not just another editor.**

It is a VS Code fork with agent-first capabilities. The fastest path is not "rewrite the IDE."
The path is:

1. **Stabilize** the VS Code-compatible base
2. **Harden** the agent loop
3. **Make remote compute first-class**
4. **Make every agent action observable**
5. **Make every agent action reversible**

---

## Pillar 1 — VS Code Base Stabilization

### Entry Point

```
pnkln.code-workspace
```

This is the ONLY authorized workspace entry point. All multi-root folders, settings, and
extension recommendations flow from this file.

### Extension Compatibility

Antigravity inherits the full VS Code extension ecosystem. Extensions are additive capabilities,
not replacements for MCP servers. If an MCP server can perform the operation, the MCP server wins.

### Settings Hierarchy

| Layer | File | Scope |
|-------|------|-------|
| Workspace | `pnkln.code-workspace` | Multi-root layout, shared settings |
| Project | `.vscode/settings.json` | Per-root overrides |
| User | `~/.config/Code/User/settings.json` | Global defaults |

### Multi-Root Layout

The workspace is organized as one control plane with multiple live roots:

- `/` — Monorepo root (canonical)
- `apps/kovelai` — KovelAI (Firebase Hosting, Next.js 16)
- `apps/counselconduit` — CounselConduit (Cloud Run, FastAPI)
- `labs/uphillsnowball` — R&D (Apple Silicon, local-only)

---

## Pillar 2 — Agent Loop Hardening

### Anti-Theater Protocol

"Agent theater" is the #1 failure mode: plans claiming files exist, scripts failing silently,
false confidence reports. The antidote is **verification at every step**.

| Checkpoint | Enforcement |
|-----------|-------------|
| File existence | `view_file` or `list_dir` before claiming a file exists |
| Build success | `run_command` with exit code check, not just "I ran the command" |
| Test pass | Actual test output parsed, not assumed |
| Deploy success | Live URL verified via `chrome-devtools-mcp`, not assumed |
| Auth validity | Token expiry checked before push, not assumed |

### MCP-First Routing

If an operation CAN be performed by an MCP server, it MUST be.

| Operation | MCP Server | Fallback |
|-----------|-----------|----------|
| Google API docs | `google-developer-knowledge` | NEVER `search_web` |
| Firebase deploy | `firebase-mcp-server` | NEVER raw terminal |
| Screenshots/DOM | `chrome-devtools-mcp` | NEVER external tools |
| Design systems | `StitchMCP` | NEVER hand-coded tokens |
| Architecture reasoning | `sequential-thinking` | NEVER ad-hoc lists |

### Pre-Action Memory Gate

Before EVERY action:

1. Check KI summaries for existing patterns
2. Verify the target MCP server is UP (Fleet Vanguard)
3. Establish temporal anchor (`git log -n 1`)
4. Confirm auth state (GitHub, Firebase, GCP)

### Post-Edit Validation Loop

After EVERY file modification:

1. `ruff check --fix` + `ruff format` (Python)
2. `biome check --fix` (TypeScript/JS)
3. Verify no new lint errors introduced
4. If lint regression: temporal rollback (`git checkout -- <file>`)

### Execution State Machine

| State | Trigger | Behavior |
|-------|---------|----------|
| **A — Pure YOLO** | Standard work, known patterns | Execute unconstrained, parallelize |
| **B — Clutch** | Force-push, migrations, auth changes | Plan → lock → research → bound → log → disengage |

---

## Pillar 3 — Remote Compute

### Compute Topology

```
┌─────────────────────────────────────────────────┐
│              ANTIGRAVITY CONTROL PLANE           │
│         (VS Code fork + Agent + MCP Fleet)       │
├─────────────────────────────────────────────────┤
│                                                  │
│  LOCAL (Apple Silicon M-series)                  │
│  ├─ ANE: 10.22 TOPS neural inference             │
│  ├─ MLX: Sovereign KV-cache slab architecture    │
│  └─ CPU: Python 3.14.3, .NET 11.0               │
│                                                  │
│  GOOGLE CLOUD                                    │
│  ├─ Cloud Run: CounselConduit API                │
│  ├─ Firestore: Document database                 │
│  ├─ Cloud Tasks: Job queue (BullMQ BANNED)       │
│  ├─ Secret Manager: All secrets                  │
│  └─ Firebase Hosting: KovelAI, ShadowTagAI       │
│                                                  │
│  COLAB (on-demand)                               │
│  ├─ GPU/TPU: Training, heavy inference           │
│  └─ Notebook: Interactive experimentation        │
│                                                  │
└─────────────────────────────────────────────────┘
```

### Compute Dispatch Rules

| Workload | Target | Rationale |
|----------|--------|-----------|
| Lint, format, git ops | Local CPU | Sub-second latency |
| ML inference (<7B params) | Local ANE/MLX | Zero egress, sovereign |
| ML inference (>7B params) | Colab GPU | Cost-effective burst |
| Production API | Cloud Run | Managed, autoscaling |
| Document storage | Firestore | Native Firebase integration |
| Job scheduling | Cloud Tasks | Durable, exactly-once |
| Static hosting | Firebase Hosting | CDN, SSL, custom domains |

---

## Pillar 4 — Observability

### Every Agent Action is Observable

No silent failures. No assumed success. Every action produces a verifiable trace.

#### Beads Audit Trail

```
.beads/
├── issues.jsonl          # Structured issue log (append-only)
├── kairos_heartbeat.json # Daemon heartbeat (5-min cycles)
└── session_pins/         # Active session state
```

Format for `issues.jsonl`:
```json
{"ts": "2026-04-27T07:00:00Z", "type": "lint_fix", "file": "api/routes.py", "detail": "F401 removed unused import"}
```

#### MCP Fleet Status Table

Report at conversation start and after any server failure:

| # | Server | Status | Tools |
|---|--------|--------|-------|
| 1 | StitchMCP | ✅ UP | 12 |
| 2 | chrome-devtools-mcp | ✅ UP | 29 |
| 3 | firebase-mcp-server | ✅ UP | 45 |
| 4 | google-developer-knowledge | ✅ UP | 3 |
| 5 | sequential-thinking | ✅ UP | 1 |

#### Daemon Fleet Monitoring

| Daemon | Script | Health Check |
|--------|--------|-------------|
| Dream Consolidation | `scripts/dream_consolidation.py` | KI count + timestamp |
| Loop Steward | `scripts/loop_steward.py` | Task queue depth |
| COR.KAIROS | `scripts/kairos_daemon.py` | Heartbeat file |
| pnkln-evolve | `scripts/pnkln_evolve.py` | Evolution log |
| Omni-Autolint | `scripts/gca_autolint_daemon.py` | Last push timestamp |

#### Git as Audit Log

Every commit is a trace entry. Conventional Commits format enforced:

```
<type>(<scope>): <description>

Types: feat, fix, chore, docs, refactor, test, ci, perf
Scope: the affected package or module
```

---

## Pillar 5 — Reversibility

### Every Agent Action is Reversible

No destructive operations without explicit human authorization.

#### RULE 00: Immutable Infrastructure

- **No `rm`, `unlink`, or destructive `>`** on existing files
- Archive-only deactivation: `mv <file> _archive_<date>/`
- Full spec: `.agents/RULE_00_IMMUTABLE_INFRASTRUCTURE.md`

#### Temporal Rollback Protocol

If a code change introduces a regression:

1. **Lint regression:** `git checkout -- <file>` (NEVER `git reset --hard`)
2. **Build regression:** Revert the specific commit with `git revert <sha>`
3. **Deploy regression:** Firebase rollback to previous version
4. **Data regression:** Firestore point-in-time recovery

#### Archive-Only Deactivation

When retiring a component:

```bash
# CORRECT — archive
mv component/ archive/legacy_component_$(date +%Y-%m-%d)/

# PROHIBITED — destruction
rm -rf component/  # BANNED
```

---

## Sources of Truth

| Domain | File | Authority |
|--------|------|-----------|
| Workspace structure | `monorepo_manifest.yaml` | CANONICAL |
| Agent behavior | `AGENTS.md` (via `.ruler/`) | CANONICAL |
| Agent shim | `CLAUDE.md` | THIN SHIM |
| MCP configuration | `antigravity-mcp-config.json` | CANONICAL |
| Pricing & architecture | `BUSINESS_CONTEXT_LOCKED.md` | CANONICAL |
| Operational risk | `RISK_REGISTER.md` | CANONICAL |
| Control plane | This document | CANONICAL |

### Fix Order

When truth surfaces conflict, fix in this order:

1. `monorepo_manifest.yaml` (workspace truth)
2. `AGENTS.md` (agent behavior truth)
3. `antigravity-mcp-config.json` (MCP truth)
4. Runtime configuration
5. Product hardening

---

## Secret Handling

- **GCP Secret Manager** is the ONLY production secret store
- `.env` files are **BANNED** (deprecated 2026-04-22)
- Local secrets: `source scripts/load_mcp_secrets.sh`
- MCP config: `${VAR}` references resolved by platform env injection
- NEVER commit secrets to source control

---

## Agent Split

### Antigravity (Primary)

- Agent-first VS Code fork
- YOLO mode (STATE A) for standard operations
- Clutch mode (STATE B) for high-risk operations
- MCP fleet: 5 servers, 90 tools

### Claude Code (Secondary)

- Async reviewer and cross-model coordination
- Governed by CLAUDE.md shim pointing to AGENTS.md
- Not a second control plane

### Cline / Cursor / Others

- Extension-layer agents only
- Must conform to AGENTS.md, monorepo_manifest.yaml, antigravity-mcp-config.json
- Not second control planes

---

## Non-Goals

- No second source of truth for any domain
- No inline secrets in code or config
- No revival of superseded thread artifacts
- No agent theater (claiming success without verification)
- No terminal fallbacks for MCP-capable operations
- No `rm`, `unlink`, or destructive operations without human authorization
