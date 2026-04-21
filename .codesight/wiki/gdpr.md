# Gdpr

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Gdpr subsystem handles **5 routes** and touches: auth, db, queue, email.

## Routes

- `POST` `/delete` → in: DeletionRequest, out: DeletionReceipt [auth, db, queue, email, upload]
  `apps/counselconduit/api/gdpr.py`
- `POST` `/export` → in: DeletionRequest, out: DeletionReceipt [auth, db, queue, email, upload]
  `apps/counselconduit/api/gdpr.py`
- `GET` `/deletion-status/{receipt_id}` params(receipt_id) → out: DeletionReceipt [auth, db, queue, email, upload]
  `apps/counselconduit/api/gdpr.py`
- `POST` `/_execute-delete` → in: DeletionRequest, out: DeletionReceipt [auth, db, queue, email, upload]
  `apps/counselconduit/api/gdpr.py`
- `POST` `/_execute-export` → in: DeletionRequest, out: DeletionReceipt [auth, db, queue, email, upload]
  `apps/counselconduit/api/gdpr.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `apps/counselconduit/api/gdpr.py`

---
_Back to [overview.md](./overview.md)_
