# Mcp

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Mcp subsystem handles **8 routes** and touches: auth, db, cache, queue.

## Routes

- `GET` `/{toolsetName}/sse` params(toolsetName) [auth, db, cache, queue]
  `external_repos/mcp-toolbox/internal/server/mcp.go`
- `GET` `/{toolsetName}` params(toolsetName) [auth, db, cache, queue]
  `external_repos/mcp-toolbox/internal/server/mcp.go`
- `POST` `/{toolsetName}` params(toolsetName) [auth, db, cache, queue]
  `external_repos/mcp-toolbox/internal/server/mcp.go`
- `DELETE` `/{toolsetName}` params(toolsetName) [auth, db, cache, queue]
  `external_repos/mcp-toolbox/internal/server/mcp.go`
- `GET` `X-Forwarded-Proto` [auth, db, cache, queue]
  `external_repos/mcp-toolbox/internal/server/mcp.go`
- `GET` `sessionId` [auth, db, cache, queue]
  `external_repos/mcp-toolbox/internal/server/mcp.go`
- `GET` `Mcp-Session-Id` [auth, db, cache, queue]
  `external_repos/mcp-toolbox/internal/server/mcp.go`
- `GET` `MCP-Protocol-Version` [auth, db, cache, queue]
  `external_repos/mcp-toolbox/internal/server/mcp.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/mcp-toolbox/internal/server/mcp.go`

---
_Back to [overview.md](./overview.md)_