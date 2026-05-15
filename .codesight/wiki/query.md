# Query

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Query subsystem handles **1 routes** and touches: auth, email, payment, ai.

## Routes

- `POST` `/api/v1/query` → in: MagicLinkRequest, out: dict [auth, email, payment, ai]
  `apps/kovelai/api/main.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `apps/kovelai/api/main.py`

---
_Back to [overview.md](./overview.md)_
