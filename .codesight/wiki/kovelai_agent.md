# Kovelai_agent

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Kovelai_agent subsystem handles **3 routes** and touches: auth, cache, payment.

## Routes

- `POST` `/api/copilotkit` [auth, cache, payment]
  `apps/kovelai/agent/kovelai_agent.py`
- `POST` `/api/oracle-studio` [auth, cache, payment]
  `apps/kovelai/agent/kovelai_agent.py`
- `POST` `/api/verb-audit` [auth, cache, payment]
  `apps/kovelai/agent/kovelai_agent.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `apps/kovelai/agent/kovelai_agent.py`

---
_Back to [overview.md](./overview.md)_
