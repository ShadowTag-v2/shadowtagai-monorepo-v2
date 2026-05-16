# Goal Description

Execute Stage 3 canonicalization and perform a repo-drift audit on the canonical monorepo to ensure all dependencies and skills align with the established control plane truth.

## Proposed Changes
- Execute structural audit scripts in the monorepo
- Verify the integrity of indexed dependencies and metadata
- Rectify any deviations from the canonical `fold_in_checklist.yaml` and `operator_invariants.json` paths
- Generate an updated canonical state report

## Verification Plan
1. Output generated drift reports to the user.
2. Ensure no untracked or duplicated sub-repositories exist.
