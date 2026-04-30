# Client

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Client subsystem handles **5 routes** and touches: auth, cache.

## Routes

- `GET` `missing protocol: %q` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/lfshttp/client.go`
- `GET` `too many redirects` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/lfshttp/client.go`
- `GET` `HTTP/2 cannot be used except with TLS` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/lfshttp/client.go`
- `GET` `Unknown HTTP version %q` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/lfshttp/client.go`
- `GET` `refusing insecure redirect: HTTPS to HTTP` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/lfshttp/client.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `libs/cyberpunk_stack/git-lfs/lfshttp/client.go`

---
_Back to [overview.md](./overview.md)_
