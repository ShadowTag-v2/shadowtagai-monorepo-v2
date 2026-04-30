# Main_ecosystem

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Main_ecosystem subsystem handles **9 routes**.

## Routes

- `POST` `/decision` → in: DecisionContext, out: DecisionResult
  `apps/aiyou_stack/aiyou-fastapi-services/app/main_ecosystem.py`
- `GET` `/validation` → out: DecisionResult
  `apps/aiyou_stack/aiyou-fastapi-services/app/main_ecosystem.py`
- `POST` `/debate` → in: DecisionContext, out: DecisionResult
  `apps/aiyou_stack/aiyou-fastapi-services/app/main_ecosystem.py`
- `POST` `/evolve` → in: DecisionContext, out: DecisionResult
  `apps/aiyou_stack/aiyou-fastapi-services/app/main_ecosystem.py`
- `POST` `/wealth/analyze` → in: DecisionContext, out: DecisionResult
  `apps/aiyou_stack/aiyou-fastapi-services/app/main_ecosystem.py`
- `GET` `/ratings` → out: DecisionResult
  `apps/aiyou_stack/aiyou-fastapi-services/app/main_ecosystem.py`
- `GET` `/training/compare` → out: DecisionResult
  `apps/aiyou_stack/aiyou-fastapi-services/app/main_ecosystem.py`
- `GET` `/cheat-sheet` → out: DecisionResult
  `apps/aiyou_stack/aiyou-fastapi-services/app/main_ecosystem.py`
- `GET` `/ecosystem/status` → out: DecisionResult
  `apps/aiyou_stack/aiyou-fastapi-services/app/main_ecosystem.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `apps/aiyou_stack/aiyou-fastapi-services/app/main_ecosystem.py`

---
_Back to [overview.md](./overview.md)_
