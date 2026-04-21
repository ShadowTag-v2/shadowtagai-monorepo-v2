# Terraform

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Terraform subsystem handles **5 routes** and touches: auth, cache, queue, payment.

## Routes

- `ALL` `/{inventory_id}/terraform/aliases` params(inventory_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{inventory_id}/terraform/aliases/{alias_id}` params(inventory_id, alias_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{inventory_id}/terraform/states` params(inventory_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{inventory_id}/terraform/states/latest` params(inventory_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{inventory_id}/terraform/states/{state_id}` params(inventory_id, state_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/semaphore/api/router.go`

---
_Back to [overview.md](./overview.md)_