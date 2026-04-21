# Trust

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Trust subsystem handles **1 routes** and touches: auth, db.

## Routes

- `GET` `/v1/trust/{agent_id}` params(agent_id) → out: GovernanceResponse [auth, db]
  `apps/aiyou_stack/aiyou-fastapi-services/src/main.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `apps/aiyou_stack/aiyou-fastapi-services/src/main.py`

---
_Back to [overview.md](./overview.md)_
