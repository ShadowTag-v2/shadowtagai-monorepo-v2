---
description: Perform one bounded maintenance pass safely. No recursion.
---

# /gated-maintenance

## Goal

Perform one bounded maintenance pass safely.
This replaces infinite `/live-engine` recursion loops.

## Steps

1. Run `/repo-pulse` first.
2. Determine scope — pick exactly ONE of:
   - One Beads issue
   - One PR diff
   - One package path
3. Run secret and bloat gates:
   - `betterleaks` scan on target files
   - `scripts/classify-upload-payload.sh` on any new files
4. Run formatters in **check mode first**:
   - `ruff check` (Python)
   - `biome check` (TypeScript)
   - `buildifier --mode=check` (Bazel)
5. If autofix is allowed:
   - Create or confirm feature branch
   - Apply minimal patch
   - Run tests/checks
   - Write evidence via `scripts/record-agent-event.sh`
   - Update Beads issue
6. **STOP.** Do not recurse. Do not start a second maintenance pass.

## Rules

- Scope is bounded to ONE issue/diff/package
- No recursive loops
- No silent overwrites
- Evidence is mandatory
- Beads update is mandatory
- If scope creep is discovered, create a NEW Beads issue for it
