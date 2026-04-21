# Users

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Users subsystem handles **3 routes** and touches: auth, db, queue.

## Routes

- `POST` `/users` → in: UserCreate, out: UserResponse [auth, db]
  `apps/aiyou_stack/aiyou-fastapi-services/main.py`
- `GET` `/users` → out: UserResponse [auth, db]
  `apps/aiyou_stack/aiyou-fastapi-services/main.py`
- `GET` `s` [auth, db, queue]
  `external_repos/semaphore/api/users.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `apps/aiyou_stack/aiyou-fastapi-services/main.py`
- `external_repos/semaphore/api/users.go`

---
_Back to [overview.md](./overview.md)_
