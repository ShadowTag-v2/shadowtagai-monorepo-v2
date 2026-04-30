# Threads

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Threads subsystem handles **11 routes** and touches: auth, db, cache.

## Routes

- `POST` `/v1/threads` → in: ThreadCreateRequest [auth, db, cache]
  `external_repos/apps/CortexLTM/cortexltm/api.py`
- `GET` `/v1/threads` [auth, db, cache]
  `external_repos/apps/CortexLTM/cortexltm/api.py`
- `GET` `/v1/threads/{thread_id}/events` params(thread_id) [auth, db, cache]
  `external_repos/apps/CortexLTM/cortexltm/api.py`
- `PATCH` `/v1/threads/{thread_id}` params(thread_id) [auth, db, cache]
  `external_repos/apps/CortexLTM/cortexltm/api.py`
- `DELETE` `/v1/threads/{thread_id}` params(thread_id) [auth, db, cache]
  `external_repos/apps/CortexLTM/cortexltm/api.py`
- `POST` `/v1/threads/{thread_id}/promote-core-memory` params(thread_id) → in: ThreadCreateRequest [auth, db, cache]
  `external_repos/apps/CortexLTM/cortexltm/api.py`
- `POST` `/v1/threads/{thread_id}/events` params(thread_id) → in: ThreadCreateRequest [auth, db, cache]
  `external_repos/apps/CortexLTM/cortexltm/api.py`
- `POST` `/v1/threads/{thread_id}/events/{event_id}/reaction` params(thread_id, event_id) → in: ThreadCreateRequest [auth, db, cache]
  `external_repos/apps/CortexLTM/cortexltm/api.py`
- `GET` `/v1/threads/{thread_id}/summary` params(thread_id) [auth, db, cache]
  `external_repos/apps/CortexLTM/cortexltm/api.py`
- `POST` `/v1/threads/{thread_id}/memory-context` params(thread_id) → in: ThreadCreateRequest [auth, db, cache]
  `external_repos/apps/CortexLTM/cortexltm/api.py`
- `POST` `/v1/threads/{thread_id}/chat` params(thread_id) → in: ThreadCreateRequest [auth, db, cache]
  `external_repos/apps/CortexLTM/cortexltm/api.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/apps/CortexLTM/cortexltm/api.py`

---
_Back to [overview.md](./overview.md)_
