# Detach

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Detach subsystem handles **1 routes** and touches: auth, cache, queue, payment.

## Routes

- `ALL` `/{inventory_id}/detach` params(inventory_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/semaphore/api/router.go`

---
_Back to [overview.md](./overview.md)_
