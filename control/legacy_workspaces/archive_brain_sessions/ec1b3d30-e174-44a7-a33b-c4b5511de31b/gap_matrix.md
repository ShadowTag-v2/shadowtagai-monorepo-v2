# Monorepo Integration Gap Matrix

As demanded by the control-plane rules, declaring a repository as "canonical" does not mean it is fully assimilated. The `fold_in_checklist.yaml` exposes massive structural gaps between intent and reality. Here is the strict gap matrix.

## 1. Canonical Roots vs Duplicate Families

**The 4 Declared Canonical Roots:**
These repos are designated as `canonical_in_monorepo` and successfully hold the root destination assignments, but lack integration completion.
- `ehanc69/ShadowTag-v2-fastapi-services` -> `apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services`
- `ehanc69/Pipeline` -> `apps/ShadowTag-v2_stack/Pipeline`
- `ehanc69/cosmic-crab-payload` -> `apps/ShadowTag-v2_stack/cosmic-crab-payload`
- `ehanc69/nascent-apollo` -> `apps/ShadowTag-v2_stack/nascent-apollo`

**Unresolved Duplicate Families (`duplicate_family_checked: false`):**
These twin repositories exist in a split-brain state where the legacy bare-name repo competes with the `ShadowTag-v2-*` prefixed repo. Neither has been fully superseded or eliminated.
- **fastapi-services:** `ehanc69/ShadowTag-v2-fastapi-services` vs `ehanc69/fastapi-services`
- **core:** `ehanc69/ShadowTag-v2-core` vs `ehanc69/core`
- **security:** `ehanc69/ShadowTag-v2-security` vs `ehanc69/security`
- **sre:** `ehanc69/ShadowTag-v2-sre` vs `ehanc69/sre`
- **observability:** `ehanc69/ShadowTag-v2-observability` vs `ehanc69/observability`
- **mlops:** `ehanc69/ShadowTag-v2-mlops` vs `ehanc69/mlops`
- **docs:** `ehanc69/ShadowTag-v2-docs` vs `ehanc69/docs`
- **infra:** `ehanc69/ShadowTag-v2-infra` vs `ehanc69/infra`
- **prompts:** `ehanc69/prompts`

## 2. Old Live Copies That Still Need Demotion

For **every single repository** in the checklist—including the 4 canonical roots—the completion gate `old_live_copies_demoted` remains strictly `false`.
This means the original standalone GitHub repositories are still active and have not been officially archived or locked to redirect developers strictly to the Monorepo. This creates a critical risk of architectural drift.

## 3. Manifest / Merge-Status / Tooling References Not Updated

In `fold_in_checklist.yaml`, the integration phase gates are unilaterally `false` across the board:
- `manifest_updated: false`
- `merge_status_updated: false`
- `tooling_updated: false`
- `index_updated: false`
- `build_sanity_checked: false`
- `final_status_stamped: false`

**However, the Control Plane is actually ahead of the checklist!**
`monorepo_manifest.yaml` and `MERGE_STATUS.md` **DO** currently list the 4 roots properly. The checklist is lagging behind reality.

## 4. Repo-by-Repo Checklist Fields That Can Be Truthfully Flipped Next

Based on current repository truth, we can immediately run an automation script to flip the following fields to `true` inside `fold_in_checklist.yaml`:

**For the 4 Canonical Roots (`ShadowTag-v2-fastapi-services`, `Pipeline`, `cosmic-crab-payload`, `nascent-apollo`):**
- `manifest_updated` -> Can be safely set to `true`.
- `merge_status_updated` -> Can be safely set to `true`.

**For the Remaining Unresolved Repos:**
- No gates can be flipped to `true` yet. We must physically trigger the tooling updates, archive the old live GitHub copies, verify the builds, and resolve the duplicate families before stamping them as integrated.
