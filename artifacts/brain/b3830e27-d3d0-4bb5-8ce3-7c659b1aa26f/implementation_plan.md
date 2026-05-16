# Implementation Plan - Infrastructure Cleanup & Git Sync

# Goal Description

Clean up the Google Cloud environment by removing legacy/unnecessary Cloud Run services and ensuring the git repository is fully synchronized with the remote 'zero deviation' state.

## Proposed Changes

### Infrastructure (Google Cloud Run)

#### [DELETE] Legacy Services

The following services have been identified as legacy or superseded by the `omega-stack` and `sovereign` architecture:

- `antigravity-agent`
- `antigravity-agent-v8`
- `csrmc-judge-v6`
- `flyingmonkeys-server`
- `flyingmonkeys-worker`
- `judge-six-core`
- `n8n-server`
- `orbit-server`
- `shadowtag-brain`
- `sqdn-cdr-func`
- `squadron-commander-func`
- `wing-commander-func`

#### [RETAIN] Sovereign Stack

The following services map to the current `OMEGA_PROTOCOL_MASTER_REPRINT.md` and will be RETAINED:

- `flyingmonkeys-omega-stack`
- `jetski-bridge`
- `judge-six-omega-stack`
- `shadowtag-omega-v2`
- `shadowtagai-juggernaut`
- `uphillsnowball-sovereign`

### Repository

- Force add all changes (`git add -A`) to resolve staging issues.
- Commit and push to `main`.

## Verification Plan

### Automated Tests

- Run `gcloud run services list` to confirm only the 6 retained services exist.
- Run `git status` to confirm clean working tree.
