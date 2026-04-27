# .memory/ — Knowledge Atom Store

> Files are truth; SQLite is cache.

## Architecture

```text
.memory/
  ├── atoms/               # Git-tracked knowledge atoms (Markdown + YAML frontmatter)
  │   ├── doctrine/        # Operational doctrine and invariants
  │   ├── architecture/    # Architecture decisions and patterns
  │   ├── incidents/       # Incident post-mortems and resolutions
  │   └── sessions/        # Session summaries and learnings
  ├── events.ndjson        # Git-tracked authoritative mutation log
  ├── cache/               # NOT git-tracked — rebuildable indexes
  └── README.md            # This file
```

## Knowledge Atoms

Each atom is a Markdown file with YAML frontmatter:

```markdown
---
id: "atom-uuid7"
created: "2026-04-27T00:00:00Z"
updated: "2026-04-27T00:00:00Z"
category: doctrine|architecture|incident|session
tags: [tag1, tag2]
references:
  - file:///path/to/source
  - conversation://conversation-id
status: active|archived|superseded
superseded_by: "atom-uuid7-of-replacement"  # if superseded
---

# Atom Title

Content here.
```

## Mutation Log

`events.ndjson` records every atom lifecycle event:

```json
{"ts":"2026-04-27T00:00:00Z","type":"atom.created","atom_id":"...","category":"doctrine","title":"...","agent":"antigravity"}
{"ts":"2026-04-27T00:00:00Z","type":"atom.updated","atom_id":"...","fields":["content"],"agent":"antigravity"}
{"ts":"2026-04-27T00:00:00Z","type":"atom.archived","atom_id":"...","reason":"superseded","agent":"antigravity"}
```

## Rules

1. **Atoms are truth.** SQLite indexes and vector embeddings are cache.
2. **Every mutation is logged.** `events.ndjson` is append-only.
3. **Atoms reference sources.** Every atom cites where its knowledge came from.
4. **Cache is rebuildable.** Delete `.memory/cache/` and rebuild from atoms.
5. **Categories are finite.** doctrine, architecture, incident, session.
