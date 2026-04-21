# Pipeline

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Pipeline subsystem handles **4 routes** and touches: auth, ai.

## Routes

- `POST` `/pipeline/{name}` params(name) [auth, ai]
  `external_repos/agents/Agentic-AI-Pipeline/mcp/server.py`
- `POST` `/pipeline/coding/stream` [auth, ai]
  `external_repos/agents/Agentic-AI-Pipeline/mcp/server.py`
- `POST` `/pipeline/rag/ask` [auth, ai]
  `external_repos/agents/Agentic-AI-Pipeline/mcp/server.py`
- `POST` `/pipeline/data/analyze` [auth, ai]
  `external_repos/agents/Agentic-AI-Pipeline/mcp/server.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/agents/Agentic-AI-Pipeline/mcp/server.py`

---
_Back to [overview.md](./overview.md)_