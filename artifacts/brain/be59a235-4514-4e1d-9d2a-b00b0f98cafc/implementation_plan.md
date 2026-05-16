# Goal Description
Resolve the critical split-brain schema drift between the primary `monorepo_manifest.yaml` and the secondary `manifests/monorepo_manifest.yaml`. Following reconciliation, execute a strict, batch-mode canonicalization fold-in of the 30+ queued `aiyou-*` repositories into the `Monorepo-Uphillsnowball` architecture.

## User Review Required
> [!WARNING]
> **Data Loss Prevention**: The `manifest_reconcile_report.py` identified 46 keys unique to the secondary manifest and 59 unique to the primary. We will formally archive `manifests/monorepo_manifest.yaml` into an `.agent/archive` state rather than outright deletion to prevent losing historical edge-case declarations, while elevating the root manifest as the sole operational source of truth.

## Proposed Changes

### Configuration Control Target
The control plane must have only a single truth surface.
#### [RENAME] `manifests/monorepo_manifest.yaml` -> `archive_legacy/manifests/monorepo_manifest.yaml`

### Queued Fold-in Execution Matrix
We will establish an autonomous python/bash loop built upon `fold_in_repo_checklist.py` to recursively pull, audit, and fold in the following target map:

1. **Deployable Services & Apps** (`apps/...`)
   - `aiyoujr-template-2`
   - `aiyou-clients`
   - `aiyou-frontend`
   - `aiyou-examples`
   - `aiyou-api`
   - `aiyou-backend`
   - `aiyou-ui-kit`
   - `aiyou-offline-appliance`
2. **Infrastructure & Ops** (`infra/...`)
   - `aiyou-mlops`, `aiyou-infra`, `aiyou-devops`, `aiyou-observability`, `aiyou-sre`, `aiyou-security`, `aiyou-sops`, `aiyou-risk-engine`, `aiyou-risk`, `aiyou-ci`
3. **Packages & Shared Logic** (`packages/...`)
   - `aiyou-core`, `aiyou-data-contracts`, `aiyou-rollup`, `aiyou-policy`, `aiyou-indexer`, `aiyou-codesmith`, `aiyou-prompts`, `aiyou-exec`
4. **Governance, Eval, & Memory** (`governance/...`, `memory/...`, etc.)
   - `aiyou-objections-decisions`, `aiyou-governance`, `erik-hancock-llm-memory`, `aiyou-evals`, `pnkln`, `aiyou-ml`, `aiyou-data`

*Note: As this is a batch migration, overlapping paths and stale MCP/model references will be caught, repaired, and rewritten to the global manifest iteratively per the `ANTIGRAVITY_MANIFEST_AWARE_FOLDIN_GUIDE.md`.*

## Verification Plan
### Automated Verifications
1. **Zero-Drift Validation**: Re-run `manifest_reconcile_report.py`. The required exit state must explicitly report no secondary manifest found, effectively achieving Zero Drift.
2. **Schema Sanity Check**: Run Python schema validation against the updated `monorepo_manifest.yaml` to ensure no corrupted dict/list structures were injected during the 30-run loop.
3. **Workspace Check**: Evaluate `./.vscode/settings.json` and `./.aiexclude` to ensure canonical live paths remain exposed, while all backup and nested `.git` remnants run through the strict `demote` protocol.
