# Policies

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Policies subsystem handles **3 routes** and touches: auth, db.

## Routes

- `POST` `/v1/policies` → in: MissionRequest, out: GovernanceResponse [auth, db]
  `apps/aiyou_stack/aiyou-fastapi-services/src/main.py`
- `PUT` `/v1/policies/{policy_id}` params(policy_id) → out: GovernanceResponse [auth, db]
  `apps/aiyou_stack/aiyou-fastapi-services/src/main.py`
- `DELETE` `/v1/policies/{policy_id}` params(policy_id) → out: GovernanceResponse [auth, db]
  `apps/aiyou_stack/aiyou-fastapi-services/src/main.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `apps/aiyou_stack/aiyou-fastapi-services/src/main.py`

---
_Back to [overview.md](./overview.md)_
