<<<<<<< HEAD
# MERGE_STATUS.md\n
||||||| empty tree
=======
# MERGE_STATUS.md

## Status

Fold-in complete. The four former repo roots are now integrated components of the monorepo.

### Canonical root

`ShadowTag-v2/Monorepo-Uphillsnowball` — the single source of truth.

### Folded-in components (not root truth)
- `pnkln-stack-fastapi-services` → `apps/pnkln-stack_stack/pnkln-stack-fastapi-services`
- `cosmic-crab-payload` → `apps/pnkln-stack_stack/cosmic-crab-payload`
- `Pipeline` → `apps/pnkln-stack_stack/Pipeline`
- `nascent-apollo` → `apps/pnkln-stack_stack/nascent-apollo`

## Meaning

The monorepo owns these four domains. They are first-class sub-paths, not root peers.
No external repo is a canonical root. There is one root: this repo.

## Completion rule

A component counts as fully merged only when:

1. its code lives under `apps/pnkln-stack_stack/` or an appropriate monorepo sub-path
2. it is declared in `monorepo_manifest.yaml` under `folded-in-components`
3. it is no longer operated as an independent canonical root by any tooling or agent
4. duplicate live roots, backup trees, recovered trees, legacy mirrors, and raw-ingest debris are excluded from live code paths

## Remaining work

Structural hardening:
- denied-zone cleanup in live trees
- build / CI hardening
- CODEOWNERS and protected-main enforcement
- shared contracts and `third_party` centralization
- repo-wide refactorability proof

## Summary

- 1 canonical root: `ShadowTag-v2/Monorepo-Uphillsnowball`
- 4 folded-in components
- 0 unresolved

The monorepo is the truth surface. The components serve it.
>>>>>>> 5003ee8144b25604e711ef88a2d161f951a40419
