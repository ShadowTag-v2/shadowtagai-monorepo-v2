# Monorepo Truth Map

## Canonical repo-root layer
A repo is merged at the canonical-root layer when:
- it has exactly one declared canonical live root
- it is not unresolved in the manifest
- active tooling points to that root
- duplicate/recovered/legacy/raw-ingest trees are excluded from live code paths

## Structural hardening still required
Canonical-root merge is not the same as full operational merge.
Remaining work can still include:
- denied-zone cleanup
- CI/build hardening
- CODEOWNERS / protected main
- shared contracts and third_party centralization
- repo-wide refactorability proof
