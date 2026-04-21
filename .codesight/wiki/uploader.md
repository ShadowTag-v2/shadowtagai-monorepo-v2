# Uploader

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Uploader subsystem handles **14 routes** and touches: queue.

## Routes

- `GET` `ref %q:` [queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/uploader.go`
- `GET` `push` [queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/uploader.go`
- `GET` `missing objects` [queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/uploader.go`
- `GET` `failed` [queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/uploader.go`
- `GET` `Git LFS upload %s:` [queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/uploader.go`
- `GET` `  (missing) %s (%s)` [queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/uploader.go`
- `GET` `  (corrupt) %s (%s)` [queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/uploader.go`
- `GET` `hint: Your push was rejected due to missing or corrupt local objects.` [queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/uploader.go`
- `GET` `hint: You can disable this check with: `git config lfs.allowincompletepush true`` [queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/uploader.go`
- `GET` `Unable to push locked files:` [queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/uploader.go`
- `GET` `Cannot update locked files.` [queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/uploader.go`
- `GET` `warning: The above files would have halted this push.` [queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/uploader.go`
- `GET` `Consider unlocking your own locked files: (`git lfs unlock <path>`)` params(path) [queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/uploader.go`
- `GET` `Error uploading file %s (%s)` [queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/uploader.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `libs/cyberpunk_stack/git-lfs/commands/uploader.go`

---
_Back to [overview.md](./overview.md)_
