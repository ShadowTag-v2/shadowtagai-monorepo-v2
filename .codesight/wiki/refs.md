# Refs

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Refs subsystem handles **8 routes** and touches: auth, cache, queue, payment.

## Routes

- `ALL` `/{key_id}/refs` params(key_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{storage_id}/refs` params(storage_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{repository_id}/refs` params(repository_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{inventory_id}/refs` params(inventory_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{environment_id}/refs` params(environment_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{template_id}/refs` params(template_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{integration_id}/refs` params(integration_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `GET` `push.default`
  `libs/cyberpunk_stack/git-lfs/git/refs.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/semaphore/api/router.go`
- `libs/cyberpunk_stack/git-lfs/git/refs.go`

---
_Back to [overview.md](./overview.md)_
