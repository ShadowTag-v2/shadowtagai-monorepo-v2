# Audit

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Audit subsystem handles **1 routes** and touches: auth, cache.

## Routes

- `GET` `/api/v1/audit/{decision_id}` params(decision_id) → out: DecisionResult [auth, cache]
  `archive/agent_debris/app/main.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `archive/agent_debris/app/main.py`

---
_Back to [overview.md](./overview.md)_