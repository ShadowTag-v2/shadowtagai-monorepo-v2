# Swarm_endpoint

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Swarm_endpoint subsystem handles **2 routes** and touches: payment.

## Routes

- `POST` `/vote` → in: SwarmVoteRequest, out: SwarmVoteResponse [payment]
  `apps/aiyou_stack/aiyou-fastapi-services/api/swarm_endpoint.py`
- `GET` `/usage` → in: dic, out: SwarmVoteResponse [payment]
  `apps/aiyou_stack/aiyou-fastapi-services/api/swarm_endpoint.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `apps/aiyou_stack/aiyou-fastapi-services/api/swarm_endpoint.py`

---
_Back to [overview.md](./overview.md)_