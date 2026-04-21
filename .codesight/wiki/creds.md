# Creds

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Creds subsystem handles **17 routes** and touches: auth, cache.

## Routes

- `GET` `Git credentials for %s not found` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/creds/creds.go`
- `GET` `credential value for %s contains newline: %q` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/creds/creds.go`
- `GET` `credential value for %s contains carriage return: %q\nIf this is intended, set `credential.protectProtocol=false`` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/creds/creds.go`
- `GET` `credential value for %s contains null byte: %q` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/creds/creds.go`
- `GET` `GIT_ASKPASS` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/creds/creds.go`
- `GET` `core.askpass` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/creds/creds.go`
- `GET` `SSH_ASKPASS` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/creds/creds.go`
- `GET` `credential` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/creds/creds.go`
- `GET` `Invalid Credential type queried from AskPass` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/creds/creds.go`
- `GET` `failed to find `git credential %s`: %v` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/creds/creds.go`
- `GET` `invalid input to `git credential %s`: %v` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/creds/creds.go`
- `GET` `change the GIT_TERMINAL_PROMPT env var to be prompted to enter your credentials for %s://%s` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/creds/creds.go`
- `GET` ``git credential %s` error: %s` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/creds/creds.go`
- `GET` `credential fill errors:` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/creds/creds.go`
- `GET` `no valid credential helpers to reject` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/creds/creds.go`
- `GET` `no valid credential helpers to approve` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/creds/creds.go`
- `GET` `No credential helper configured` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/creds/creds.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `libs/cyberpunk_stack/git-lfs/creds/creds.go`

---
_Back to [overview.md](./overview.md)_