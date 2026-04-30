# Command_push

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Command_push subsystem handles **6 routes** and touches: queue.

## Routes

- `GET` `Specify a remote and a remote branch name (`git lfs push origin main`)` [queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/command_push.go`
- `GET` `At least one object ID must be supplied with --object-id` [queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/command_push.go`
- `GET` `At least one ref must be supplied without --all` [queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/command_push.go`
- `GET` `Error getting local refs.` [queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/command_push.go`
- `GET` `Unable to find local media path:` [queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/command_push.go`
- `GET` `Unable to stat local media path` [queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/command_push.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `libs/cyberpunk_stack/git-lfs/commands/command_push.go`

---
_Back to [overview.md](./overview.md)_
