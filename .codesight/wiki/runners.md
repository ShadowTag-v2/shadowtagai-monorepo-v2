# Runners

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Runners subsystem handles **2 routes** and touches: auth, cache, queue, payment.

## Routes

- `ALL` `/runners` [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `GET` `X-Runner-Token` [auth, cache, payment]
  `external_repos/semaphore/api/runners/runners.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/semaphore/api/router.go`
- `external_repos/semaphore/api/runners/runners.go`

---
_Back to [overview.md](./overview.md)_
