# sim102/sim117 Style Refactor Schedule — apps/aiyou_stack/

> Created: 2026-04-30 | Status: SCHEDULED

## Background

The `sim102` and `sim117` patterns refer to structural code refactors identified during the
CounselConduit and AiYou stack audits. These target dead code, import standardization,
and structural alignment with the monorepo's canonical patterns.

## Scope

| Package | Path | Refactor Type | Priority |
|---------|------|---------------|----------|
| aiyou-fastapi-services | `apps/aiyou_stack/aiyou-fastapi-services/` | sim102: Import path normalization | P2 |
| shield | `apps/aiyou_stack/shield/` | sim117: Dead export pruning | P2 |
| serverless_node | `apps/aiyou_stack/serverless_node/` | sim102: CJS→ESM migration | P3 |
| Pipeline | `apps/aiyou_stack/Pipeline/` | sim117: Unused handler cleanup | P3 |
| cosmic-crab-payload | `apps/aiyou_stack/cosmic-crab-payload/` | sim102: Import dedup | P3 |
| nascent-apollo | `apps/aiyou_stack/nascent-apollo/` | sim117: Dead route removal | P3 |

## Execution Plan

### Phase 1: sim102 — Import Path Normalization (ETA: Q2W3 2026)
1. Run `ruff check --select F401,F811 --fix` across all Python packages
2. Run `biome check --fix` across all TypeScript packages
3. Normalize import paths to use monorepo-relative `packages/*` where applicable
4. Verify no circular imports via `ast-grep`

### Phase 2: sim117 — Dead Export Pruning (ETA: Q2W4 2026)
1. Run `scripts/dead-code-audit.sh` per-package
2. Remove unused exports from `index.ts` / `__init__.py` barrels
3. Verify downstream consumers don't break (test suite regression check)
4. Update `monorepo_manifest.yaml` with pruned module counts

## Constraints
- RULE 00: No file deletions — only archive to `_archive_*` directories
- All changes must pass `ruff` + `biome` + test suite before commit
- Each package refactored as a separate commit for clean rollback
