# Aliases

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Aliases subsystem handles **4 routes** and touches: auth, cache, queue, payment.

## Routes

- `ALL` `/aliases` [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/aliases/{alias_id}` params(alias_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{integration_id}/aliases` params(integration_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{integration_id}/aliases/{alias_id}` params(integration_id, alias_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/semaphore/api/router.go`

---
_Back to [overview.md](./overview.md)_