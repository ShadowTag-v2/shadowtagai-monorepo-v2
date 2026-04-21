# Mgmt

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Mgmt subsystem handles **8 routes** and touches: auth, db.

## Routes

- `ALL` `/mgmt` [auth, db]
  `libs/cyberpunk_stack/lfs-test-server/mgmt.go`
- `ALL` `/mgmt/objects` [auth, db]
  `libs/cyberpunk_stack/lfs-test-server/mgmt.go`
- `ALL` `/mgmt/raw/{oid}` params(oid) [auth, db]
  `libs/cyberpunk_stack/lfs-test-server/mgmt.go`
- `ALL` `/mgmt/locks` [auth, db]
  `libs/cyberpunk_stack/lfs-test-server/mgmt.go`
- `ALL` `/mgmt/users` [auth, db]
  `libs/cyberpunk_stack/lfs-test-server/mgmt.go`
- `ALL` `/mgmt/add` [auth, db]
  `libs/cyberpunk_stack/lfs-test-server/mgmt.go`
- `ALL` `/mgmt/del` [auth, db]
  `libs/cyberpunk_stack/lfs-test-server/mgmt.go`
- `ALL` `/mgmt/css/{file}` params(file) [auth, db]
  `libs/cyberpunk_stack/lfs-test-server/mgmt.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `libs/cyberpunk_stack/lfs-test-server/mgmt.go`

---
_Back to [overview.md](./overview.md)_