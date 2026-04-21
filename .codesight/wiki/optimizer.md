# Optimizer

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Optimizer subsystem handles **1 routes** and touches: auth, db, cache.

## Routes

- `POST` `/process` → in: BackgroundTasks [auth, db, cache]
  `archive/agent_debris/app/services/optimizer.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `archive/agent_debris/app/services/optimizer.py`

---
_Back to [overview.md](./overview.md)_
