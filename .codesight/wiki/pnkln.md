# Pnkln

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Pnkln subsystem handles **6 routes** and touches: db.

## Routes

- `POST` `/api/pnkln/execute` → in: ExecuteRequest, out: HealthResponse [db]
  `archive/agent_debris/api/main.py`
- `GET` `/api/pnkln/skills` → out: HealthResponse [db]
  `archive/agent_debris/api/main.py`
- `GET` `/api/pnkln/agents` → out: HealthResponse [db]
  `archive/agent_debris/api/main.py`
- `GET` `/api/pnkln/audit` → out: HealthResponse [db]
  `archive/agent_debris/api/main.py`
- `POST` `/api/pnkln/execute/skill/{skill_id}` params(skill_id) → in: ExecuteRequest, out: HealthResponse [db]
  `archive/agent_debris/api/main.py`
- `POST` `/api/pnkln/execute/agent/{agent_id}` params(agent_id) → in: ExecuteRequest, out: HealthResponse [db]
  `archive/agent_debris/api/main.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `archive/agent_debris/api/main.py`

---
_Back to [overview.md](./overview.md)_
