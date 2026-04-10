# ANTIGRAVITY INGEST INSTRUCTION BLOCK

You are ingesting the canonical final bundle for the memory-first monorepo control plane.

## Primary objective

Make memory the single source of truth.
Do not let stale repo files, stale branches, stale docs, or old local assumptions redefine standards, settings, procedures, or canonical repo roots.

## Canonical authority order

1. `authority-current.json`
2. authority snapshots + authority atoms
3. monorepo control-plane truth
4. active tasks + drift reports
5. code graph / local indexes
6. raw codebase

## Monorepo rule

Treat `ShadowTag-v2/Monorepo-Uphillsnowball` as the future sole workspace.
Do not assume all ehanc69 repos are already canonically folded in.
Instead:

- preserve current declared monorepo truth
- compare it against the repo census / fold-in checklist
- create explicit fold-in work for the delta

## Launch sequence

1. Load authority memory first
2. Load monorepo truth
3. Load top atoms
4. Load active tasks
5. Load drift reports
6. Load fold-in checklist
7. Only then inspect code

## Fold-in rule

For every repo in `fold_in_checklist.yaml`, ensure it is exactly one of:

- `canonical_in_monorepo`
- `queued_for_fold_in`
- `archived_after_fold_in`
- `reference_only`
- `deprecated`

Nothing should float unclassified.

## Conflict rule

If codebase conflicts with authority memory, preserve authority memory and generate code upgrade work.
If local assumptions conflict with monorepo control-plane files, preserve monorepo control-plane truth and generate topology/root-fix work.

## Use these files as the canonical ingest set

- `ane_cortex_stack_v10_bundle.tar.gz`
- `fold_in_checklist.yaml`
- `antigravity_github_app_policy.md`
- `antigravity_github_app_sync_plan.sh`
- `clone_upstreams_v10.sh`

## Operational instruction

Use the GitHub app as the freshness/control plane.
Use local clones only as indexed working copies and execution caches.
Re-index changed files only.
Regenerate memory-bank derived views from canonical authority, never the other way around.

## Output expectation

After ingestion, produce:

- current launch packet
- repo fold-in delta
- current drift report
- next upgrade tasks
