# Validate

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Validate subsystem handles **2 routes** and touches: auth.

## Routes

- `POST` `/validate` → in: ValidationRequest, out: HealthResponse [auth]
  `apps/aiyou_stack/aiyou-fastapi-services/validation/api.py`
- `POST` `/validate/batch` → in: ValidationRequest, out: HealthResponse [auth]
  `apps/aiyou_stack/aiyou-fastapi-services/validation/api.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `apps/aiyou_stack/aiyou-fastapi-services/validation/api.py`

---
_Back to [overview.md](./overview.md)_