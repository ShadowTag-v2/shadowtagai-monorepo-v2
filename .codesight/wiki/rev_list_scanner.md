# Rev_list_scanner

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Rev_list_scanner subsystem handles **4 routes** and touches: auth.

## Routes

- `GET` `unknown RevListOrder %d` [auth]
  `libs/cyberpunk_stack/git-lfs/git/rev_list_scanner.go`
- `GET` `ref %q is ambiguous` [auth]
  `libs/cyberpunk_stack/git-lfs/git/rev_list_scanner.go`
- `GET` `unknown scan type: %d` [auth]
  `libs/cyberpunk_stack/git-lfs/git/rev_list_scanner.go`
- `GET` `missing OID in line (got %q)` [auth]
  `libs/cyberpunk_stack/git-lfs/git/rev_list_scanner.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `libs/cyberpunk_stack/git-lfs/git/rev_list_scanner.go`

---
_Back to [overview.md](./overview.md)_