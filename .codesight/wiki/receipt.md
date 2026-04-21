# Receipt

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Receipt subsystem handles **1 routes** and touches: auth.

## Routes

- `GET` `/receipt/{asset_id}` params(asset_id) → out: AuthenticationResponse [auth, upload]
  `apps/aiyou_stack/aiyou-fastapi-services/shadowtag/api.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `apps/aiyou_stack/aiyou-fastapi-services/shadowtag/api.py`

---
_Back to [overview.md](./overview.md)_