---
id: atom-procedure-surprise-memory-triage
type: procedure
created: 2026-04-27T22:36:00Z
source: docs/research/miras-titans-notes.md
tags: [procedure, memory, triage, beads]
---

# Procedure: Surprise-Based Memory Triage

## When to Apply

Before writing to `.memory/atoms/` or `.beads/issues.jsonl`, evaluate the surprise
score of the information to determine the correct capture path.

## Triage Decision Tree

```
Input arrives (finding, observation, error, decision)
  │
  ├─ Does this CHANGE agent behavior? ──→ YES → beads-capture.sh decision <slug>
  │                                        (High surprise — permanent atom)
  │
  ├─ Does this BLOCK current work? ──────→ YES → beads-capture.sh issue <slug>
  │                                        (High surprise — active tracking)
  │
  ├─ Is this a NEW fact not in atoms? ───→ YES → beads-capture.sh fact <slug>
  │                                        (Medium surprise — knowledge expansion)
  │
  ├─ Is this a routine operational event? → YES → beads-capture.sh event <slug>
  │                                        (Low surprise — append to journal)
  │
  └─ Is this already captured? ──────────→ YES → Skip (zero surprise)
                                           Do NOT duplicate existing atoms.
```

## Surprise Score Thresholds

| Score | Type | Store | Retention |
|-------|------|-------|-----------|
| High (0.8-1.0) | Decision, Architecture change | `.memory/atoms/decisions/` | Permanent |
| High (0.7-0.9) | Blocking issue, Error | `.beads/issues.jsonl` | Until resolved |
| Medium (0.4-0.6) | New fact, API discovery | `.memory/atoms/facts/` | Permanent |
| Low (0.1-0.3) | Deploy event, Scan result | `.memory/events.ndjson` | Compress nightly |
| Zero (0.0) | Duplicate, Already known | Skip | N/A |

## Anti-Patterns

- ❌ Capturing every console log as a fact (memory bloat).
- ❌ Creating an issue for something already in `.memory/atoms/` (duplication).
- ❌ Writing a decision atom without verifying it differs from existing atoms.
- ❌ Skipping issue creation for a genuine blocker ("I'll remember it").

## Scripts

- `scripts/beads-capture.sh` — Primary capture interface
- `scripts/memory-retain.sh` — Persist atoms to git
- `scripts/dream_consolidation.py` — Nightly compression of low-surprise events
