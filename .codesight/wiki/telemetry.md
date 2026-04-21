# Telemetry

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Telemetry subsystem handles **2 routes** and touches: auth, db, email, payment.

## Routes

- `POST` `/telemetry` → in: VehicleTelemetry, out: HealthResponse
  `apps/aiyou_stack/aiyou-fastapi-services/digital-freeway-api/main.py`
- `GET` `/api/v1/telemetry/roi` [auth, db, email, payment]
  `apps/legaltrack/src/legaltrack/main.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `apps/aiyou_stack/aiyou-fastapi-services/digital-freeway-api/main.py`
- `apps/legaltrack/src/legaltrack/main.py`

---
_Back to [overview.md](./overview.md)_
