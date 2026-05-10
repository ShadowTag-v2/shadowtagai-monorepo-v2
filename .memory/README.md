# .memory/README.md — Operational Memory System

## Purpose

This directory holds **durable operational knowledge** — decisions, constraints, procedures,
facts, and conflict resolutions that persist across sessions.

## Structure

```
.memory/
├── config.yaml          # Memory system configuration
├── events.ndjson        # Append-only event log (newline-delimited JSON)
├── atoms/               # Categorized knowledge atoms
│   ├── decisions/       # Architectural and design decisions
│   ├── constraints/     # Technical and business constraints
│   ├── procedures/      # Standard operating procedures
│   ├── facts/           # Verified technical facts
│   ├── conflicts/       # Resolved conflicts and resolutions
│   └── open_questions/  # Unresolved questions
└── views/               # Generated summary views
    ├── HANDOFF.md        # Session handoff context
    ├── DECISIONS.md      # Decision log
    ├── CONSTRAINTS.md    # Active constraints
    └── OPEN_QUESTIONS.md # Open questions
```

## Rules

1. **Events are append-only.** Never edit `events.ndjson`.
2. **Atoms are small.** One decision/constraint/fact per file.
3. **Views are generated.** Regenerate from atoms, never edit directly.
4. **Memory is not source truth.** It records what we know, not what the code is.
5. **Promote from research.** Durable findings from `knowledge/vault` → atoms.
6. **Create Beads for action.** If an atom implies work, create a Bead, not more atoms.
