# Login

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Login subsystem handles **5 routes** and touches: auth, queue, db.

## Routes

- `GET` `state` [auth, queue]
  `external_repos/opentofu/internal/command/login.go`
- `GET` `code` [auth, queue]
  `external_repos/opentofu/internal/command/login.go`
- `GET` `X-Real-IP` [auth, db]
  `external_repos/semaphore/api/login.go`
- `GET` `user-agent` [auth, db]
  `external_repos/semaphore/api/login.go`
- `GET` `return` [auth, db]
  `external_repos/semaphore/api/login.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/opentofu/internal/command/login.go`
- `external_repos/semaphore/api/login.go`

---
_Back to [overview.md](./overview.md)_
