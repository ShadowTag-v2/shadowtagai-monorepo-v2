# Api_flyingmonkeys_api

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Api_flyingmonkeys_api subsystem handles **15 routes** and touches: auth, db, queue, ai.

## Routes

- `POST` `/hunt` → out: JobResponse [auth, db, queue, ai]
  `control/legacy_workspaces/archive_swarm/api_flyingmonkeys_api.py`
- `POST` `/swarm` → out: JobResponse [auth, db, queue, ai]
  `control/legacy_workspaces/archive_swarm/api_flyingmonkeys_api.py`
- `POST` `/brainstorm` → out: JobResponse [auth, db, queue, ai]
  `control/legacy_workspaces/archive_swarm/api_flyingmonkeys_api.py`
- `POST` `/single` → out: JobResponse [auth, db, queue, ai]
  `control/legacy_workspaces/archive_swarm/api_flyingmonkeys_api.py`
- `POST` `/bulk_analyze` → out: JobResponse [auth, db, queue, ai]
  `control/legacy_workspaces/archive_swarm/api_flyingmonkeys_api.py`
- `GET` `/cost_stats` → out: JobResponse [auth, db, queue, ai]
  `control/legacy_workspaces/archive_swarm/api_flyingmonkeys_api.py`
- `POST` `/hunt/async` → out: JobResponse [auth, db, queue, ai]
  `control/legacy_workspaces/archive_swarm/api_flyingmonkeys_api.py`
- `POST` `/puzzle/start` → out: JobResponse [auth, db, queue, ai]
  `control/legacy_workspaces/archive_swarm/api_flyingmonkeys_api.py`
- `GET` `/puzzle/{room_id}/status` params(room_id) → out: JobResponse [auth, db, queue, ai]
  `control/legacy_workspaces/archive_swarm/api_flyingmonkeys_api.py`
- `POST` `/puzzle/{room_id}/solve` params(room_id) → out: JobResponse [auth, db, queue, ai]
  `control/legacy_workspaces/archive_swarm/api_flyingmonkeys_api.py`
- `POST` `/puzzle/{room_id}/code` params(room_id) → out: JobResponse [auth, db, queue, ai]
  `control/legacy_workspaces/archive_swarm/api_flyingmonkeys_api.py`
- `POST` `/puzzle/{room_id}/auto` params(room_id) → out: JobResponse [auth, db, queue, ai]
  `control/legacy_workspaces/archive_swarm/api_flyingmonkeys_api.py`
- `POST` `/puzzle/{room_id}/vault_interaction` params(room_id) → out: JobResponse [auth, db, queue, ai]
  `control/legacy_workspaces/archive_swarm/api_flyingmonkeys_api.py`
- `GET` `/puzzle/{room_id}/history` params(room_id) → out: JobResponse [auth, db, queue, ai]
  `control/legacy_workspaces/archive_swarm/api_flyingmonkeys_api.py`
- `GET` `/vertex_test` → out: JobResponse [auth, db, queue, ai]
  `control/legacy_workspaces/archive_swarm/api_flyingmonkeys_api.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `control/legacy_workspaces/archive_swarm/api_flyingmonkeys_api.py`

---
_Back to [overview.md](./overview.md)_
