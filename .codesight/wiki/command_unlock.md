# Command_unlock

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Command_unlock subsystem handles **7 routes** and touches: cache.

## Routes

- `GET` `Exactly one of --id or a set of paths must be provided` [cache]
  `libs/cyberpunk_stack/git-lfs/commands/command_unlock.go`
- `GET` `Unable to determine path: %v` [cache]
  `libs/cyberpunk_stack/git-lfs/commands/command_unlock.go`
- `GET` `Unlocked %s` [cache]
  `libs/cyberpunk_stack/git-lfs/commands/command_unlock.go`
- `GET` `Unable to unlock %v: %v` [cache]
  `libs/cyberpunk_stack/git-lfs/commands/command_unlock.go`
- `GET` `Unlocked Lock %s` [cache]
  `libs/cyberpunk_stack/git-lfs/commands/command_unlock.go`
- `GET` `warning: unlocking with uncommitted changes because --force` [cache]
  `libs/cyberpunk_stack/git-lfs/commands/command_unlock.go`
- `GET` `Cannot unlock file with uncommitted changes` [cache]
  `libs/cyberpunk_stack/git-lfs/commands/command_unlock.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `libs/cyberpunk_stack/git-lfs/commands/command_unlock.go`

---
_Back to [overview.md](./overview.md)_