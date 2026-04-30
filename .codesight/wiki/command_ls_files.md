# Command_ls_files

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Command_ls_files subsystem handles **7 routes** and touches: payment.

## Routes

- `GET` `Cannot use --all with explicit reference` [payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_ls_files.go`
- `GET` `Did you mean `git lfs ls-files --all --` ?` [payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_ls_files.go`
- `GET` `Cannot use --deleted with reference range` [payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_ls_files.go`
- `GET` `Could not read empty Git tree object` [payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_ls_files.go`
- `GET` `filepath: %s\n    size: %d\ncheckout: %v\ndownload: %v\n     oid: %s %s\n version: %s\n` [payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_ls_files.go`
- `GET` `Could not scan for Git LFS index: %s` [payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_ls_files.go`
- `GET` `Could not scan for Git LFS history: %s` [payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_ls_files.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `libs/cyberpunk_stack/git-lfs/commands/command_ls_files.go`

---
_Back to [overview.md](./overview.md)_
