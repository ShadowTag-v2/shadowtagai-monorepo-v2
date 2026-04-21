# Swarm_router

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Swarm_router subsystem handles **7 routes** and touches: db.

## Routes

- `GET` `/agents` [db]
  `archive/agent_debris/app/routers/swarm_router.py`
- `GET` `/agents/{agent_id}` params(agent_id) [db]
  `archive/agent_debris/app/routers/swarm_router.py`
- `POST` `/spawn` → in: SpawnRequest [db]
  `archive/agent_debris/app/routers/swarm_router.py`
- `POST` `/task` → in: SpawnRequest [db]
  `archive/agent_debris/app/routers/swarm_router.py`
- `POST` `/revenue` → in: SpawnRequest [db]
  `archive/agent_debris/app/routers/swarm_router.py`
- `GET` `/tree` [db]
  `archive/agent_debris/app/routers/swarm_router.py`
- `POST` `/activate` → in: SpawnRequest [db]
  `archive/agent_debris/app/routers/swarm_router.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `archive/agent_debris/app/routers/swarm_router.py`

---
_Back to [overview.md](./overview.md)_