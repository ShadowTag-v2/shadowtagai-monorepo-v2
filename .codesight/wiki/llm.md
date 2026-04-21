# Llm

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Llm subsystem handles **2 routes** and touches: auth, ai.

## Routes

- `POST` `/llm/{provider}` params(provider) [auth, ai]
  `external_repos/agents/Agentic-AI-Pipeline/mcp/server.py`
- `POST` `/llm/summarize` [auth, ai]
  `external_repos/agents/Agentic-AI-Pipeline/mcp/server.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/agents/Agentic-AI-Pipeline/mcp/server.py`

---
_Back to [overview.md](./overview.md)_