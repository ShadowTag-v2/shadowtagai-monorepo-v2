# Vault

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Vault subsystem handles **1 routes** and touches: auth, db.

## Routes

- `POST` `/log-receipt` → in: ReceiptPayload [auth, db]
  `apps/headfade/api/routers/vault.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `apps/headfade/api/routers/vault.py`

---
_Back to [overview.md](./overview.md)_