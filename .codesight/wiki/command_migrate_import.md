# Command_migrate_import

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Command_migrate_import subsystem handles **17 routes** and touches: auth, cache, payment.

## Routes

- `GET` `--no-rewrite and --fixup cannot be combined` [auth, cache, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_migrate_import.go`
- `GET` `Expected one or more files with --no-rewrite` [auth, cache, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_migrate_import.go`
- `GET` `Unable to find current reference` [auth, cache, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_migrate_import.go`
- `GET` `Unable to load commit` [auth, cache, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_migrate_import.go`
- `GET` `No Git LFS filters found in '.gitattributes'` [auth, cache, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_migrate_import.go`
- `GET` `File %s did not match any Git LFS filters in '.gitattributes'` [auth, cache, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_migrate_import.go`
- `GET` `Could not rewrite %q` [auth, cache, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_migrate_import.go`
- `GET` `Unable to write commit` [auth, cache, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_migrate_import.go`
- `GET` `Unable to update ref` [auth, cache, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_migrate_import.go`
- `GET` `Cannot use --fixup with --include, --exclude` [auth, cache, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_migrate_import.go`
- `GET` `Cannot parse --above=<n>` params(n) [auth, cache, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_migrate_import.go`
- `GET` `Cannot use --above with --include, --exclude, --fixup` [auth, cache, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_migrate_import.go`
- `GET` `%s: convert to Git LFS` [auth, cache, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_migrate_import.go`
- `GET` `expected '.gitattributes' to be a file, got a symbolic link` [auth, cache, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_migrate_import.go`
- `GET` `unable to find entry %s in tree` [auth, cache, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_migrate_import.go`
- `GET` `expected %s to be a tree, got %s` [auth, cache, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_migrate_import.go`
- `GET` `error parsing path %s` [auth, cache, payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_migrate_import.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `libs/cyberpunk_stack/git-lfs/commands/command_migrate_import.go`

---
_Back to [overview.md](./overview.md)_
