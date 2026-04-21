# Objects

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Objects subsystem handles **4 routes** and touches: auth, db.

## Routes

- `ALL` `/{user}/{repo}/objects/batch` params(user, repo) [auth, db, upload]
  `libs/cyberpunk_stack/lfs-test-server/server.go`
- `ALL` `/{user}/{repo}/objects` params(user, repo) [auth, db, upload]
  `libs/cyberpunk_stack/lfs-test-server/server.go`
- `ALL` `/objects/batch` [auth, db, upload]
  `libs/cyberpunk_stack/lfs-test-server/server.go`
- `ALL` `/objects` [auth, db, upload]
  `libs/cyberpunk_stack/lfs-test-server/server.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `libs/cyberpunk_stack/lfs-test-server/server.go`

---
_Back to [overview.md](./overview.md)_