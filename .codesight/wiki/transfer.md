# Transfer

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Transfer subsystem handles **4 routes** and touches: auth, queue, payment.

## Routes

- `GET` `Checking out LFS objects` [auth, queue, payment, upload]
  `libs/cyberpunk_stack/git-lfs/tq/transfer.go`
- `GET` `Downloading LFS objects` [auth, queue, payment, upload]
  `libs/cyberpunk_stack/git-lfs/tq/transfer.go`
- `GET` `Uploading LFS objects` [auth, queue, payment, upload]
  `libs/cyberpunk_stack/git-lfs/tq/transfer.go`
- `GET` `action %q expires at %s` [auth, queue, payment, upload]
  `libs/cyberpunk_stack/git-lfs/tq/transfer.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `libs/cyberpunk_stack/git-lfs/tq/transfer.go`

---
_Back to [overview.md](./overview.md)_