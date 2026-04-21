# Experts

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Experts subsystem handles **6 routes** and touches: auth, db, queue, ai.

## Routes

- `GET` `/api/experts` → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`
- `GET` `/experts` → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`
- `POST` `/api/experts/{expert_id}/advice` params(expert_id) → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`
- `GET` `/api/experts/advice/history` → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`
- `GET` `/api/experts/advice/content` → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`
- `GET` `/api/experts/{name}` params(name) → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/super-dev/super_dev/web/api.py`

---
_Back to [overview.md](./overview.md)_