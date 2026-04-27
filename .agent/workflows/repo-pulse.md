---
description: Refresh Antigravity's operational state from repo truth before work. Replaces /live-engine.
---

# /repo-pulse

## Goal

Wake Antigravity into repo truth before any meaningful work begins.
This replaces `/live-engine`. No infinite recursion. No auto-overwrite.

## Steps

1. Run `scripts/antigravity-preflight.sh`
2. Run `scripts/beads-sync.sh`
3. Run `scripts/index-status.sh`
4. Run `scripts/contract-drift-check.sh`
5. Run `scripts/repo-oracle "$TASK"` (if task context is known)
6. Load context:
   - `docs/hand_off/SHADOWTAGAI_CURRENT_STATE.md`
   - `.memory/views/HANDOFF.md`
   - `.beads ready` work
7. If conflicts appear between sources, **STOP** and report them.
   Follow `.ruler/memory-hygiene.md` freshness order.
8. Select exactly one Beads issue or create one.
9. Continue only through ToolGateway.

## Rules

- Do **not** run `/live-engine`
- Do **not** recurse infinitely
- Do **not** auto-overwrite files
- Do **not** push or deploy from memory
- End after one bounded pass with evidence and Beads updates
