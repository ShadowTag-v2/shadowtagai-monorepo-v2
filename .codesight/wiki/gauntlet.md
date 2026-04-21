# Gauntlet

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Gauntlet subsystem handles **1 routes** and touches: auth, queue.

## Routes

- `POST` `/api/gauntlet/evaluate` → in: TaskCreate [auth, queue]
  `labs/uphillsnowball/api/main.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `labs/uphillsnowball/api/main.py`

---
_Back to [overview.md](./overview.md)_