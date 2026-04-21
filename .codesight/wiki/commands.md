# Commands

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Commands subsystem handles **21 routes** and touches: cache, queue.

## Routes

- `GET` `Unable to create lock system: %v` [cache, queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/commands.go`
- `GET` `Add the following to '%s/%s':` [cache, queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/commands.go`
- `GET` `Not in a Git repository` [cache, queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/commands.go`
- `GET` `Errors logged to '%s'.\nUse `git lfs logs last` to view the log.` [cache, queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/commands.go`
- `GET` `Error clearing old temporary files: %s` [cache, queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/commands.go`
- `GET` `Cannot read from STDIN: %s (%s)` [cache, queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/commands.go`
- `GET` `Cannot read from STDIN: %s` [cache, queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/commands.go`
- `GET` `Not in a Git repository.` [cache, queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/commands.go`
- `GET` `Could not determine bareness` [cache, queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/commands.go`
- `GET` `Unknown repository format version: %s` [cache, queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/commands.go`
- `GET` `Could not determine current working directory` [cache, queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/commands.go`
- `GET` `Could not canonicalize current working directory` [cache, queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/commands.go`
- `GET` `Unable to log panic to '%s': %s` [cache, queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/commands.go`
- `GET` `Unable to log panic to '%s'` [cache, queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/commands.go`
- `GET` `Error getting network interface: %s` [cache, queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/commands.go`
- `GET` `Error getting IP address: %s` [cache, queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/commands.go`
- `GET` `Current time in UTC:` [cache, queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/commands.go`
- `GET` `Environment:` [cache, queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/commands.go`
- `GET` `Client IP addresses:` [cache, queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/commands.go`
- `GET` `lfs.pathfiltercachesize` [cache, queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/commands.go`
- `GET` `Git version %s or higher is required for Git LFS; your version: %s` [cache, queue, upload]
  `libs/cyberpunk_stack/git-lfs/commands/commands.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `libs/cyberpunk_stack/git-lfs/commands/commands.go`

---
_Back to [overview.md](./overview.md)_
