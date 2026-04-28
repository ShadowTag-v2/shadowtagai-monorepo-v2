# Monorepo OS — v2.2

> **Status:** Active | **Version:** 2.2 | **Updated:** 2026-04-28

## Overview

The Monorepo OS is the unified operating system for the ShadowTag-v2/Monorepo-Uphillsnowball
repository. It replaces fragmented tooling with a coherent truth layer architecture where
every operational domain has exactly one canonical source.

## Operator Invariants

Canonical source: `operator_invariants.json` (repo root).

| ID | Name | Enforcement |
|----|------|-------------|
| 104 | Monorepo-Bounced Tool Calls | `packages/tool_gateway/gateway.py` |
| 111 | Two-Lane Upload Doctrine | `upload_policy.yaml`, `scripts/classify-upload-payload.sh` |
| 112 | GitHub App Push Gate | `scripts/auth_github_app.py`, `scripts/push-with-app-gates.sh` |
| 121 | No Markdown Plan Sprawl | Beads (`bd create`), `.memory/atoms/` |
| 129 | Research Wiki Is Synthesis | `knowledge/` vault, KI system |
| 131 | Gate 0 UI Discipline | `tool_contracts/design_system.lint.yaml`, Stitch MCP |
| 136 | Bootstrap Alignment Is Phased | `tool_contracts/bootstrap.alignment.yaml`, Beads |
| 137 | Taste Is A Gate, Not A Vibe | `DESIGN.md`, `tokens.css`, design-taste-frontend skill |

## Truth Layer Architecture

| Truth Layer | Canonical Source | Scripts/Tools |
|-------------|-----------------|---------------|
| **Work Truth** | `.beads/issues.jsonl` | `beads-capture.sh`, `beads-plan.sh`, `beads-sync.sh`, `beads-health.sh` |
| **Operational Memory** | `.memory/atoms/` + `.memory/events.ndjson` | `memory-retain.sh`, `session-handoff.sh` |
| **Research Memory** | `knowledge/` + Obsidian Vault | `dream_consolidation.py`, KI system |
| **Code Truth** | Git + `repo-oracle` | `repo-oracle`, `packages/repo_oracle/` |
| **Build Truth** | Bazel + Buildifier + BEP | `BUILD` files, `bazel-*` symlinks |
| **Design Truth** | `DESIGN.md` + `tokens.css` | `design-system-lint.mjs`, Stitch MCP |
| **Safety Truth** | Tool contracts + `guardian-propose-patch.sh` | `tool_contracts/*.yaml` |
| **Execution Truth** | GitHub Actions + Cloud Tasks | `.github/workflows/`, `temporal/` |
| **Evidence Truth** | `.agent/evidence/` + OTel traces | `record-agent-event.sh` |
| **Push Truth** | GitHub App tokens | `auth_github_app.py`, `finish_changes.py` |
| **Client Action Truth** | Firebase Tool Bridge | `packages/firebase_tool_bridge/` |
| **Command Deck** | AG-UI + Chrome DevTools MCP | Browser subagent, DevTools MCP |

## Beads Task Flow

### Before Coding

```bash
bd sync                           # Refresh from remote
bd ready --json                   # List ready issues
bd show <issue>                   # Read issue plan
# Write/verify issue plan inside Beads:
#   problem_statement, solution_approach, files,
#   acceptance_criteria, dependencies, test_strategy
```

### During Coding

```bash
bd update <issue> --status in_progress
bd create <discovered-issue>       # Unrelated findings
bd link <child> --depends-on <parent>  # Wire dependencies
```

### After Coding

```bash
bd update <issue> --status done
scripts/session-handoff.sh         # Capture handoff state
scripts/finish_changes.py          # Stage, commit, push
```

### Rework

```bash
bd update <issue> --status in_progress  # Reopen
# Add to issue: root_cause, revised_test_plan, completion_notes
bd update <issue> --status done
```

## Memory Architecture

Three-tier memory following MIRAS design (see `docs/research/miras-titans-notes.md`):

```
Working Memory          Episodic Memory              Semantic Memory
┌─────────────────┐    ┌─────────────────────┐      ┌──────────────────┐
│ session_handoff  │    │ .beads/issues.jsonl │      │ .memory/atoms/   │
│ .json            │    │ .memory/events.ndjson│      │ knowledge/ (KIs) │
│ (per-session)    │    │ (append-only)       │      │ (permanent)      │
└─────────────────┘    └─────────────────────┘      └──────────────────┘
        ↑                       ↑                           ↑
    beads-capture.sh     beads-capture.sh          dream_consolidation.py
    session-handoff.sh   record-agent-event.sh     memory-retain.sh
```

## Truth Hierarchy

```
AGENTS.md                    ← Canonical contract
  ├── GEMINI.md              ← Operator invariants
  ├── CLAUDE.md              ← Thin shim
  ├── monorepo_manifest.yaml ← Workspace truth
  ├── antigravity-mcp-config.json ← MCP truth
  ├── BUSINESS_CONTEXT_LOCKED.md  ← Pricing/architecture
  └── RISK_REGISTER.md      ← Operational risk
```

## Execution State Machine

- **STATE A (Pure YOLO):** Standard work, low-ambiguity, automated.
- **STATE B (Clutch):** Architecture shifts, auth changes, migrations.

