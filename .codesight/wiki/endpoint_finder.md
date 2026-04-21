# Endpoint_finder

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Endpoint_finder subsystem handles **5 routes** and touches: auth, cache.

## Routes

- `GET` `lfs.gitprotocol` [auth, cache, upload]
  `libs/cyberpunk_stack/git-lfs/lfsapi/endpoint_finder.go`
- `GET` `lfs.pushurl` [auth, cache, upload]
  `libs/cyberpunk_stack/git-lfs/lfsapi/endpoint_finder.go`
- `GET` `lfs.url` [auth, cache, upload]
  `libs/cyberpunk_stack/git-lfs/lfsapi/endpoint_finder.go`
- `GET` `remote.` [auth, cache, upload]
  `libs/cyberpunk_stack/git-lfs/lfsapi/endpoint_finder.go`
- `GET` `warning: Multiple 'url.*.%s' keys with the same alias: %q` [auth, cache, upload]
  `libs/cyberpunk_stack/git-lfs/lfsapi/endpoint_finder.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `libs/cyberpunk_stack/git-lfs/lfsapi/endpoint_finder.go`

---
_Back to [overview.md](./overview.md)_