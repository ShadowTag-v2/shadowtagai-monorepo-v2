# Command_checkout

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Command_checkout subsystem handles **15 routes** and touches: queue, payment.

## Routes

- `GET` `This operation must be run in a work tree.` [queue, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_checkout.go`
- `GET` `Error parsing args: %v` [queue, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_checkout.go`
- `GET` `--to requires exactly one Git LFS object file path` [queue, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_checkout.go`
- `GET` `--to and exactly one of --theirs, --ours, and --base must be used together` [queue, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_checkout.go`
- `GET` `Could not checkout` [queue, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_checkout.go`
- `GET` `Cannot checkout LFS objects, Git LFS is not installed.` [queue, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_checkout.go`
- `GET` `Scanner error: %s` [queue, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_checkout.go`
- `GET` `Could not convert %q to absolute path: %v` [queue, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_checkout.go`
- `GET` `Could not create path %q: %v` [queue, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_checkout.go`
- `GET` `Could not checkout (are you not in the middle of a merge?): %v` [queue, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_checkout.go`
- `GET` `Could not create object scanner: %v` [queue, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_checkout.go`
- `GET` `Could not find object %q` [queue, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_checkout.go`
- `GET` `Could not find decoder pointer for object %q: %v` [queue, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_checkout.go`
- `GET` `Error checking out %v to %q: %v` [queue, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_checkout.go`
- `GET` `at most one of --base, --theirs, and --ours is allowed` [queue, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_checkout.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `libs/cyberpunk_stack/git-lfs/commands/command_checkout.go`

---
_Back to [overview.md](./overview.md)_