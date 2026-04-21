# Fastapi_kovel_enclave

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Fastapi_kovel_enclave subsystem handles **4 routes** and touches: auth, cache, email, payment.

## Routes

- `POST` `/heartbeat` → out: QueryResponse [auth, cache, email, payment]
  `apps/counselconduit/api/fastapi_kovel_enclave.py`
- `POST` `/enclave/v1/query` → out: QueryResponse [auth, cache, email, payment]
  `apps/counselconduit/api/fastapi_kovel_enclave.py`
- `POST` `/enclave/v1/query/stream` → out: QueryResponse [auth, cache, email, payment]
  `apps/counselconduit/api/fastapi_kovel_enclave.py`
- `GET` `/enclave/v1/health` → out: QueryResponse [auth, cache, email, payment]
  `apps/counselconduit/api/fastapi_kovel_enclave.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `apps/counselconduit/api/fastapi_kovel_enclave.py`

---
_Back to [overview.md](./overview.md)_