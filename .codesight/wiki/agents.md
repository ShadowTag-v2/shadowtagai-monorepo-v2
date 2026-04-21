# Agents

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Agents subsystem handles **3 routes** and touches: auth, queue.

## Routes

- `POST` `/query` → in: SwarmQuery [auth, queue]
  `apps/aiyou-fastapi-services/routers/agents.py`
- `POST` `/wealth` → in: DebateRequest, out: DebateResult
  `archive/agent_debris/app/routes/agents.py`
- `GET` `/api/agents` [auth, queue]
  `labs/uphillsnowball/api/main.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `apps/aiyou-fastapi-services/routers/agents.py`
- `archive/agent_debris/app/routes/agents.py`
- `labs/uphillsnowball/api/main.py`

---
_Back to [overview.md](./overview.md)_
