# Memory & Beads Merge Policy

> **Status:** Active | **Owner:** Agent Fleet | **Version:** 1.0
> **Last updated:** 2026-04-27

## Purpose

Defines how `.beads/` and `.memory/` artifacts are handled during branch merges,
rebases, and cross-agent session handoffs. These files are append-only journals and
atomic knowledge stores — standard merge strategies cause data loss.

## Rules

### 1. `.beads/issues.jsonl` — Append-Only, Never Overwrite

- **Merge strategy:** `union` (both sides win).
- On conflict: concatenate both versions, then deduplicate by `id` field.
- Never delete lines — closed issues remain for audit trail.
- Script: `scripts/beads-capture.sh` handles safe appends.

### 2. `.beads/kairos_heartbeat.json` — Last-Writer-Wins

- **Merge strategy:** `theirs` (most recent session wins).
- This file is a transient timestamp — the latest value is always correct.
- Configure in `.gitattributes`:
  ```
  .beads/kairos_heartbeat.json merge=theirs
  ```

### 3. `.beads/repo_doctor_latest.json` — Last-Writer-Wins

- Same as heartbeat: the most recent scan result is canonical.
- Previous results are archived in git history, not in the file.

### 4. `.memory/events.ndjson` — Append-Only

- Same as `issues.jsonl`: concatenate on conflict, deduplicate by `id`.
- Events are immutable historical records.

### 5. `.memory/atoms/*` — File-Level Merge

- Each atom is a standalone markdown file with frontmatter.
- **Merge strategy:** standard file-level merge (no line-level).
- On conflict: keep the version with the later `created` timestamp in frontmatter.
- Never merge two atoms into one — they are intentionally separate units.

### 6. `.memory/config.yaml` — Manual Review

- This is a structural config file. Conflicts require human review.
- Flag as STATE B (Clutch) if automated merge fails.

## .gitattributes Configuration

Add to the repository root:

```gitattributes
# Beads — append-only journals
.beads/issues.jsonl merge=union
.beads/kairos_heartbeat.json merge=theirs
.beads/heartbeat.json merge=theirs
.beads/repo_doctor_latest.json merge=theirs

# Memory — append-only events
.memory/events.ndjson merge=union
```

## Cross-Agent Handoff Protocol

1. Outgoing agent runs `scripts/session-handoff.sh` to capture state.
2. Incoming agent reads `.beads/session_handoff.json` to resume.
3. If handoff file is stale (>24h), incoming agent runs `bd sync` to refresh.
4. Merge conflicts in beads/memory during `git pull` are resolved per the rules above.

## Anti-Patterns

- ❌ `git checkout --theirs .beads/issues.jsonl` — loses the other agent's issues.
- ❌ Editing `.memory/atoms/` files during merge — atoms are immutable after creation.
- ❌ Using `git reset --hard` on `.beads/` — violates RULE 00 (Immutable Infrastructure).
