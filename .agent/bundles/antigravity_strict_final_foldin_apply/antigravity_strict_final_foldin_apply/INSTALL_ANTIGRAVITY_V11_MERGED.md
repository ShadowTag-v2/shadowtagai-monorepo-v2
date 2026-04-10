# Install Antigravity v11 Merged Control Plane

## Goal
Make Antigravity local boot through a merged control plane:

- repo-native pnkln control plane stays authoritative for workspace/root truth
- v10 stack provides authority memory, atoms, hydrate-pack, drift, code-graph, promotions
- operator invariants lock Git/GitHub behavior
- fold-in checklist drives the 56-repo migration delta

## Final local shape

```text
Monorepo-Uphillsnowball/
  control/
    antigravity/
      final_ingest/
      ane_cortex_stack_v10/
      v11/
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
```

## Startup law
At every Antigravity/editor launch:

1. Load `authority-current.json`
2. Load `operator_invariants.json`
3. Load monorepo control-plane truth
4. Load top authority atoms
5. Load active tasks
6. Load drift reports
7. Load `fold_in_checklist.yaml`
8. Only then inspect code or do Git/GitHub operations

## The key distinction
- memory decides what is true
- monorepo control plane decides where live code truth lives
- codebase decides what must change

## Recommended usage
Run the merged setup from monorepo root:

```bash
bash setup_antigravity_v11_merged.sh .
```

Then start the local API from:

```bash
cd control/antigravity/ane_cortex_stack_v10
uvicorn service.app.main:app --reload --port 8090
```

And make Antigravity call:

```text
GET /api/hydrate-pack
```

before substantial repo reasoning.
