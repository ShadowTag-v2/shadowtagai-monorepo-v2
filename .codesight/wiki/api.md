# Api

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Api subsystem handles **11 routes** and touches: auth, cache, queue, payment.

## Routes

- `ALL` `/{user_id}` params(user_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{key_id}` params(key_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{storage_id}` params(storage_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{repository_id}` params(repository_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{inventory_id}` params(inventory_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{environment_id}` params(environment_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{template_id}` params(template_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{task_id}` params(task_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{schedule_id}` params(schedule_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{view_id}` params(view_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{integration_id}` params(integration_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/semaphore/api/router.go`

---
_Back to [overview.md](./overview.md)_