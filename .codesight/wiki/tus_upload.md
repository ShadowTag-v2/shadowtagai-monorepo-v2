# Tus_upload

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Tus_upload subsystem handles **4 routes** and touches: auth.

## Routes

- `GET` `Upload-Offset` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/tq/tus_upload.go`
- `GET` `missing Upload-Offset header from tus.io HEAD response at %q, contact server admin` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/tq/tus_upload.go`
- `GET` `invalid Upload-Offset value %q in response from tus.io HEAD at %q, contact server admin` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/tq/tus_upload.go`
- `GET` `tus.io upload` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/tq/tus_upload.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `libs/cyberpunk_stack/git-lfs/tq/tus_upload.go`

---
_Back to [overview.md](./overview.md)_
