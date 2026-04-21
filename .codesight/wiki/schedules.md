# Schedules

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Schedules subsystem handles **1 routes** and touches: auth, cache, queue, payment.

## Routes

- `ALL` `/{template_id}/schedules` params(template_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/semaphore/api/router.go`

---
_Back to [overview.md](./overview.md)_