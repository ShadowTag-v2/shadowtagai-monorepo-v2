# Monorepo OS — Unified Operating System

> No agent action touches source truth until it has passed through graph truth,
> build truth, safety truth, execution truth, and evidence truth.

## Architecture

```text
Monorepo OS
  ├── Source Truth           Git-tracked canonical code only
  ├── Artifact Truth         GCS/Releases/LFS-by-exception, with manifests
  ├── Build Truth            Bazel + BEP
  ├── Execution Truth        Dagger (future) / scripts (current)
  ├── Safety Truth           ToolGateway contracts + Betterleaks
  ├── Evidence Truth         OTel + .agent/evidence/ + BEP JSON
  ├── Push Truth             GitHub App short-lived tokens + preflight gates
  ├── Memory Truth           .memory/ atoms + events.ndjson
  ├── Task Truth             .beads/ issues + session ledger
  └── Client Action Truth    Firebase Tool Bridge — registry + gate + evidence
```

## Subsystem Registry

| Subsystem | Location | Git-Tracked | Purpose |
|-----------|----------|-------------|---------|
| **Beads** | `.beads/` | issues.jsonl only | Task graph, work ledger, lint events |
| **Memory** | `.memory/` | atoms + events | Knowledge atoms, doctrine ledger |
| **ToolGateway** | `tool_contracts/` | yes | Action contracts with preconditions |
| **Ruler** | `.ruler/` | yes | Agent instruction propagation |
| **GitNexus** | `.gitnexus/` | no (cache) | Agent impact graph |
| **Push Gates** | `scripts/push-*` | yes | Outbound safety artery |
| **Evidence** | `.agent/evidence/` | reports only | Flight recorder |
| **Index Fabric** | `index_policy.yaml` | yes | Multi-index routing |
| **Upload Policy** | `upload_policy.yaml` | yes | Two-lane upload doctrine |
| **Firebase Tool Bridge** | `packages/firebase_tool_bridge/` | yes | Client Action Truth — function registry, confirmation gate, evidence |

## Core Doctrine

### Files Are Truth; SQLite Is Cache

Knowledge atoms live as Markdown with YAML frontmatter. SQLite databases
(`.beads/beads_index.sqlite`, `.beads/temporal.db`) are **rebuildable indexes**.
`events.ndjson` and `issues.jsonl` are the **authoritative mutation logs**.

### Track Truth Files. Ignore Caches. Record Every Mutation. Rebuild Indexes.

```text
Git tracks:
  - .memory/atoms/**/*.md          (knowledge atoms)
  - .memory/events.ndjson          (mutation log)
  - .beads/issues.jsonl            (task ledger)
  - tool_contracts/**              (action contracts)
  - .ruler/                        (instruction propagation)
  - .agent/evidence/**/*.yaml      (evidence reports)
  - index_policy.yaml              (index fabric)
  - upload_policy.yaml             (upload doctrine)

Git ignores:
  - .beads/beads_index.sqlite      (rebuildable)
  - .beads/temporal.db             (rebuildable)
  - .beads/*.log                   (ephemeral daemon output)
  - .beads/firebase-sa.json        (secret)
  - .memory/cache/                 (rebuildable)
  - .gitnexus/                     (rebuildable)
```

### Every Mutation Is Logged

Every knowledge atom creation, update, or archival is appended to
`.memory/events.ndjson`. Every tool gateway check is appended to
`.beads/issues.jsonl`. These logs are the authoritative record.

### Indexes Are Routed, Not Monolithic

No single index is total truth. See `index_policy.yaml` for the routing
fabric. The agent uses the correct index for the correct question:

| Question | Primary Index | Fallback |
|----------|--------------|----------|
| Symbol definition | SCIP | GitNexus → ripgrep |
| Impact analysis | GitNexus | Bazel rdeps → SCIP refs |
| Build dependencies | Bazel query | GitNexus imports |
| Text search | Zoekt | ripgrep |
| Architecture docs | RAG | docs search |

