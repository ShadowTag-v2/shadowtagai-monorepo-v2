# Lockverifier

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Lockverifier subsystem handles **7 routes** and touches: auth.

## Routes

- `GET` `no ref specified for verification` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/commands/lockverifier.go`
- `GET` `warning: Authentication error: %s` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/commands/lockverifier.go`
- `GET` `error: Authentication error: %s` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/commands/lockverifier.go`
- `GET` `Remote %q does not support the Git LFS locking API. Consider disabling it with:` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/commands/lockverifier.go`
- `GET` `Locking support detected on remote %q. Consider enabling it with:` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/commands/lockverifier.go`
- `GET` `warning: error adding %q lock for ref %q: %+v` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/commands/lockverifier.go`
- `GET` `lfs` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/commands/lockverifier.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `libs/cyberpunk_stack/git-lfs/commands/lockverifier.go`

---
_Back to [overview.md](./overview.md)_