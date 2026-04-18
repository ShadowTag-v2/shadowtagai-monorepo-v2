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
  - Pipeline
  - nascent-apollo
- Update monorepo_manifest.yaml with:
  - canonical_path
  - archived_paths
  - status
  - notes
- Canonical namespace:
  - apps/ShadowTag-v2_stack

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
