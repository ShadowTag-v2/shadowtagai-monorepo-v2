# Timeline

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Timeline subsystem handles **2 routes** and touches: db.

## Routes

- `POST` `/calculate` → in: TimelineRequest [db]
  `core/lawtrack/services/timeline.py`
- `GET` `/matter/{matter_id}` params(matter_id) [db]
  `core/lawtrack/services/timeline.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `core/lawtrack/services/timeline.py`

---
_Back to [overview.md](./overview.md)_
