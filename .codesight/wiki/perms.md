# Perms

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Perms subsystem handles **2 routes** and touches: auth, cache, queue, payment.

## Routes

- `ALL` `/{template_id}/perms` params(template_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{template_id}/perms/{perm_id}` params(template_id, perm_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/semaphore/api/router.go`

---
_Back to [overview.md](./overview.md)_