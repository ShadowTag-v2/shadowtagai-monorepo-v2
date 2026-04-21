# Streaming

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Streaming subsystem handles **1 routes** and touches: auth, cache, queue.

## Routes

- `GET` `/events` → in: Optional [auth, cache, queue]
  `external_repos/Kosmos/kosmos/api/streaming.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/Kosmos/kosmos/api/streaming.py`

---
_Back to [overview.md](./overview.md)_