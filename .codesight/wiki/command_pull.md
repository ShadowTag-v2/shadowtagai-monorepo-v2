# Command_pull

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Command_pull subsystem handles **3 routes** and touches: queue, payment.

## Routes

- `GET` `Could not pull` [queue, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_pull.go`
- `GET` `Failed to fetch some objects from '%s'` [queue, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_pull.go`
- `GET` `Skipping object checkout, Git LFS is not installed for this repository.\nConsider installing it with 'git lfs install'.` [queue, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_pull.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `libs/cyberpunk_stack/git-lfs/commands/command_pull.go`

---
_Back to [overview.md](./overview.md)_
