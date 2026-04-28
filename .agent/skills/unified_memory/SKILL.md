---
name: Unified Memory
description: BANS legacy beads_manager.py. All memory operations use the KI system and .beads/ evidence trail.
---

# Unified Memory

## Prohibition

**`beads_manager.py` is BANNED and DELETED.** Any attempt to import, invoke, or recreate `beads_manager.py` is a Tier 1 violation. The legacy bead management system has been replaced by the Unified Memory architecture.

## Mandatory Execution Paths

### Memory Promotion (Session → Persistent)

All session learnings that must persist across conversations MUST be promoted via the Knowledge Item (KI) system:

```
Target: ~/.gemini/antigravity/knowledge/<ki-name>/
Structure:
  metadata.json   — summary, timestamps, references
  artifacts/      — related files, docs, implementation details
```

**Promotion trigger**: End of session, significant architectural decision, or resolved debugging pattern.

### Evidence Trail (.beads/)

All operational events (audit results, CI failures, deployment logs) MUST be logged to the `.beads/` evidence directory:

- `.beads/issues.jsonl` — Structured issue log (JSON Lines format)
- `.beads/kairos_heartbeat.json` — Daemon health status
- `.beads/firebase-sa.json` — Service account key (gitignored)

### Task Tracking

Use the monorepo's task ledger system:

- `docs/TASK_LEDGER.md` — Active task tracking
- `docs/MONOREPO_OS.md` — Operational state documentation
- Conversation artifacts — Stored in `~/.gemini/antigravity/brain/<conversation-id>/`

## Memory Hierarchy

1. **KI System** (persistent, curated) → `~/.gemini/antigravity/knowledge/`
2. **Conversation Context** (session-scoped) → `~/.gemini/antigravity/brain/`
3. **Evidence Trail** (append-only audit) → `.beads/`
4. **Daemon State** (runtime) → `.beads/kairos_heartbeat.json`

## Detection Pattern

If any agent imports `beads_manager` or calls `beads_manager.py`, flag as `LEGACY_MEMORY_VIOLATION` in `.beads/issues.jsonl`.

## Cross-References

- `~/.gemini/antigravity/knowledge/` — KI root
- `.beads/` — Evidence directory
- `scripts/dream_consolidation.py` — Nightly KI maintenance daemon
- `GEMINI.md` → Context Compaction section
