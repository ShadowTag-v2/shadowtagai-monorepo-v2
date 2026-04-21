# Tool

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Tool subsystem handles **2 routes** and touches: auth.

## Routes

- `GET` `/tool/{toolName}` params(toolName) [auth]
  `external_repos/mcp-toolbox/internal/server/api.go`
- `POST` `/tool/{toolName}/invoke` params(toolName) [auth]
  `external_repos/mcp-toolbox/internal/server/api.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/mcp-toolbox/internal/server/api.go`

---
_Back to [overview.md](./overview.md)_