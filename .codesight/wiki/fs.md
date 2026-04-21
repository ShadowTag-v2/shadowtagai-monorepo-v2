# Fs

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Fs subsystem handles **5 routes** and touches: auth, ai.

## Routes

- `POST` `/fs/write` [auth, ai]
  `external_repos/agents/Agentic-AI-Pipeline/mcp/server.py`
- `GET` `/fs/read` [auth, ai]
  `external_repos/agents/Agentic-AI-Pipeline/mcp/server.py`
- `GET` `too short object ID: %q`
  `libs/cyberpunk_stack/git-lfs/fs/fs.go`
- `GET` `error trying to create local storage directory in %q: %s`
  `libs/cyberpunk_stack/git-lfs/fs/fs.go`
- `GET` `GIT_ALTERNATE_OBJECT_DIRECTORIES`
  `libs/cyberpunk_stack/git-lfs/fs/fs.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/agents/Agentic-AI-Pipeline/mcp/server.py`
- `libs/cyberpunk_stack/git-lfs/fs/fs.go`

---
_Back to [overview.md](./overview.md)_
