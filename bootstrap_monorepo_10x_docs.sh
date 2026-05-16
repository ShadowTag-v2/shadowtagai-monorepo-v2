#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"

mkdir -p "${ROOT}/docs"
cd "${ROOT}"

cat > docs/monorepo-10x-command.txt <<'EOF'
/monorepo-10x

MONOREPO 10/10 EXECUTION DIRECTIVE

Canonical workspace root:
/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball

Objective
Transform Monorepo-Uphillsnowball into a fully canonical, Google-style open-source monorepo with:
- one canonical live root per repo
- zero unresolved repos
- zero backup, recovered, legacy, raw-ingest, or nested-repo trees in live code paths
- enforced trunk governance on main
- active CODEOWNERS
- required Bazel checks on main
- centralized third_party policy
- centralized shared contract layer
- deterministic workspace, indexing, build, and search behavior

Success definition
The monorepo is complete only when:
1. Every repo is either canonical or archived.
2. No repo remains unresolved in monorepo_manifest.yaml.
3. main is protected and requires:
   - bazel-build
   - bazel-test
4. CODEOWNERS is active and enforced.
5. No backup, recovered, nested legacy, or raw-ingest tree remains in live code paths.
6. Search, build, indexing, and agent operations point only at canonical live paths.
7. Shared contracts are centralized.
8. Third-party policy is centralized.
9. Workspace drift is prevented by default.
10. The repo supports safe repo-wide refactors.

Execution posture
- Fail closed on ambiguity.
- Never create a second source of truth.
- Prefer canonicalization over ingestion.
- Prefer archive-then-delete over indefinite coexistence.
- Prefer structural clarity over temporary convenience.
- Never call a repo “merged” unless it has one canonical live root and no live duplicate.

Phase 0 — Freeze and protect
- Freeze new ingestion into live code paths.
- Commit and apply:
  - .github/CODEOWNERS
  - .github/workflows/main.yml
  - monorepo_manifest.yaml
  - workspace isolation settings
  - pyrightconfig.json
- Enforce GitHub branch protection for main:
  - require pull requests
  - require 1 approval minimum
  - require code owner review
  - require status checks:
    - bazel-build
    - bazel-test
  - block direct pushes
  - require up-to-date branch before merge
- Verify canonical workspace root and path guards.

Phase 1 — Canonicalization decisions
- For every shared repo, assign exactly one state:
  - canonical
  - archived
- Resolve immediately:
- Update monorepo_manifest.yaml with:
  - canonical_path
  - archived_paths
  - status
  - notes
- Canonical namespace:
  - apps/pnkln-stack_stack

