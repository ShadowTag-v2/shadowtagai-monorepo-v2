# Integration

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Integration subsystem handles **2 routes** and touches: auth, queue, payment.

## Routes

- `GET` `X-Hub-Signature-256` [auth, queue, payment]
  `external_repos/semaphore/api/integration.go`
- `GET` `x-hub-signature` [auth, queue, payment]
  `external_repos/semaphore/api/integration.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/semaphore/api/integration.go`

---
_Back to [overview.md](./overview.md)_