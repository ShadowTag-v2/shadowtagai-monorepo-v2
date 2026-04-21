# Magic_link

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Magic_link subsystem handles **1 routes** and touches: auth, email.

## Routes

- `POST` `/create-matter` → in: MatterCreateRequest, out: MagicLinkResponse [auth, email]
  `apps/counselconduit/api/magic_link.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `apps/counselconduit/api/magic_link.py`

---
_Back to [overview.md](./overview.md)_
