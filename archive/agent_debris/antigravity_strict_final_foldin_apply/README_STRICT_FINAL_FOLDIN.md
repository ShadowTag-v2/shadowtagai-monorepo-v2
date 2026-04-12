# Antigravity Strict Final Fold-In Apply Pack

This pack is the reconciled internal-apply bundle built from the currently available artifacts.

## Canonical precedence

1. `data/memory/authority-current.json`
2. `data/memory/operator_invariants.json`
3. repo-native monorepo control-plane truth
4. `data/memory/operator_invariants_atoms.json`
5. active tasks and drift reports
6. `fold_in_checklist.yaml`
7. only then code inspection and Git/GitHub actions

## What this pack includes

- corrected merged-control-plane installer entrypoint
- v11 merged bundle
- missing final-ingest bundle, staged explicitly
- v10 stack bundle
- operator invariants and atoms
- fold-in checklist
- internal handoff docs
- public support repo manifest and clone script

## Important

The embedded `antigravity_v11_merged_control_plane_final_bundle.tar.gz` is preserved as historical input, but the primary entrypoint in this pack is `APPLY_INTERNAL.sh`, which stages the missing final-ingest bundle explicitly before invoking the merged installer.

## Internal apply

From monorepo root:

```bash
bash APPLY_INTERNAL.sh .
```

Then:

```bash
cd control/antigravity/ane_cortex_stack_v10
uvicorn service.app.main:app --reload --port 8090
```

Then Antigravity should call:

```text
GET /api/hydrate-pack
```

before substantial repo reasoning.
