# Rollback

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Rollback subsystem handles **3 routes** and touches: auth, payment.

## Routes

- `ALL` `/rollback/check` [auth, payment]
  `external_repos/flagger/pkg/loadtester/server.go`
- `ALL` `/rollback/open` [auth, payment]
  `external_repos/flagger/pkg/loadtester/server.go`
- `ALL` `/rollback/close` [auth, payment]
  `external_repos/flagger/pkg/loadtester/server.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/flagger/pkg/loadtester/server.go`

---
_Back to [overview.md](./overview.md)_
