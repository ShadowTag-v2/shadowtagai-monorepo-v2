# Ingestion

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Ingestion subsystem handles **15 routes** and touches: auth, db.

## Routes

- `GET` `/report` → in: in, out: IngestionReport [auth, db]
  `archive/agent_debris/app/routes/ingestion.py`
- `GET` `/runtime-efficiency` → in: in, out: IngestionReport [auth, db]
  `archive/agent_debris/app/routes/ingestion.py`
- `GET` `/quality-gates` → in: in, out: IngestionReport [auth, db]
  `archive/agent_debris/app/routes/ingestion.py`
- `GET` `/source-coverage` → in: in, out: IngestionReport [auth, db]
  `archive/agent_debris/app/routes/ingestion.py`
- `GET` `/source-coverage/gaps` → in: in, out: IngestionReport [auth, db]
  `archive/agent_debris/app/routes/ingestion.py`
- `GET` `/source-coverage/{source_type}` params(source_type) → in: in, out: IngestionReport [auth, db]
  `archive/agent_debris/app/routes/ingestion.py`
- `GET` `/tier-distribution` → in: in, out: IngestionReport [auth, db]
  `archive/agent_debris/app/routes/ingestion.py`
- `GET` `/ethical-compliance` → in: in, out: IngestionReport [auth, db]
  `archive/agent_debris/app/routes/ingestion.py`
- `GET` `/ethical-compliance/score` → in: in, out: IngestionReport [auth, db]
  `archive/agent_debris/app/routes/ingestion.py`
- `GET` `/ethical-compliance/violations` → in: in, out: IngestionReport [auth, db]
  `archive/agent_debris/app/routes/ingestion.py`
- `GET` `/costs/monthly` → in: in, out: IngestionReport [auth, db]
  `archive/agent_debris/app/routes/ingestion.py`
- `GET` `/briefing-delivery` → in: in, out: IngestionReport [auth, db]
  `archive/agent_debris/app/routes/ingestion.py`
- `GET` `/summary` → in: in, out: IngestionReport [auth, db]
  `archive/agent_debris/app/routes/ingestion.py`
- `POST` `/check-robots-txt` → in: st, out: IngestionReport [auth, db]
  `archive/agent_debris/app/routes/ingestion.py`
- `POST` `/check-rate-limit` → in: st, out: IngestionReport [auth, db]
  `archive/agent_debris/app/routes/ingestion.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `archive/agent_debris/app/routes/ingestion.py`

---
_Back to [overview.md](./overview.md)_
