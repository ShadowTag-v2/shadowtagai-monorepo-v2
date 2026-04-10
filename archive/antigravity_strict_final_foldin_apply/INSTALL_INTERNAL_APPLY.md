# Install: Internal Apply

## Goal

Apply the strict merged control plane internally with memory-first startup, explicit Git/GitHub invariants, and fold-in governance.

## Canonical local shape

```text
Monorepo-Uphillsnowball/
  control/
    antigravity/
      final_ingest/
      ane_cortex_stack_v10/
      v11/
      strict_final_foldin/
  data/
    memory/
      authority-current.json
      operator_invariants.json
      operator_invariants_atoms.json
      memories.jsonl
      launch-packet.json
  .agent/
    memory/
  manifests/
    monorepo_manifest.yaml
  docs/
    MERGE_STATUS.md
    ANTIGRAVITY_CONTROL_PLANE.md
  fold_in_checklist.yaml
```

## Startup law

1. Load `authority-current.json`
2. Load `operator_invariants.json`
3. Load monorepo control-plane truth
4. Load top authority atoms
5. Load active tasks
6. Load drift reports
7. Load `fold_in_checklist.yaml`
8. Only then inspect code or perform Git/GitHub operations

## Apply

```bash
bash APPLY_INTERNAL.sh .
```

## Notes

- Memory decides what is true.
- Monorepo control plane decides where live code truth lives.
- Codebase decides what must change.
- GitHub app is for freshness and repo truth.
- Local clone is for indexing and execution only.
