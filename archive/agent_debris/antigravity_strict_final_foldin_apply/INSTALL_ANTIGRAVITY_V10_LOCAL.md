# Install Antigravity v10 Local

## Goal

Make Antigravity local boot through the v10 control plane every time, with memory-first startup and monorepo-truth hydration.

## Canonical local paths

```text
Monorepo-Uphillsnowball/
  control/
    antigravity/
      final_ingest/
      ane_cortex_stack_v10/
  data/
    memory/
      authority-current.json
      memories.jsonl
      launch-packet.json
  .agent/
    memory/
```

## What this installs

- final ingest bundle into `control/antigravity/final_ingest/`
- v10 stack into `control/antigravity/ane_cortex_stack_v10/`
- stable authority memory into `data/memory/`
- generated `.agent/memory/*` compatibility views
- local startup contract for Antigravity:
  - authority memory first
  - monorepo truth second
  - tasks/drift third
  - codebase only after hydration

## Inputs expected

Place these files where the setup script can access them:

- `antigravity_final_ingest_bundle.tar.gz`
- `ane_cortex_stack_v10_bundle.tar.gz`

## Recommended monorepo root

Run everything from the root of:

- `shadowtag-omega-v4/Monorepo-Uphillsnowball`

## Install steps

### 1. Unpack the final ingest bundle

This lands:

- `ANTIGRAVITY_INGEST_INSTRUCTIONS.md`
- `fold_in_checklist.yaml`
- policy/sync/clone files
- the v10 bundle itself

### 2. Expand the v10 bundle into the control-plane path

Canonical local install target:

- `control/antigravity/ane_cortex_stack_v10/`

### 3. Promote stable memory paths

Canonical local memory paths:

- `data/memory/authority-current.json`
- `data/memory/memories.jsonl`
- `data/memory/launch-packet.json`

These must not stay buried inside the extracted bundle tree.

### 4. Generate `.agent/memory/*` derived views

Do not hand-edit `.agent/memory/*` as primary truth.
They are generated compatibility surfaces.

### 5. Start the local stack

- bootstrap SQLite
- start Postgres/Grafana
- seed memory-first bootstrap
- export launch packet

### 6. Make Antigravity launch through hydrate-pack

Antigravity should call:

- `GET /api/hydrate-pack`

before any substantial repo reasoning.

## Required behavior after install

Antigravity local must follow this order:

1. Load `authority-current.json`
2. Load authority atoms/snapshots
3. Load monorepo control-plane truth
4. Load fold-in checklist
5. Load drift reports
6. Load active tasks
7. Only then inspect code

## GitHub freshness rule

Use GitHub app for:

- repo freshness
- control-plane files
- repo census / fold-in delta

Use local clones for:

- indexing
- code graph
- changed-file embedding
- patch synthesis

## If Git push/auth is broken

Do not block local adoption on a giant remote push.

Adopt locally first.
Then fix Git auth and push controlled changes later.

Preferred remote mode:

```bash
git remote set-url origin git@github.com:ShadowTag-v2/Monorepo-Uphillsnowball.git
```

Or for HTTPS:

```bash
gh auth login
gh auth setup-git
```

## Success criteria

Antigravity local is correctly installed when:

- v10 is expanded under `control/antigravity/ane_cortex_stack_v10/`
- memory files live under `data/memory/`
- `.agent/memory/*` exists as generated derived views
- the local API can serve `GET /api/hydrate-pack`
- Antigravity starts from hydrate-pack instead of stale repo context
- code is treated as upgrade target, not memory authority
