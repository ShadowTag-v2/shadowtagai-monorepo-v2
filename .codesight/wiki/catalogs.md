# Catalogs

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Catalogs subsystem handles **1 routes** and touches: auth, db, queue, ai.

## Routes

- `GET` `/api/catalogs` → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/super-dev/super_dev/web/api.py`

---
_Back to [overview.md](./overview.md)_