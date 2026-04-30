# Judge_api

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Judge_api subsystem handles **4 routes** and touches: auth, db.

## Routes

- `POST` `/v1/judge` → in: JudgeRequest, out: HealthResponse [auth, db]
  `archive/broken/aiyou_fastapi_src/judge_api.py`
- `GET` `/v1/rulings/{decision_id}` params(decision_id) → out: HealthResponse [auth, db]
  `archive/broken/aiyou_fastapi_src/judge_api.py`
- `GET` `/v1/usage` → out: HealthResponse [auth, db]
  `archive/broken/aiyou_fastapi_src/judge_api.py`
- `DELETE` `/v1/rulings` → out: HealthResponse [auth, db]
  `archive/broken/aiyou_fastapi_src/judge_api.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `archive/broken/aiyou_fastapi_src/judge_api.py`

---
_Back to [overview.md](./overview.md)_
