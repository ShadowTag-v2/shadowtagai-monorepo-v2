# Mcp_server

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Mcp_server subsystem handles **1 routes** and touches: auth, db, queue.

## Routes

- `POST` `/execute` → in: CodeExecutionRequest, out: CodeExecutionResponse [auth, db, queue]
  `apps/aiyou_stack/aiyou-fastapi-services/mcp-validation/mcp_server.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `apps/aiyou_stack/aiyou-fastapi-services/mcp-validation/mcp_server.py`

---
_Back to [overview.md](./overview.md)_