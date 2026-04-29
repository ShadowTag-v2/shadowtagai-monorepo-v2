# Contract Coverage Plan — P2/Deprecated Burn-Down

> **Generated:** 2026-04-29 | **Version:** v3.1 | **Gate 9 Status:** 29/39 enforced (74%)

## Overview

Of the 39 total tool contracts, **29** are enforced (detected by Gate 9 via
CI references, script keyword matching, ToolGateway presence, or verified map).

The remaining **10** are advisory-only. This plan governs their disposition.

## v3.5 Elevation Candidates (2 contracts)

These have security-adjacent value and merit promotion to hard enforcement:

| Contract | Current | Proposed | Enforcement Plan |
|----------|---------|----------|-----------------|
| `function_call.consequential_action.yaml` | Advisory | P1 enforced | Wire into ToolGateway action classification. Add CI step to verify all consequential actions have `<!-- GUARDRAIL -->` annotations. |
| `python.typecheck.yaml` | Keyword match | P1 hard enforced | Wire `ruff check --select E` into CI gate. Currently detected via keyword only. |

## Permanent Advisory — No Elevation Needed (8 contracts)

These contracts serve documentation or agent-internal purposes and carry no operational risk:

| Contract | Disposition | Justification |
|----------|-------------|---------------|
| `agent.progression.yaml` | PERMANENT P2 | Agent skill tracking — purely internal metric |
| `artifact.upload.yaml` | PERMANENT P2 | Already covered by `upload_policy.yaml` (dual-coverage) |
| `code_reasoning.certificate.yaml` | PERMANENT P2 | Agent-internal reasoning audit trail |
| `context.google_drive_fetch.yaml` | PERMANENT P2 | Read-only data fetch, no mutation risk |
| `gemini.function_call.yaml` | PERMANENT P2 | Covered by ToolGateway (dual-coverage with `tool.gateway.yaml`) |
| `gitnexus.impact.yaml` | PERMANENT P2 | Future feature — no current code path |
| `pageindex.compile.yaml` | PERMANENT P2 | Read-only index generation, no side effects |
| `repowise.evaluate.yaml` | PERMANENT P2 | Evaluation-only, no state mutation |

> **Note:** `visual.proof.yaml` was reclassified from P2 to the advisory tier.
> It documents screenshot provenance — zero execution risk.

## Duplicate Consolidation (Already Done in v3.0)

These two contracts have been consolidated into `git.lfs_check.yaml`:
- `large_file_scan.yaml` — flagged as superseded in v3.0
- `repo.large_file_scan.yaml` — flagged as superseded in v3.0

They remain in `tool_contracts/` as documentation artifacts and are counted as
"enforced" by keyword match because their `tool_id` is referenced in scripts.

## Projected v3.5 State

| Tier | Count | Change from v3.1 |
|------|-------|-----------------|
| Hard enforcement (CI/script/gateway) | 18 | +2 (elevated from keyword/advisory) |
| Keyword match (passive) | 1 | -2 (elevated) + `ruler.apply.yaml` stays |
| Verified map (operational) | 10 | — |
| Advisory (P2) | 8 | -2 (elevated) |
| Superseded (counted as keyword) | 2 | — |
| **Total enforced (Gate 9)** | **31/39** | +2 |

## Acceptance Criteria for v3.5

- [ ] `function_call.consequential_action.yaml` wired to ToolGateway classification
- [ ] `python.typecheck.yaml` wired to `ruff check --select E` in CI
- [ ] Orphan report regenerated showing 31/39
- [ ] Release readiness gate passes with 0 failures
- [ ] All duplicate contracts annotated with `# SUPERSEDED BY: <canonical>` header

---

*Plan generated as part of Monorepo OS v3.1 proof-tightening.*
