# Util

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Util subsystem handles **6 routes** and touches: auth, db.

## Routes

- `GET` `https://oauth2.googleapis.com/tokeninfo` [auth, db]
  `external_repos/mcp-toolbox/internal/sources/util.go`
- `GET` `User-Agent`
  `external_repos/mcp-toolbox/internal/util/util.go`
- `GET` `GIT_LFS_PROGRESS`
  `libs/cyberpunk_stack/git-lfs/lfs/util.go`
- `GET` `GIT_LFS_PROGRESS must be an absolute path`
  `libs/cyberpunk_stack/git-lfs/lfs/util.go`
- `GET` `error writing Git LFS %s progress to %s: %s`
  `libs/cyberpunk_stack/git-lfs/lfs/util.go`
- `GET` `unable to get working dir: %v`
  `libs/cyberpunk_stack/git-lfs/lfs/util.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/mcp-toolbox/internal/sources/util.go`
- `external_repos/mcp-toolbox/internal/util/util.go`
- `libs/cyberpunk_stack/git-lfs/lfs/util.go`

---
_Back to [overview.md](./overview.md)_
