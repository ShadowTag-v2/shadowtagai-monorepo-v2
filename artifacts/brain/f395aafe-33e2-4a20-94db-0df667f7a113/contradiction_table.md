# Control-Plane Contradiction Table

| Claim | Matching File(s) | Conflicting File(s) | Confidence |
|-------|------------------|---------------------|------------|
| All intended fold-ins are fully completed (`total queued: 0`) | `04_canonical_state.md` | `fold_in_checklist.yaml` (Lists repos as `queued_for_fold_in` with incomplete `false` checks like `folded_into_destination`) | High (The operational yaml tracker contradicts the asserted snapshot) |
| Topography relies on one unified product path (`apps/counselconduit`) | `04_canonical_state.md`, `.memory_lock_state` | System Prompts/Legacy Docs (Carry legacy rules that 4 repo roots like `apps/aiyou_stack/*` remain canonical) | High (Stale instructions conflict with the new memory lock) |

## Proposed Resolution Plan

1. **Reconcile the Tracker (`fold_in_checklist.yaml`)**
   - Audit the remaining `queued_for_fold_in` entries against the physical repository state.
   - If they have already been merged via `deploy`/`foldin` scripts, batch update the checks to `true` and the status to `canonical_in_monorepo` or `archived_after_fold_in`.
   - If work remains, execute the final repo fold-ins correctly.

2. **Purge Legacy Topography Rules**
   - Hunt down the lingering "four repo roots" mandate across all agent system prompt files (`.antigravity-system-prompt.txt`, `AGENTS.md`, `COR.RULES.md`, etc.).
   - Rewrite or delete them to strictly enforce the unified `apps/counselconduit` topography rule.

3. **Re-Synchronize Asserts**
   - Wait until the operational tracker (`fold_in_checklist.yaml`) and system prompts mathematically match before regenerating `04_canonical_state.md` as the true final proof.
