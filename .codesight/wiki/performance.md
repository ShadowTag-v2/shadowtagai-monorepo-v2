# Performance

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Performance subsystem handles **9 routes** and touches: auth, db, cache.

## Routes

- `GET` `/bottlenecks` → in: in, out: PerformanceReport [auth, db, cache]
  `archive/agent_debris/app/routes/performance.py`
- `GET` `/bottlenecks/{bottleneck_id}/fix` params(bottleneck_id) → in: in, out: PerformanceReport [auth, db, cache]
  `archive/agent_debris/app/routes/performance.py`
- `GET` `/slow-endpoints` → in: in, out: PerformanceReport [auth, db, cache]
  `archive/agent_debris/app/routes/performance.py`
- `GET` `/trends/{endpoint:path}` params(path) → in: in, out: PerformanceReport [auth, db, cache]
  `archive/agent_debris/app/routes/performance.py`
- `GET` `/n-plus-one` → in: in, out: PerformanceReport [auth, db, cache]
  `archive/agent_debris/app/routes/performance.py`
- `GET` `/memory-leaks` → in: in, out: PerformanceReport [auth, db, cache]
  `archive/agent_debris/app/routes/performance.py`
- `GET` `/optimization-suggestions` → in: in, out: PerformanceReport [auth, db, cache]
  `archive/agent_debris/app/routes/performance.py`
- `GET` `/cache/stats` → in: in, out: PerformanceReport [auth, db, cache]
  `archive/agent_debris/app/routes/performance.py`
- `POST` `/cache/clear` → out: PerformanceReport [auth, db, cache]
  `archive/agent_debris/app/routes/performance.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `archive/agent_debris/app/routes/performance.py`

---
_Back to [overview.md](./overview.md)_
