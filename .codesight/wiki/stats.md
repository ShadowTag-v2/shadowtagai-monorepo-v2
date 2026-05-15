# Stats

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Stats subsystem handles **2 routes** and touches: auth, cache, queue, payment.

## Routes

- `GET` `/stats` → out: FeedResponse [auth, upload]
  `apps/aiyou_stack/aiyou-fastapi-services/aiyou/api.py`
- `ALL` `/{template_id}/stats` params(template_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `apps/aiyou_stack/aiyou-fastapi-services/aiyou/api.py`
- `external_repos/semaphore/api/router.go`

---
_Back to [overview.md](./overview.md)_
