# Memory-first source of truth

## Goal
Antigravity should always wake up current, not regress to stale codebase state.

## Core rule
Authority memory is canonical. Codebase is an object to update.

## The four memory layers
1. Authority snapshot
   - current standards
   - current settings
   - current startup contract
   - current operating procedures

2. Task/flow memory
   - Beads tasks
   - open blockers
   - current branch/workstream

3. Long-term memory
   - semantic memories
   - JSONL journal
   - CortexLTM thread summaries

4. Codebase
   - evidence
   - implementation target
   - never canonical for standards/settings by default

## Startup sequence
1. Load authority-current.json
2. Load active authority snapshots
3. Load recent task state + recent summary
4. Only then inspect codebase
5. If codebase conflicts with authority, produce an upgrade task

## Write barrier
Any change to standards/settings/procedures is not real until it updates:
- authority-current.json
- authority_snapshots
- optional JSONL journal

## Anti-regression rule
Never let raw repo files silently overwrite canonical memory.
