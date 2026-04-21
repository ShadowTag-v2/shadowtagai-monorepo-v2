# Toolset

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Toolset subsystem handles **2 routes** and touches: auth.

## Routes

- `GET` `/toolset` [auth]
  `external_repos/mcp-toolbox/internal/server/api.go`
- `GET` `/toolset/{toolsetName}` params(toolsetName) [auth]
  `external_repos/mcp-toolbox/internal/server/api.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/mcp-toolbox/internal/server/api.go`

---
_Back to [overview.md](./overview.md)_