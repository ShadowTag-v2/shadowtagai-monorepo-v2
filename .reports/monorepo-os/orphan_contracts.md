# Orphan Contract Audit

> **Generated:** 2026-04-28 | **Total Contracts:** 39

## Summary

| Classification | Count |
|---------------|-------|
| `enforced_by_ci` | 8 |
| `enforced_by_script` | 5 |
| `enforced_by_toolgateway` | 1 |
| `advisory_only` | 25 |
| **Total** | **39** |

## Enforced Contracts (14/39)

| Contract | Classification | Evidence |
|----------|---------------|----------|
| `github.push.yaml` | `enforced_by_ci` | scripts/push-with-app-gates.sh, .github/workflows/monorepo-os-gates.yml |
| `github_push.yaml` | `enforced_by_script` | scripts/push-with-app-gates.sh |
| `index.query.yaml` | `enforced_by_script` | scripts/index-status.sh |
| `repo.secret_scan.yaml` | `enforced_by_ci` | scripts/secret-scan.sh, .github/workflows/monorepo-os-gates.yml |
| `secret_scan.yaml` | `enforced_by_ci` | scripts/secret-scan.sh, .github/workflows/monorepo-os-gates.yml |
| `skills.repo_mass_reduction.yaml` | `enforced_by_ci` | .github/workflows/monorepo-os-gates.yml |
| `skills.update.yaml` | `enforced_by_ci` | .github/workflows/monorepo-os-gates.yml |
| `skills.yolo_mode_operator.yaml` | `enforced_by_ci` | .github/workflows/monorepo-os-gates.yml |
| `tool.gateway.yaml` | `enforced_by_toolgateway` | scripts/release-readiness-gate.sh, packages/tool_gateway/ |
| `firebase_deploy.yaml` | `enforced_by_ci` | scripts/firebase-deploy-gate.sh, .github/workflows/monorepo-os-gates.yml |
| `git.history_rewrite.yaml` | `enforced_by_script` | scripts/force-push-guard.sh, .git/hooks/pre-push |
| `git.lfs_check.yaml` | `enforced_by_script` | scripts/prepush-bloat-gate.sh, .git/hooks/pre-push |
| `github_app.auth.yaml` | `enforced_by_script` | scripts/auth_github_app.py, 5-tier PEM fallback |
| `github_app.workflow_token.yaml` | `enforced_by_ci` | scripts/github-token-scope-audit.sh, .github/workflows/monorepo-os-gates.yml |

## Advisory Contracts — Priority Triage

### P0 — Security/Safety ✅ ALL ENFORCED (v2.5)

| Contract | Status | Enforcement |
|----------|--------|-------------|
| `firebase_deploy.yaml` | ✅ `enforced_by_ci` | `scripts/firebase-deploy-gate.sh` → CI step |
| `git.history_rewrite.yaml` | ✅ `enforced_by_script` | `scripts/force-push-guard.sh` → pre-push hook |
| `git.lfs_check.yaml` | ✅ `enforced_by_script` | `scripts/prepush-bloat-gate.sh` → pre-push hook |
| `github_app.auth.yaml` | ✅ `enforced_by_script` | `scripts/auth_github_app.py` (5-tier PEM fallback) |
| `github_app.workflow_token.yaml` | ✅ `enforced_by_ci` | `scripts/github-token-scope-audit.sh` → CI step |

### P1 — Operational Integrity (target v3.0)

| Contract | Risk | Wiring Target |
|----------|------|---------------|
| `beads.update.yaml` | Stale task tracking | Post-commit hook: verify `.beads/` touched |
| `firebase.function_bridge.yaml` | Unvetted function calls | ToolGateway: function call routing |
| `knowledge.compile.yaml` | Stale KIs | Nightly daemon: `dream_consolidation.py` |
| `knowledge.promote_to_memory.yaml` | Lost context | Session-handoff: `memory-retain.sh` |
| `memory.promote.yaml` | Lost atoms | Session-handoff: `memory-retain.sh` |
| `memory.resolve_conflict.yaml` | Conflicting memory | Session-handoff: conflict detection |
| `memory.retain.yaml` | Ephemeral state | Session-handoff: `memory-retain.sh` |
| `large_file_scan.yaml` | Duplicate of `git.lfs_check` | Consolidate with `git.lfs_check.yaml` |
| `repo.large_file_scan.yaml` | Duplicate of above | Consolidate with `git.lfs_check.yaml` |
| `repo.oracle.yaml` | Stale oracle score | CI: `repo-oracle-score.sh` in gate |
| `design_system.lint.yaml` | Design drift | CI: `design-system-lint.mjs` |
| `bootstrap.alignment.yaml` | Misaligned bootstraps | CI: phase gate check |

### P2 — Advisory Documentation (acceptable as-is)

| Contract | Rationale |
|----------|-----------|
| `agent.progression.yaml` | Agent-internal tracking, no external risk |
| `artifact.upload.yaml` | Covered by `upload_policy.yaml` |
| `bazel.build.yaml` | Bazel not in active build path |
| `code_reasoning.certificate.yaml` | Agent-internal reasoning certificate |
| `context.google_drive_fetch.yaml` | Read-only operation |
| `function_call.consequential_action.yaml` | Covered by ToolGateway |
| `gemini.function_call.yaml` | Covered by ToolGateway |
| `gitnexus.impact.yaml` | Future feature, no current risk |
| `pageindex.compile.yaml` | Read-only index generation |
| `python.typecheck.yaml` | Advisory lint, not safety-critical |
| `repowise.evaluate.yaml` | Evaluation-only, no mutation |
| `ruler.apply.yaml` | Agent instruction distribution |
| `visual.proof.yaml` | Screenshot documentation |

## Enforcement Roadmap

| Milestone | Target | Count |
|-----------|--------|-------|
| **v2.4** | P0 security contracts identified | 5 |
| **v2.5** (now) | ✅ P0 security contracts ALL ENFORCED | 5/5 |
| **v3.0** | P1 operational contracts enforced | 12 |
| **v3.5** | All non-P2 enforced | 12 |
| **Permanent** | P2 stays advisory | 13 |
