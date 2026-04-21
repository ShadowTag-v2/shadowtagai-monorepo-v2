# Ansible

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Ansible subsystem handles **2 routes** and touches: auth, cache, queue, payment.

## Routes

- `ALL` `/{task_id}/ansible/hosts` params(task_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{task_id}/ansible/errors` params(task_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/semaphore/api/router.go`

---
_Back to [overview.md](./overview.md)_