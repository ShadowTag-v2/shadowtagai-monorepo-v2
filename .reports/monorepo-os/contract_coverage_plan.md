# Contract Coverage Plan — P2/Deprecated Burn-Down

> **Generated:** 2026-04-29 | **Version:** v3.1 | **Remaining:** 13 advisory contracts

## Overview

Of the 39 total tool contracts, **26** are enforced (14 hard + 12 P1 operational).
This plan covers the remaining **13 P2 advisory** contracts and their disposition.

## P2 Elevation Analysis

### Candidates for v3.5 Elevation (2 contracts)

These have security-adjacent value and merit promotion to enforced status:

| Contract | Current | Proposed | Enforcement Plan |
|----------|---------|----------|-----------------|
| `function_call.consequential_action.yaml` | P2 advisory | P1 enforced | Wire into ToolGateway action classification. Add CI step to verify all consequential actions have `<!-- GUARDRAIL -->` annotations. |
| `python.typecheck.yaml` | P2 advisory | P1 enforced | Wire `ruff check --select E` into CI. mypy/pyright optional but ruff type errors are low-cost high-value. |

### Permanent P2 — No Elevation Needed (11 contracts)

These contracts serve documentation or agent-internal purposes and carry no operational risk:

| Contract | Disposition | Justification |
|----------|-------------|---------------|
| `agent.progression.yaml` | PERMANENT P2 | Agent skill tracking — purely internal metric |
| `artifact.upload.yaml` | PERMANENT P2 | Already covered by `upload_policy.yaml` (dual-coverage) |
| `bazel.build.yaml` | DEPRECATED | Bazel not in active build path; Keep contract for future reference |
| `code_reasoning.certificate.yaml` | PERMANENT P2 | Agent-internal reasoning audit trail |
| `context.google_drive_fetch.yaml` | PERMANENT P2 | Read-only data fetch, no mutation risk |
| `gemini.function_call.yaml` | PERMANENT P2 | Covered by ToolGateway (dual-coverage with tool.gateway.yaml) |
| `gitnexus.impact.yaml` | PERMANENT P2 | Future feature — no current code path |
| `pageindex.compile.yaml` | PERMANENT P2 | Read-only index generation, no side effects |
| `repowise.evaluate.yaml` | PERMANENT P2 | Evaluation-only, no state mutation |
| `ruler.apply.yaml` | PERMANENT P2 | Agent instruction distribution — write-once, read-many |
| `visual.proof.yaml` | PERMANENT P2 | Screenshot documentation — no execution risk |

## Duplicate Consolidation (Already Done)

These two contracts have been consolidated into `git.lfs_check.yaml`:
- `large_file_scan.yaml` — flagged as superseded in v3.0
- `repo.large_file_scan.yaml` — flagged as superseded in v3.0

They remain in `tool_contracts/` as documentation artifacts but are counted as
"enforced" because the functionality is covered by the canonical `git.lfs_check.yaml`.

## Projected v3.5 State

| Tier | Count | Change from v3.1 |
|------|-------|-----------------|
| Hard enforcement (CI/script/gateway) | 14 | — |
| P1 operational (CI presence) | 14 | +2 (elevated from P2) |
| P2 advisory | 11 | -2 (elevated) |
| **Total enforced** | **28/39** | +2 |

## Acceptance Criteria for v3.5

- [ ] `function_call.consequential_action.yaml` wired to ToolGateway classification
- [ ] `python.typecheck.yaml` wired to `ruff check --select E` in CI
- [ ] Orphan report regenerated showing 28/39
- [ ] Release readiness gate passes with 0 failures
- [ ] All duplicate contracts annotated with `# SUPERSEDED BY: <canonical>` header

---

*Plan generated as part of Monorepo OS v3.1 proof-tightening.*
