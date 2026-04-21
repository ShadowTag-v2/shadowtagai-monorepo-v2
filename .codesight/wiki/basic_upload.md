# Basic_upload

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Basic_upload subsystem handles **8 routes** and touches: auth, queue.

## Routes

- `GET` `No upload action for object: %s` [auth, queue, upload]
  `libs/cyberpunk_stack/git-lfs/tq/basic_upload.go`
- `GET` `Transfer-Encoding` [auth, queue, upload]
  `libs/cyberpunk_stack/git-lfs/tq/basic_upload.go`
- `GET` `basic upload` [auth, queue, upload]
  `libs/cyberpunk_stack/git-lfs/tq/basic_upload.go`
- `GET` `Received status %d` [auth, queue, upload]
  `libs/cyberpunk_stack/git-lfs/tq/basic_upload.go`
- `GET` `Invalid status for %s %s: %d` [auth, queue, upload]
  `libs/cyberpunk_stack/git-lfs/tq/basic_upload.go`
- `GET` `content type detection error` [auth, queue, upload]
  `libs/cyberpunk_stack/git-lfs/tq/basic_upload.go`
- `GET` `content type rewind failure` [auth, queue, upload]
  `libs/cyberpunk_stack/git-lfs/tq/basic_upload.go`
- `GET` `Should never ask this function to download` [auth, queue, upload]
  `libs/cyberpunk_stack/git-lfs/tq/basic_upload.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `libs/cyberpunk_stack/git-lfs/tq/basic_upload.go`

---
_Back to [overview.md](./overview.md)_