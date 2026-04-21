# Agent

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Agent subsystem handles **2 routes** and touches: queue.

## Routes

- `POST` `/api/agent/stream` → in: AgentRequest [queue]
  `labs/uphillsnowball/tauri-agentic-workspace/engine/main.py`
- `POST` `/api/v1/agent/execute` → in: AgentExecutionRequest
  `scripts/legacy/app.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `labs/uphillsnowball/tauri-agentic-workspace/engine/main.py`
- `scripts/legacy/app.py`

---
_Back to [overview.md](./overview.md)_