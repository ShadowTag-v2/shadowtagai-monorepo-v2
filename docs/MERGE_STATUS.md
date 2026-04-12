# MERGE_STATUS.md

## Status

The four-repo merge has been resolved at the manifest level.

### Canonical
- `aiyou-fastapi-services` → `apps/aiyou_stack/aiyou-fastapi-services`
- `cosmic-crab-payload` → `apps/aiyou_stack/cosmic-crab-payload`
- `Pipeline` → `apps/aiyou_stack/Pipeline`
- `nascent-apollo` → `apps/aiyou_stack/nascent-apollo`

## Meaning

All four shared repos now have one declared live canonical root.

There are no unresolved repos remaining in `monorepo_manifest.yaml`.

## Completion rule

A repo counts as fully merged only when:

1. it has exactly one declared canonical live root
2. it is no longer unresolved in `monorepo_manifest.yaml`
3. active tooling points to that canonical root
4. duplicate live roots, backup trees, recovered trees, legacy mirrors, and raw-ingest debris are excluded from live code paths

## Summary

- 4 canonical
- 0 unresolved
- merge canonicalization complete

The monorepo is now structurally truthful at the repo-root layer.
