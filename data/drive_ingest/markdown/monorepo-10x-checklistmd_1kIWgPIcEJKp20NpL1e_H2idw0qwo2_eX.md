# Monorepo 10/10 Checklist

## Goal
Turn `Monorepo-Uphillsnowball` into a fully canonical, Google-style open-source monorepo.

## Definition of done
- [ ] Every shared repo is either canonical or archived
- [ ] No repo remains unresolved in `monorepo_manifest.yaml`
- [ ] `main` is protected and requires `bazel-build` and `bazel-test`
- [ ] `CODEOWNERS` is active and enforced
- [ ] No backup trees remain in live code paths
- [ ] No recovered trees remain in live code paths
- [ ] No nested legacy repos remain in live code paths
- [ ] No raw-ingest trees remain in live code paths
- [ ] A top-level `third_party/` policy exists and is enforced
- [ ] A top-level shared contract root exists and is in use
- [ ] Workspace, search, indexing, and build all target canonical live roots only
- [ ] At least one safe repo-wide refactor has been completed successfully

---

## Phase 0 — Freeze and protect
- [ ] Freeze new ingestion into live code paths
- [ ] Commit `.github/CODEOWNERS`
- [ ] Commit `.github/workflows/main.yml`
- [ ] Commit `monorepo_manifest.yaml`
- [ ] Commit workspace isolation settings
- [ ] Commit `pyrightconfig.json`
- [ ] Protect `main`
- [ ] Require pull requests
- [ ] Require at least 1 approval
- [ ] Require code owner review
- [ ] Require `bazel-build`
- [ ] Require `bazel-test`
- [ ] Block direct pushes to `main`
- [ ] Require branch to be up to date before merge

### Evidence
- PR / commit:
- GitHub ruleset screenshot or note:
- Validation command:
- Result:

---

## Phase 1 — Canonicalization decisions
- [ ] Canonical namespace fixed to `apps/ShadowTag-v2_stack`
- [ ] `ShadowTag-v2-fastapi-services` status verified
- [ ] `cosmic-crab-payload` status verified
- [x] `Pipeline` resolved to canonical or archived
- [x] `nascent-apollo` resolved to canonical or archived
- [ ] `monorepo_manifest.yaml` updated

### Repo state table
| Repo | Status | Canonical path | Archived paths | Notes |
|---|---|---|---|---|
| ShadowTag-v2-fastapi-services |  |  |  |  |
| cosmic-crab-payload |  |  |  |  |
| Pipeline | canonical | apps/ShadowTag-v2_stack/Pipeline | archive/recovered/arsenal_recovered | Fully canonicalized and active. |
| nascent-apollo | canonical | apps/ShadowTag-v2_stack/nascent-apollo | | Live canonical root for nascent-apollo. |

---

## Phase 2 — Live tree surgery
- [ ] Move `_PRE_OMEGA_BACKUP_*` out of live code
- [ ] Move `repos/*-legacy` out of live code
- [ ] Move `ShadowTag-Omega` out of live code
- [ ] Move `arsenal_recovered` out of live code
- [ ] Move `raw_ingest` out of live code
- [ ] Populate archive lanes:
  - [ ] `archive/backups`
  - [ ] `archive/legacy`
  - [ ] `archive/recovered`
  - [ ] `archive/imports`

### Move log
| From | To | Reason | Validated | Safe to delete later |
|---|---|---|---|---|
|  |  |  |  |  |
|  |  |  |  |  |

---

## Phase 3 — Build graph hardening
- [ ] Each canonical repo root has explicit build ownership
- [ ] Archive and denied zones excluded from active build/test paths
- [ ] `bazel build //...` passes
- [ ] `bazel test //...` passes
- [ ] CI failures map only to live code, not archive debris

### Evidence
- Last green `bazel-build`:
- Last green `bazel-test`:
- Notes:

---

## Phase 4 — `third_party` and contract layer
- [ ] Top-level `third_party/` policy created
- [ ] Shared contract root chosen:
  - [ ] `proto/`
  - [ ] `contracts/`
  - [ ] `schemas/`
- [ ] Shared interfaces moved into contract root
- [ ] At least one real service path migrated to shared contracts
- [ ] Ad hoc vendor universes removed or justified

### Evidence
- Contract root path:
- Example migrated service:
- Example generated/shared contract:
- Notes:

---

## Phase 5 — Tooling unification
- [ ] VS Code workspace points only at canonical root
- [ ] Search excludes match denied zones
- [ ] Watcher excludes match denied zones
- [ ] `pyrightconfig.json` targets only canonical live paths
- [ ] Local RAG index targets only canonical live roots
- [ ] No workspace drift
- [ ] No invalid interpreter binding
- [ ] No symlink-jungle pyright warnings

### Evidence
- Basedpyright source file count:
- Python interpreter:
- RAG/index validation:
- Notes:

---

## Phase 6 — Refactorability proof
- [ ] Perform one repo-wide refactor
- [ ] Build passes after refactor
- [ ] Tests pass after refactor
- [ ] No duplicate-path conflicts appear
- [ ] Ownership remains clear
- [ ] Final audit completed

### Refactor proof
- Refactor description:
- Paths touched:
- PR / commit:
- Validation result:

---

## Final acceptance checklist
- [ ] Zero unresolved repos
- [ ] Zero live backup trees
- [ ] Zero live recovered trees
- [ ] Zero live nested legacy repos
- [ ] `main` protected and enforced
- [ ] `CODEOWNERS` active
- [ ] `bazel-build` required and green
- [ ] `bazel-test` required and green
- [ ] `third_party/` centralized
- [ ] shared contracts centralized
- [ ] tooling aligned with canonical roots
- [ ] repo-wide refactor proven safe

## Final signoff
- Date:
- Owner:
- Remaining non-blocking improvements: