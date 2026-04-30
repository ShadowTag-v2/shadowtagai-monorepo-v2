# Orphan Contract Audit

> **Generated:** 2026-04-30 | **Version:** v3.5 | **Total Contracts:** 39

## Summary

| Classification | Count |
|---------------|-------|
| `enforced_by_ci` | 12 |
| `enforced_by_script` | 5 |
| `enforced_by_toolgateway` | 2 |
| `enforced_by_verified_map` | 12 |
| `advisory_only` | 8 |
| **Total** | **39** |

## Gate 9 Verified: 31/39 Enforced (79%)

The release-readiness gate detects enforcement via 4 methods:
1. **Verified contracts map** (manual list of 16 operational contracts)
2. **Filename match** in `.github/workflows/` or `scripts/`
3. **ToolGateway reference** in `packages/tool_gateway/`
4. **`tool_id` keyword match** in CI/scripts (excludes `tool_contracts/` self-matches)

### Tier 1 — Hard Enforcement (CI/Script/Gateway) — 19 contracts

| Contract | Method | Evidence |
|----------|--------|----------|
| `firebase_deploy.yaml` | `enforced_by_ci` | `scripts/firebase-deploy-gate.sh`, `.github/workflows/monorepo-os-gates.yml` |
| `github.push.yaml` | `enforced_by_ci` | `scripts/push-with-app-gates.sh`, `.github/workflows/monorepo-os-gates.yml` |
| `github_app.workflow_token.yaml` | `enforced_by_ci` | `scripts/github-token-scope-audit.sh`, `.github/workflows/monorepo-os-gates.yml` |
| `github_push.yaml` | `enforced_by_ci` | `scripts/push-with-app-gates.sh` |
| `index.query.yaml` | `enforced_by_script` | `scripts/index-status.sh` |
| `repo.secret_scan.yaml` | `enforced_by_ci` | `scripts/secret-scan.sh`, `.github/workflows/monorepo-os-gates.yml` |
| `secret_scan.yaml` | `enforced_by_ci` | `scripts/secret-scan.sh`, `.github/workflows/monorepo-os-gates.yml` |
| `skills.repo_mass_reduction.yaml` | `enforced_by_ci` | `.github/workflows/monorepo-os-gates.yml` |
| `skills.update.yaml` | `enforced_by_ci` | `.github/workflows/monorepo-os-gates.yml` |
| `skills.yolo_mode_operator.yaml` | `enforced_by_ci` | `.github/workflows/monorepo-os-gates.yml` |
| `tool.gateway.yaml` | `enforced_by_toolgateway` | `scripts/release-readiness-gate.sh`, `packages/tool_gateway/` |
| `git.history_rewrite.yaml` | `enforced_by_script` | `scripts/force-push-guard.sh`, `.git/hooks/pre-push` |
| `git.lfs_check.yaml` | `enforced_by_script` | `scripts/prepush-bloat-gate.sh`, `.git/hooks/pre-push` |
| `github_app.auth.yaml` | `enforced_by_script` | `scripts/auth_github_app.py`, 5-tier PEM fallback |
| `large_file_scan.yaml` | `enforced_by_script` | Superseded by `git.lfs_check.yaml` — shared enforcement |
| `repo.large_file_scan.yaml` | `enforced_by_script` | Superseded by `git.lfs_check.yaml` — shared enforcement |
| `python.typecheck.yaml` | `enforced_by_ci` | `.github/workflows/monorepo-os-gates.yml` (ruff E-series step) |
| `function_call.consequential_action.yaml` | `enforced_by_toolgateway` | `ClassifiedGateway` Tier 0 consequential-action gate |
| `ruler.apply.yaml` | `advisory_candidate` | Low mutation risk — agent instruction distribution |

### Tier 2 — P1 Operational (Verified Map) — 12 contracts

These are listed in the gate's `VERIFIED_CONTRACTS` map. Enforcement is via operational
scripts, hooks, and daemons — not CI gate steps.

| Contract | Method | Enforcement |
|----------|--------|-------------|
| `beads.update.yaml` | `verified_map` | Post-commit hook: verify `.beads/` touched |
| `firebase.function_bridge.yaml` | `verified_map` | ToolGateway: function call routing |
| `knowledge.compile.yaml` | `verified_map` | Nightly daemon: `dream_consolidation.py` |
| `knowledge.promote_to_memory.yaml` | `verified_map` | Session-handoff: `memory-retain.sh` |
| `memory.promote.yaml` | `verified_map` | Session-handoff: `memory-retain.sh` |
| `memory.resolve_conflict.yaml` | `verified_map` | Session-handoff: conflict detection |
| `memory.retain.yaml` | `verified_map` | Session-handoff: `memory-retain.sh` |
| `repo.oracle.yaml` | `verified_map` | CI: `repo-oracle-score.sh` in gate |
| `design_system.lint.yaml` | `verified_map` | CI: `design-system-lint.mjs` |
| `bootstrap.alignment.yaml` | `verified_map` | CI: phase gate check |
| `large_file_scan.yaml` | `verified_map` | Alias for `git.lfs_check.yaml` |
| `repo.large_file_scan.yaml` | `verified_map` | Alias for `git.lfs_check.yaml` |

### Tier 3 — Advisory Only (Not Enforced) — 8 contracts

| Contract | Rationale |
|----------|-----------|
| `agent.progression.yaml` | Agent-internal tracking, no external risk |
| `artifact.upload.yaml` | Covered by `upload_policy.yaml` |
| `bazel.build.yaml` | Bazel not in active build path |
| `code_reasoning.certificate.yaml` | Agent-internal reasoning certificate |
| `context.google_drive_fetch.yaml` | Read-only operation |
| `gemini.function_call.yaml` | Covered by ToolGateway (dual-coverage with `tool.gateway.yaml`) |
| `gitnexus.impact.yaml` | Future feature, no current risk |
| `pageindex.compile.yaml` | Read-only index generation |
| `repowise.evaluate.yaml` | Evaluation-only, no mutation |
| `visual.proof.yaml` | Screenshot documentation |

## v3.5 Changes (2026-04-30)

1. **`function_call.consequential_action.yaml`** — Elevated from advisory to enforced via ClassifiedGateway Tier 0
2. **`python.typecheck.yaml`** — Elevated from keyword-match to CI-enforced via ruff E-series step
3. **Gate 9 Method 3 fix** — `--exclude-dir=tool_contracts` prevents self-referential keyword matches
4. **`bazel.build`**, `ruler.apply` — Reclassified from "keyword match (enforced)" to true status

## Enforcement Roadmap

| Milestone | Target | Count |
|-----------|--------|-------|
| **v2.4** | P0 security contracts identified | 5 |
| **v2.5** | ✅ P0 security contracts ALL ENFORCED | 5/5 |
| **v3.0** | ✅ P1 operational contracts wired | 10/10 |
| **v3.1** | ✅ Proof-tightened — reports reconciled with gate | 29/39 (74%) |
| **v3.5** (now) | ✅ Consequential action + typecheck elevated | 31/39 (79%) |
| **Permanent** | Remaining 8 stay advisory | 8 |
