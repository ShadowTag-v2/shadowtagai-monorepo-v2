# Antigravity GitHub App Policy

## Current truth vs intended truth

### Current declared monorepo truth

The live monorepo documents still declare a **four-repo canonical merge at the canonical-root layer**:

- `apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services`
- `apps/ShadowTag-v2_stack/cosmic-crab-payload`
- `apps/ShadowTag-v2_stack/Pipeline`
- `apps/ShadowTag-v2_stack/nascent-apollo`

They also define additional active monorepo roots such as:

- `apps/counselconduit`
- `labs/uphillsnowball`
- `apps/shadowtag-web`

### Intended future truth

Your intended operating model is stronger:

- **Monorepo-Uphillsnowball becomes the only workspace**
- **All ehanc69 repos are folded into its authority / ingest / migration plan**
- Antigravity uses the **GitHub app first** for freshness and repo truth
- local checkouts exist only as indexed working copies and execution caches

This means Antigravity should treat the monorepo as:

- canonical workspace
- canonical repo-root truth
- eventual sink for all ehanc69 repos

But it should also recognize that the current monorepo docs do **not yet** declare that all repos are fully folded in.

## Hard rule

Authority order:

1. `authority-current.json`
2. authority atoms / snapshots
3. monorepo control-plane truth
4. active tasks / drift reports
5. code graph / local indexed clones
6. raw repo files

## GitHub app operating model

Use the GitHub app for:

- listing all ehanc69 repos
- repo freshness / default branch / commit SHAs
- monorepo control-plane files
- PRs / branch metadata / issues
- file fetches for canonical docs

Use local clones for:

- SQLite scan / chunking
- LanceDB indexing
- code graph validation
- changed-file embedding
- patch synthesis
- fast semantic retrieval

## Monorepo-only future mode

Antigravity should operate as if:

- `ShadowTag-v2/Monorepo-Uphillsnowball` is the future sole workspace
- every `ehanc69/*` repo is either:
  - already canonicalized into the monorepo,
  - queued for fold-in,
  - or retained as legacy/reference until folded in

## Required repo classes

### Class A — canonical monorepo truth

- `ShadowTag-v2/Monorepo-Uphillsnowball`

### Class B — fold-in candidates from ehanc69

All `ehanc69/*` repos should be tracked as fold-in candidates unless explicitly marked:

- deprecated
- reference-only
- public demo only
- superseded

### Class C — runtime dependencies

- `maderix/ANE`
- `patmakesapps/CortexLTM`
- `patmakesapps/CortexUI`
- `steveyegge/beads`
- `pgvector/pgvector`
- `postgres/postgres`
- `docker-library/postgres`
- `grafana/grafana`
- `payloadcms/payload`
- `prettier/prettier-vscode`

### Class D — reference/pattern repos

- `GantisStorm/essentials-claude-code`
- `miqcie/grepai-beads-helpers`
- `JPM1118/Threadwork`
- `akng8/beads-templates`
- `CortexReach/memory-lancedb-pro`
- `Toowiredd/claude-skills-automation`

## Launch rule

At session start Antigravity must:

1. read authority memory
2. read monorepo control-plane truth
3. enumerate ehanc69 repos through GitHub app
4. compare fold-in inventory against current monorepo truth
5. detect repos not yet canonicalized
6. generate fold-in tasks instead of silently ignoring them
7. only then proceed with normal coding/search

## Repo fold-in statuses

Each ehanc69 repo should be placed into exactly one state:

- `canonical_in_monorepo`
- `queued_for_fold_in`
- `legacy_reference`
- `public_demo`
- `deprecated`

No repo should remain unclassified.

## Anti-regression rule

If the monorepo docs still describe only four canonical roots, Antigravity must not pretend all repos are already folded in.

Instead it should:

- preserve current declared truth
- preserve your intended future truth
- create the delta as explicit work

## Practical rule

Antigravity should ask on every launch:

> Which ehanc69 repos exist now?
> Which of them are already represented in monorepo truth?
> Which remain to be folded in?
> What tasks are required to close that gap?

That is the right GitHub-app-first posture.
