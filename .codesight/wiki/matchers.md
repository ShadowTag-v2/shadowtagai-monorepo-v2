# Matchers

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Matchers subsystem handles **3 routes** and touches: auth, cache, queue, payment.

## Routes

- `ALL` `/{integration_id}/matchers` params(integration_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{integration_id}/matchers/{matcher_id}` params(integration_id, matcher_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{integration_id}/matchers/{matcher_id}/refs` params(integration_id, matcher_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/semaphore/api/router.go`

---
_Back to [overview.md](./overview.md)_
