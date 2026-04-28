# Orphan Contract Audit

> **Generated:** 2026-04-28 | **Total Contracts:** 39

## Summary

| Classification | Count |
|---------------|-------|
| `enforced_by_ci` | 6 |
| `enforced_by_script` | 2 |
| `enforced_by_toolgateway` | 1 |
| `advisory_only` | 30 |
| **Total** | **39** |

## Contract Classification

| Contract | Classification | Evidence |
|----------|---------------|----------|
| `agent.progression.yaml` | `advisory_only` | — |
| `artifact.upload.yaml` | `advisory_only` | — |
| `bazel.build.yaml` | `advisory_only` | — |
| `beads.update.yaml` | `advisory_only` | — |
| `bootstrap.alignment.yaml` | `advisory_only` | — |
| `code_reasoning.certificate.yaml` | `advisory_only` | — |
| `context.google_drive_fetch.yaml` | `advisory_only` | — |
| `design_system.lint.yaml` | `advisory_only` | — |
| `firebase.function_bridge.yaml` | `advisory_only` | — |
| `firebase_deploy.yaml` | `advisory_only` | — |
| `function_call.consequential_action.yaml` | `advisory_only` | — |
| `gemini.function_call.yaml` | `advisory_only` | — |
| `git.history_rewrite.yaml` | `advisory_only` | — |
| `git.lfs_check.yaml` | `advisory_only` | — |
| `github.push.yaml` | `enforced_by_ci` | scripts/push-with-app-gates.sh, .github/workflows/monorepo-os-gates.yml |
| `github_app.auth.yaml` | `advisory_only` | — |
| `github_app.workflow_token.yaml` | `advisory_only` | — |
| `github_push.yaml` | `enforced_by_script` | scripts/push-with-app-gates.sh |
| `gitnexus.impact.yaml` | `advisory_only` | — |
| `index.query.yaml` | `enforced_by_script` | scripts/index-status.sh |
| `knowledge.compile.yaml` | `advisory_only` | — |
| `knowledge.promote_to_memory.yaml` | `advisory_only` | — |
| `large_file_scan.yaml` | `advisory_only` | — |
| `memory.promote.yaml` | `advisory_only` | — |
| `memory.resolve_conflict.yaml` | `advisory_only` | — |
| `memory.retain.yaml` | `advisory_only` | — |
| `pageindex.compile.yaml` | `advisory_only` | — |
| `python.typecheck.yaml` | `advisory_only` | — |
| `repo.large_file_scan.yaml` | `advisory_only` | — |
| `repo.oracle.yaml` | `advisory_only` | — |
| `repo.secret_scan.yaml` | `enforced_by_ci` | scripts/secret-scan.sh, .github/workflows/monorepo-os-gates.yml |
| `repowise.evaluate.yaml` | `advisory_only` | — |
| `ruler.apply.yaml` | `advisory_only` | — |
| `secret_scan.yaml` | `enforced_by_ci` | scripts/secret-scan.sh, .github/workflows/monorepo-os-gates.yml |
| `skills.repo_mass_reduction.yaml` | `enforced_by_ci` | .github/workflows/monorepo-os-gates.yml |
| `skills.update.yaml` | `enforced_by_ci` | .github/workflows/monorepo-os-gates.yml |
| `skills.yolo_mode_operator.yaml` | `enforced_by_ci` | .github/workflows/monorepo-os-gates.yml |
| `tool.gateway.yaml` | `enforced_by_toolgateway` | scripts/release-readiness-gate.sh, scripts/repo-oracle-score.sh, .github/workflows/monorepo-os-gates.yml, packages/tool_gateway/ |
| `visual.proof.yaml` | `advisory_only` | — |

## Orphan Contracts (Advisory Only)

These contracts have no CI job, script, or ToolGateway enforcement. They serve as
documentation-only policy declarations until enforcement is wired.

- `agent.progression.yaml`
- `artifact.upload.yaml`
- `bazel.build.yaml`
- `beads.update.yaml`
- `bootstrap.alignment.yaml`
- `code_reasoning.certificate.yaml`
- `context.google_drive_fetch.yaml`
- `design_system.lint.yaml`
- `firebase.function_bridge.yaml`
- `firebase_deploy.yaml`
- `function_call.consequential_action.yaml`
- `gemini.function_call.yaml`
- `git.history_rewrite.yaml`
- `git.lfs_check.yaml`
- `github_app.auth.yaml`
- `github_app.workflow_token.yaml`
- `gitnexus.impact.yaml`
- `knowledge.compile.yaml`
- `knowledge.promote_to_memory.yaml`
- `large_file_scan.yaml`
- `memory.promote.yaml`
- `memory.resolve_conflict.yaml`
- `memory.retain.yaml`
- `pageindex.compile.yaml`
- `python.typecheck.yaml`
- `repo.large_file_scan.yaml`
- `repo.oracle.yaml`
- `repowise.evaluate.yaml`
- `ruler.apply.yaml`
- `visual.proof.yaml`

## Next Steps

1. Wire each `advisory_only` contract to either a CI gate, pre-push script, or ToolGateway check
2. Track progress via Beads issues
3. Target: 100% enforced by v3.0
