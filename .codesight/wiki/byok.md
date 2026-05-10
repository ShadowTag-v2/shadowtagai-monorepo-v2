# Byok

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Byok subsystem handles **4 routes** and touches: db, ai.

## Routes

- `POST` `/keys` → in: BYOKKeyRequest, out: BYOKKeyStatus [db, ai]
  `apps/counselconduit/api/byok.py`
- `GET` `/keys/{firm_id}` params(firm_id) → out: BYOKKeyStatus [db, ai]
  `apps/counselconduit/api/byok.py`
- `DELETE` `/keys/{firm_id}/{provider}` params(firm_id, provider) → out: BYOKKeyStatus [db, ai]
  `apps/counselconduit/api/byok.py`
- `POST` `/keys/{firm_id}/{provider}/validate` params(firm_id, provider) → in: BYOKKeyRequest, out: BYOKKeyStatus [db, ai]
  `apps/counselconduit/api/byok.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `apps/counselconduit/api/byok.py`

---
_Back to [overview.md](./overview.md)_
