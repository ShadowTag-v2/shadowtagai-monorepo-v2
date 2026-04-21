# Command_clone

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Command_clone subsystem handles **7 routes** and touches: payment.

## Routes

- `GET` `WARNING: `git lfs clone` is deprecated and will not be updated\n          with new flags from `git clone`` [payment, upload]
  `libs/cyberpunk_stack/git-lfs/commands/command_clone.go`
- `GET` ``git clone` has been updated in upstream Git to have comparable\nspeeds to `git lfs clone`.` [payment, upload]
  `libs/cyberpunk_stack/git-lfs/commands/command_clone.go`
- `GET` `Error(s) during clone:` [payment, upload]
  `libs/cyberpunk_stack/git-lfs/commands/command_clone.go`
- `GET` `Unable to derive current working dir: %v` [payment, upload]
  `libs/cyberpunk_stack/git-lfs/commands/command_clone.go`
- `GET` `Unable to find clone dir at %q` [payment, upload]
  `libs/cyberpunk_stack/git-lfs/commands/command_clone.go`
- `GET` `Unable to change directory to clone dir %q: %v` [payment, upload]
  `libs/cyberpunk_stack/git-lfs/commands/command_clone.go`
- `GET` `Error performing `git lfs pull` for submodules: %v` [payment, upload]
  `libs/cyberpunk_stack/git-lfs/commands/command_clone.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `libs/cyberpunk_stack/git-lfs/commands/command_clone.go`

---
_Back to [overview.md](./overview.md)_