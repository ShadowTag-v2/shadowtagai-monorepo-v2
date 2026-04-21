# Health

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Health subsystem handles **2 routes** and touches: auth, email, payment, ai, db, queue.

## Routes

- `GET` `/api/v1/health` → out: dict [auth, email, payment, ai]
  `apps/kovelai/api/main.py`
- `GET` `/api/health` → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `apps/kovelai/api/main.py`
- `external_repos/super-dev/super_dev/web/api.py`

---
_Back to [overview.md](./overview.md)_