Transition trigger: `>3 packages affected` OR `auth/payment/migration` scope.

## Script Manifest

| Script | Purpose | LOC |
|--------|---------|-----|
| `auth_github_app.py` | GitHub App JWT push | 196 |
| `finish_changes.py` | Stage + commit + push | 109 |
| `beads-plan.sh` | Create beads-format plan | 172 |
| `beads-capture.sh` | Ingest bead (issue/fact/decision/event) | 105 |
| `beads-sync.sh` | Sync beads state | 6 |
| `beads-health.sh` | Validate beads journal | 6 |
| `session-handoff.sh` | Agent transition manifest | 80 |
| `guardian-propose-patch.sh` | Integrity scanner | 120 |
| `context-fetch-drive.py` | Google Drive context fetcher | 140 |
| `repo-oracle` | Pre-task context retrieval | 83 |
| `skills-audit.sh` | Skill fleet audit | 109 |
| `skills-registry.py` | Skill metadata registry | 182 |
| `clone-external-reference-repos.sh` | External repo yard | 108 |
| `record-agent-event.sh` | OTel event recording | 131 |
| `monorepo-heartbeat.sh` | Health check pulse | 135 |
| `memory-retain.sh` | Persist memory atoms | 6 |
| `drive_fetcher.py` | Drive API fetcher | 67 |
| `omega-loopin.py` | Session bootstrap | 41 |
| `prompt-repeat-wrapper.sh` | arXiv 2512.14982 boost | 111 |
| `write-safe-workspace.sh` | Safe file writer | 140 |
| `dead-code-audit.sh` | Guillotine v9.0 | 46 |
| `classify-upload-payload.sh` | Two-Lane payload classifier | 55 |
| `prepush-bloat-gate.sh` | Pre-push size enforcement | 139 |
| `secret-scan.sh` | Secret leak scanner | 124 |
| `push-with-app-gates.sh` | Gated GitHub App push | 379 |
| `repo-oracle-score.sh` | Truth surface confidence scorer | 105 |
| `daily-truth-report.sh` | Daily governance report generator | 93 |
| `release-readiness-gate.sh` | 8-gate pre-release validator | 157 |

## Clone Yard

**Manifest:** `external_repos/upstream_manifest.yaml` (committed, git-tracked)

| Metric | Value |
|--------|-------|
| Groups | 17 |
| Total repos | 95 |
| Dry-run status | ✅ 95/95 pass |

**Validation (reproducible from clean checkout):**
```bash
python3 -c "import yaml; yaml.safe_load(open('external_repos/upstream_manifest.yaml'))"
scripts/clone-external-reference-repos.sh --dry-run
```

## Contract Coverage

| Classification | Count |
|---------------|-------|
| `enforced_by_ci` | 6 |
| `enforced_by_script` | 2 |
| `enforced_by_toolgateway` | 1 |
| `advisory_only` | 30 |
| **Total** | **39** |

Full audit: `.reports/monorepo-os/orphan_contracts.md`
Each `advisory_only` contract has a Beads issue for enforcement wiring.

## Proof Links

| Proof | Path / Command |
|-------|---------------|
| Clone-yard manifest | `external_repos/upstream_manifest.yaml` |
| Orphan contracts report | `.reports/monorepo-os/orphan_contracts.md` |
| Daily truth report | `.reports/monorepo-os/daily.md` |
| Release readiness report | `.reports/monorepo-os/release-readiness.md` |
| Oracle score report | `.reports/monorepo-os/repo-oracle-score.md` |
| Guardrail audit report | `.reports/skills/guardrail_annotation_audit.md` |
| Triage report | `.reports/skills/unsafe_findings_triage.md` |
| Invariants validation | `python3 -c "import json; json.load(open('operator_invariants.json'))"` |
| Atoms validation | `python3 -c "import json; json.load(open('operator_invariants_atoms.json'))"` |
| CI workflow | `.github/workflows/monorepo-os-gates.yml` |
| SkillOps workflow | `.github/workflows/skillops-audit.yml` |
| Release gate | `scripts/release-readiness-gate.sh` |

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-04-26 | Initial truth layer architecture |
| 1.1 | 2026-04-26 | Added Client Action Truth (Firebase Tool Bridge) |
| 1.2 | 2026-04-27 | Added Beads task flow, memory architecture |
| 1.3 | 2026-04-27 | Script manifest, MIRAS alignment |
| 1.4 | 2026-04-27 | Complete infrastructure audit closure |
| 1.5 | 2026-04-27 | Operator Invariants section, enforcement script manifest |
| 1.6 | 2026-04-27 | Clone yard `upstream_manifest.yaml`, agent_protocols group |
| 1.7 | 2026-04-27 | Command Deck truth layer (AG-UI + Chrome DevTools MCP) |
| 2.0 | 2026-04-28 | DESIGN.md + `tokens.css` Stitch token export for KovelAI |
| 2.1 | 2026-04-28 | Guardrail annotation audit (12/12), Lighthouse A100/BP100/SEO100, 39 ToolGateway contracts |
| 2.2 | 2026-04-28 | Oracle Score engine, Daily Truth Report, Release Readiness Gate (8 gates), CI hardening (+3 steps) |
| 2.3 | 2026-04-28 | Clone-yard manifest committed, orphan contract audit (9/39 enforced, 30 advisory), Proof Links section, reproducibility from clean checkout |
