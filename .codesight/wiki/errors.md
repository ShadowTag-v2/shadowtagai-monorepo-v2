# Errors

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Errors subsystem handles **6 routes** and touches: auth.

## Routes

- `GET` `Retry-After` [auth]
  `libs/cyberpunk_stack/git-lfs/lfshttp/errors.go`
- `GET` `Invalid HTTP status for %s %s: %d` [auth]
  `libs/cyberpunk_stack/git-lfs/lfshttp/errors.go`
- `GET` `Client error %s from HTTP %d` [auth]
  `libs/cyberpunk_stack/git-lfs/lfshttp/errors.go`
- `GET` `Server error %s from HTTP %d` [auth]
  `libs/cyberpunk_stack/git-lfs/lfshttp/errors.go`
- `GET` `corrupt object: %s (%s)`
  `libs/cyberpunk_stack/git-lfs/tq/errors.go`
- `GET` `missing object: %s (%s)`
  `libs/cyberpunk_stack/git-lfs/tq/errors.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `libs/cyberpunk_stack/git-lfs/lfshttp/errors.go`
- `libs/cyberpunk_stack/git-lfs/tq/errors.go`

---
_Back to [overview.md](./overview.md)_
