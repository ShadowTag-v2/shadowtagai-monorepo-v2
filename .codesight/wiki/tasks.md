# Tasks

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Tasks subsystem handles **13 routes** and touches: auth, queue, cache, payment, db.

## Routes

- `GET` `/api/tasks` [auth, queue]
  `labs/uphillsnowball/api/main.py`
- `POST` `/api/tasks` → in: TaskCreate [auth, queue]
  `labs/uphillsnowball/api/main.py`
- `GET` `/api/tasks/{task_id}/stream` params(task_id) [auth, queue]
  `labs/uphillsnowball/api/main.py`
- `GET` `/api/tasks/{task_id}` params(task_id) → out: TaskResponse [auth, queue]
  `labs/uphillsnowball/server.py`
- `ALL` `/tasks/{task_id}/stop` params(task_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/tasks/{task_id}/reject` params(task_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/tasks/last` [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{template_id}/tasks` params(template_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{template_id}/tasks/last` params(template_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `GET` `limit` [auth, db, queue]
  `external_repos/semaphore/api/projects/tasks.go`
- `GET` `start` [auth, db, queue]
  `external_repos/semaphore/api/projects/tasks.go`
- `GET` `end` [auth, db, queue]
  `external_repos/semaphore/api/projects/tasks.go`
- `GET` `user_id` [auth, db, queue]
  `external_repos/semaphore/api/projects/tasks.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `labs/uphillsnowball/api/main.py`
- `labs/uphillsnowball/server.py`
- `external_repos/semaphore/api/router.go`
- `external_repos/semaphore/api/projects/tasks.go`

---
_Back to [overview.md](./overview.md)_