## Health Verification

Run `scripts/monorepo-health-loop.sh` to verify all subsystems:

```bash
bash scripts/monorepo-health-loop.sh
```

This checks:
1. `.beads/issues.jsonl` exists and is valid NDJSON
2. `.memory/events.ndjson` exists and is valid NDJSON
3. `.ruler/ruler.toml` exists and parses
4. `tool_contracts/` has at least the core contracts
5. `index_policy.yaml` exists
6. `upload_policy.yaml` exists
7. Git working tree cleanliness
8. Betterleaks/Gitleaks availability
9. Buildifier availability
10. Push gate script availability

## Integration Points

### Beads → Memory
When a Beads issue is resolved, the resolution becomes a knowledge atom in
`.memory/atoms/`. The creation event is logged to `.memory/events.ndjson`.

### Memory → ToolGateway
Knowledge atoms inform tool contract preconditions. Before a tool executes,
the gateway checks if relevant doctrine exists in `.memory/atoms/`.

### ToolGateway → Push Gates
`scripts/push-with-app-gates.sh` enforces all tool contracts before pushing:
secret scan, bloat gate, lint, and auth verification.

### Ruler → Agent Configs
`ruler apply` propagates `.ruler/AGENTS.md` to all agent-specific config
locations. The `.gitignore` already excludes generated Ruler output files.

### Evidence → Beads
Evidence reports from `.agent/evidence/` are referenced in Beads issues.
Every push attempt records evidence in `.agent/evidence/push/`.

### Client Action Truth (Firebase Tool Bridge)
Firebase AI Logic function calls flow through the Tool Bridge:

```text
Model proposes → FunctionRegistry validates → ConfirmationGate checks risk
  → App callable executes → EvidenceLogger records → SDK returns to model
```

- **Registry** (`registry.py`): Whitelists functions with `RiskTier` classification
- **Bridge** (`bridge.py`): Dispatch core — validates, gates, executes, logs
- **Evidence** (`evidence.py`): Append-only NDJSON to `.agent/evidence/function_calls.ndjson`
- **Contract**: `tool_contracts/firebase.function_bridge.yaml` governs behavior
- HIGH/CRITICAL risk functions require user confirmation before execution
- Args are SHA-256 hashed in evidence — raw args are NEVER stored

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-04-27 | Initial Monorepo OS integration |
| v1.1 | 2026-04-27 | Phase 6: BUILD coverage complete (12 targets), shield go_test, .mypy_cache gitignore, 60 GiB disk recovery |
| v1.2 | 2026-04-27 | Phase 6 finalized: 27.3 GiB reclaimed (archive/, .gitnexus/, .mypy_cache/), Go 6/6 + Python 201/201 pass, Bazel 14 targets resolved, heartbeat 11/0/1, 3 new quality-gate beads seeded (ISSUE-014–016) |
| v1.3 | 2026-04-27 | Client Action Truth: Firebase Tool Bridge implemented (bridge.py + registry.py + evidence.py), BUILD.bazel + 22-test suite, ConfirmationProvider gate for HIGH/CRITICAL risk, hook system for extensibility |
| v1.4 | 2026-04-27 | Beads capture, guardian patch, CI drift gates, MIRAS memory atoms, ADR-0006 VPC egress |
| v1.5 | 2026-04-27 | Cross-reference: 8 operator invariants (104,111,112,121,129,131,136,137), 4 enforcement scripts |
| v1.6 | 2026-04-27 | Governance completion: Invariants #113 (Autolint Scope Boundary) and #114 (Artifact Manifest Requirement) added. 10 invariants total. Memory atoms wired. Upload subsystem fully governed. |
| v1.7 | 2026-04-27 | Gap closure: Invariants #105 (History Bloat), #115 (Secret Scanner Succession), #138 (External Repos Mirror), #139 (SkillOps Governed), #140 (Boot Probes Read-Only) added. 15 invariants total, 17 memory atoms. SkillOps, Repo Oracle, and Clone Yard verified operational. |
