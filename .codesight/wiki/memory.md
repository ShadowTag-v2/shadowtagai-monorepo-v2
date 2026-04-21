# Memory

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Memory subsystem handles **4 routes** and touches: auth, db, queue, ai.

## Routes

- `GET` `/api/memory` → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`
- `GET` `/api/memory/{filename}` params(filename) → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`
- `DELETE` `/api/memory/{filename}` params(filename) → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`
- `POST` `/api/memory/consolidate` → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`

## Related Models

- **Memory** (13 fields) → [database.md](./database.md)

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/super-dev/super_dev/web/api.py`

---
_Back to [overview.md](./overview.md)_