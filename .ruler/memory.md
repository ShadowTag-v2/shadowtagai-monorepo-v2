# Memory Doctrine

Memory atoms own durable operational knowledge.

## Categories
- decisions/ — architectural and design decisions
- constraints/ — technical and business constraints
- procedures/ — standard operating procedures
- facts/ — verified technical facts
- conflicts/ — resolved conflicts
- open_questions/ — unresolved questions

## Rules
- Events are append-only (events.ndjson)
- Atoms are small — one per file
- Views are generated, never edited directly
- Promote from research vault, not from raw data
- Create Beads for action, not more atoms
