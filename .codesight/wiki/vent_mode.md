# Vent_mode

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Vent_mode subsystem handles **4 routes** and touches: auth, cache, payment.

## Routes

- `POST` `/start` → in: VentSessionRequest, out: VentCheckoutResponse [auth, cache, payment]
  `apps/counselconduit/api/vent_mode.py`
- `POST` `/message` → in: VentSessionRequest, out: VentCheckoutResponse [auth, cache, payment]
  `apps/counselconduit/api/vent_mode.py`
- `POST` `/message/stream` → in: VentSessionRequest, out: VentCheckoutResponse [auth, cache, payment]
  `apps/counselconduit/api/vent_mode.py`
- `POST` `/summarize` → in: VentSessionRequest, out: VentCheckoutResponse [auth, cache, payment]
  `apps/counselconduit/api/vent_mode.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `apps/counselconduit/api/vent_mode.py`

---
_Back to [overview.md](./overview.md)_