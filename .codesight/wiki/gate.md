# Gate

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Gate subsystem handles **5 routes** and touches: auth, payment.

## Routes

- `ALL` `/gate/approve` [auth, payment]
  `external_repos/flagger/pkg/loadtester/server.go`
- `ALL` `/gate/halt` [auth, payment]
  `external_repos/flagger/pkg/loadtester/server.go`
- `ALL` `/gate/check` [auth, payment]
  `external_repos/flagger/pkg/loadtester/server.go`
- `ALL` `/gate/open` [auth, payment]
  `external_repos/flagger/pkg/loadtester/server.go`
- `ALL` `/gate/close` [auth, payment]
  `external_repos/flagger/pkg/loadtester/server.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/flagger/pkg/loadtester/server.go`

---
_Back to [overview.md](./overview.md)_