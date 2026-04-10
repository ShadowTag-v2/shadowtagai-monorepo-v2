# MERGE_STATUS.md

## Status

The four-repo merge is complete at the canonical-root layer once this manifest lands.

### Canonical
- `ShadowTag-v2-fastapi-services` → `apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services`
- `cosmic-crab-payload` → `apps/ShadowTag-v2_stack/cosmic-crab-payload`
- `Pipeline` → `apps/ShadowTag-v2_stack/Pipeline`
- `nascent-apollo` → `apps/ShadowTag-v2_stack/nascent-apollo`

## Meaning

All four shared repos have one declared live canonical root.
There are no unresolved repos remaining in `monorepo_manifest.yaml`.

## Completion rule

A repo counts as fully merged only when:

1. it has exactly one declared canonical live root
2. it is no longer unresolved in `monorepo_manifest.yaml`
3. active tooling points to that canonical root
4. duplicate live roots, backup trees, recovered trees, legacy mirrors, and raw-ingest debris are excluded from live code paths

## Remaining work

Canonicalization of repo roots is complete after the manifest patch lands.

Structural hardening may still remain:
- denied-zone cleanup in live trees
- build / CI hardening
- CODEOWNERS and protected-main enforcement
- shared contracts and `third_party` centralization
- repo-wide refactorability proof

## Strategic note

The highest-value unlock was not more drafting. It was making the monorepo truthful enough that product work, lab work, and agent work stop drifting apart.

- `CounselConduit` is the MVP commercial path.
- `uphillsnowball` is the internal R&D / Apple Silicon path.
- `pnkln` is the operating/control doctrine around them.

## Summary

- 4 canonical
- 0 unresolved
- merge canonicalization complete