Phase 2 — Live tree surgery
- Move out of live trees:
  - _PRE_OMEGA_BACKUP_*
  - repos/*-legacy
  - ShadowTag-Omega
  - arsenal_recovered
  - raw_ingest
- Use archive lanes:
  - archive/backups
  - archive/legacy
  - archive/recovered
  - archive/imports
- Ensure no live app tree contains nested repo copies, backup trees, recovered shards, or legacy worlds.

Phase 3 — Build graph hardening
- Ensure each canonical repo root has explicit build ownership.
- Exclude archive and denied zones from active build/test paths.
- Verify:
  - bazel build //...
  - bazel test //...
- Remove accidental build reachability from archived or legacy material.

Phase 4 — third_party and contract layer
- Establish top-level third_party policy.
- Establish one shared contract root:
  - proto/
  - contracts/
  - or schemas/
- Move shared interfaces, generated contracts, and shared schemas there.
- Refactor services and libraries to consume shared contracts rather than local duplicates.

Phase 5 — Tooling unification
- Confirm these point only at canonical live paths:
  - VS Code workspace
  - search excludes
  - watcher excludes
  - pyrightconfig.json
  - agent workspace rules
  - local RAG reindex targets
- Rebuild local vector/index only against canonical live roots.
- Remove lingering references to old ShadowTag-v2, parent dirs, playgrounds, and sibling repos.

Phase 6 — Refactorability proof
- Perform one real repo-wide refactor across multiple canonical roots.
- Verify:
  - build passes
  - tests pass
  - ownership is clear
  - no duplicate path conflicts appear
- Run final audit:
  - canonical roots only
  - no unresolved repos
  - no live legacy debris
  - CI enforced
  - contracts centralized
  - third_party centralized

Operational rules
- Never ingest before canonicalizing.
- Never leave a repo unresolved after its assigned migration pass.
- Never keep live duplicates “temporarily” without an archive deadline.
- Never modify denied zones unless explicitly performing archival or migration work.
- Never declare success based on docs or claims alone; verify in code, build, CI, and manifest.
- Update monorepo_manifest.yaml whenever canonical state changes.
- When in doubt, archive first, then delete after validation.

Safety addendum
1. Canonical manifest is law.
2. No repo may remain unresolved after its assigned week.
3. No new archive, backup, legacy, recovered, or raw-ingest content may enter live code paths.
4. Any discovered duplicate live root must be resolved before new feature work continues.
5. All structural changes must land through protected main via PR with required checks passing.
6. All migration work must update:
   - monorepo_manifest.yaml
   - CODEOWNERS if paths changed
   - Bazel ownership/build metadata if roots changed
7. Prefer canonical live paths over archival, recovered, and legacy paths in every search, edit, refactor, and generation action.
EOF

cat > docs/monorepo-10x-checklist.md <<'EOF'
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
- [ ] Canonical namespace fixed to `apps/pnkln-stack_stack`
- [ ] `pnkln-stack-fastapi-services` status verified
- [ ] `cosmic-crab-payload` status verified
- [x] `Pipeline` resolved to canonical or archived
- [x] `nascent-apollo` resolved to canonical or archived
- [ ] `monorepo_manifest.yaml` updated

### Repo state table
| Repo | Status | Canonical path | Archived paths | Notes |
|---|---|---|---|---|
| pnkln-stack-fastapi-services |  |  |  |  |
| cosmic-crab-payload |  |  |  |  |
| Pipeline | canonical | apps/pnkln-stack_stack/Pipeline | archive/recovered/arsenal_recovered | Fully canonicalized and active. |
| nascent-apollo | canonical | apps/pnkln-stack_stack/nascent-apollo | | Live canonical root for nascent-apollo. |

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
EOF

cat > docs/monorepo-weekly-scorecard.md <<'EOF'
# Monorepo Weekly Scorecard

## Week of
`YYYY-MM-DD`

## Overall score
- Current week score: `__/100`
- Last week score: `__/100`
- Delta: `+/-__`

---

## Category scores

| Category | Weight | Score | Weighted score | Notes |
|---|---:|---:|---:|---|
| Canonical repo resolution | 20 |  |  |  |
| Live tree cleanliness | 20 |  |  |  |
| GitHub governance | 15 |  |  |  |
| Bazel / CI reliability | 15 |  |  |  |
| `third_party` discipline | 10 |  |  |  |
| Shared contracts | 10 |  |  |  |
| Workspace / tooling stability | 10 |  |  |  |

---

## 1) Canonical repo resolution

### Audit questions
- Are all shared repos marked canonical or archived?
- Does `monorepo_manifest.yaml` contain any `status: unresolved` entries?
- Does each canonical repo have exactly one live root?

### Evidence
- Manifest path:
- Commit / PR:
- Example current entries:

```yaml
# paste exact manifest examples here
```

### Scoring guide

* `20/20`: zero unresolved repos
* `10/20`: one or two unresolved repos remain
* `0/20`: multiple unresolved repos and unclear canonical roots

### Current examples

* Good example:
* Bad example:
* Fix next week:

---

## 2) Live tree cleanliness

### Audit questions

* Are backup, recovered, raw-ingest, and legacy trees still inside live app roots?
* Were any moved to `archive/` this week?
* Are there still nested repo copies in live paths?

### Evidence

* Example path removed:
* Example path still blocking:
* Archive move commit / PR:

### Specific examples

* `_PRE_OMEGA_BACKUP_*` status:
* `ShadowTag-Omega` status:
* `arsenal_recovered` status:
* `raw_ingest` status:

### Scoring guide

* `20/20`: no non-canonical trees in live paths
* `10/20`: some remain but clear progress made
* `0/20`: no meaningful cleanup

---

## 3) GitHub governance

### Audit questions

* Is `main` protected?
* Are PRs required?
* Are code owner reviews required?
* Are `bazel-build` and `bazel-test` required and passing?

### Evidence

* Ruleset summary:
* Last PR merged with checks:
* CODEOWNERS path:
* Required checks visible:

### Specific examples

* Last green `bazel-build`:
* Last green `bazel-test`:
* Example PR with owner review:
* Example violation or gap:

### Scoring guide

* `15/15`: fully enforced on `main`
* `8/15`: workflow exists but enforcement partial
* `0/15`: direct-to-main and no required checks

---

## 4) Bazel / CI reliability

### Audit questions

* Does `bazel build //...` pass?
* Does `bazel test //...` pass?
* Are archive/legacy trees excluded from active CI scope?

### Evidence

* Latest CI run link:
* Build result:
* Test result:
* Failure source if red:

### Specific examples

* Good:
* Bad:
* Fix next week:

### Scoring guide

* `15/15`: stable green CI on live code
* `8/15`: intermittent failures, but real progress
* `0/15`: CI untrusted or constantly failing from structural noise

---

## 5) `third_party` discipline

### Audit questions

* Is there a centralized `third_party/` policy?
* Are vendored dependencies centralized or still scattered?
* Are app-local vendor mirrors still acting as source of truth?

### Evidence

* Policy file / path:
* Example dependency moved:
* Example app-local vendor path still unresolved:

### Scoring guide

* `10/10`: centralized and enforced
* `5/10`: partial centralization
* `0/10`: scattered vendor worlds remain

---

## 6) Shared contracts

### Audit questions

* Is there one chosen shared contract root?
* Are services using shared schemas/contracts?
* Are duplicated local API definitions being removed?

### Evidence

* Contract root:
* Example shared contract:
* Example migrated service:
* Example remaining duplicate definition:

### Scoring guide

* `10/10`: contract root exists and is in use
* `5/10`: contract root exists but adoption partial
* `0/10`: no centralized contract layer

---

## 7) Workspace / tooling stability

### Audit questions

* Is workspace root stable?
* Is Python interpreter binding stable?
* Is basedpyright narrowed to canonical live roots?
* Are symlink-jungle warnings gone?
* Is local RAG indexing canonical-only?

### Evidence

* Active interpreter:
* Basedpyright source file count:
* Pyright warnings:
* RAG/index note:
* Workspace root verification output:

### Specific examples

* Good:
* Bad:
* Fix next week:

### Scoring guide

* `10/10`: stable and boring
* `5/10`: mostly stable, some drift/noise remains
* `0/10`: recurring workspace/env/index failures

---

## Weekly highlights

* Best improvement this week:
* Most important blocker removed:
* Biggest regression:
* Highest-risk unresolved item:

---

## Next-week commitments

1.
2.
3.

---

## Executive summary

Write 3–5 sentences:

* where the monorepo stands now
* what changed this week
* what still blocks 10/10
* what must happen next week to stay on plan
EOF

echo
echo "Wrote:"
echo "  ${ROOT}/docs/monorepo-10x-command.txt"
echo "  ${ROOT}/docs/monorepo-10x-checklist.md"
echo "  ${ROOT}/docs/monorepo-weekly-scorecard.md"
echo
echo "Suggested next step:"
echo "  git add docs/monorepo-10x-command.txt docs/monorepo-10x-checklist.md docs/monorepo-weekly-scorecard.md"
echo "  git commit -m 'docs(monorepo): add 10x directive, checklist, and weekly scorecard'"
