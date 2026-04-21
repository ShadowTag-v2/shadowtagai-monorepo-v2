# Ungpt_service

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Ungpt_service subsystem handles **3 routes** and touches: auth, cache, ai.

## Routes

- `POST` `/v1/ungpt/query` → in: UnGPTRequest, out: UnGPTResponse [auth, cache, ai]
  `apps/aiyou_stack/aiyou-fastapi-services/ungpt_service.py`
- `GET` `/v1/ungpt/health` → out: UnGPTResponse [auth, cache, ai]
  `apps/aiyou_stack/aiyou-fastapi-services/ungpt_service.py`
- `GET` `/v1/ungpt/budget/{user_id}` params(user_id) → out: UnGPTResponse [auth, cache, ai]
  `apps/aiyou_stack/aiyou-fastapi-services/ungpt_service.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `apps/aiyou_stack/aiyou-fastapi-services/ungpt_service.py`

---
_Back to [overview.md](./overview.md)_