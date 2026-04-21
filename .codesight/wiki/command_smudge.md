# Command_smudge

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Command_smudge subsystem handles **5 routes** and touches: cache, queue, payment.

## Routes

- `GET` `Unable to parse pointer at: %q` [cache, queue, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_smudge.go`
- `GET` `Error downloading object: %s (%s): %s` [cache, queue, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_smudge.go`
- `GET` `This command should be run by the Git 'smudge' filter` [cache, queue, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_smudge.go`
- `GET` `Possibly malformed smudge on Windows: see `git lfs help smudge` for more info.` [cache, queue, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_smudge.go`
- `GET` `unknown file` [cache, queue, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_smudge.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `libs/cyberpunk_stack/git-lfs/commands/command_smudge.go`

---
_Back to [overview.md](./overview.md)_