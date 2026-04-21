# Deploy

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Deploy subsystem handles **6 routes** and touches: auth, db, queue, ai.

## Routes

- `GET` `/api/deploy/platforms` → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`
- `GET` `/api/deploy/precheck` → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`
- `GET` `/api/deploy/remediation` → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`
- `POST` `/api/deploy/remediation/export` → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`
- `GET` `/api/deploy/remediation/archive` → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`
- `POST` `/api/deploy/generate` → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/super-dev/super_dev/web/api.py`

---
_Back to [overview.md](./overview.md)_