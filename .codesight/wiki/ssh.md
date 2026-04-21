# Ssh

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Ssh subsystem handles **30 routes** and touches: auth.

## Routes

- `GET` `lock response: invalid locked-at: %s`
  `libs/cyberpunk_stack/git-lfs/locking/ssh.go`
- `GET` `incomplete fields for lock`
  `libs/cyberpunk_stack/git-lfs/locking/ssh.go`
- `GET` `lock response: multiple next-cursor responses`
  `libs/cyberpunk_stack/git-lfs/locking/ssh.go`
- `GET` `lock response: invalid response: %q`
  `libs/cyberpunk_stack/git-lfs/locking/ssh.go`
- `GET` `lock response: incomplete lock data`
  `libs/cyberpunk_stack/git-lfs/locking/ssh.go`
- `GET` `lock response: interspersed response: %q`
  `libs/cyberpunk_stack/git-lfs/locking/ssh.go`
- `GET` `GIT_SSH_VARIANT` [auth]
  `libs/cyberpunk_stack/git-lfs/ssh/ssh.go`
- `GET` `ssh.variant` [auth]
  `libs/cyberpunk_stack/git-lfs/ssh/ssh.go`
- `GET` `XDG_RUNTIME_DIR` [auth]
  `libs/cyberpunk_stack/git-lfs/ssh/ssh.go`
- `GET` `GIT_SSH` [auth]
  `libs/cyberpunk_stack/git-lfs/ssh/ssh.go`
- `GET` `GIT_SSH_COMMAND` [auth]
  `libs/cyberpunk_stack/git-lfs/ssh/ssh.go`
- `GET` `core.sshcommand` [auth]
  `libs/cyberpunk_stack/git-lfs/ssh/ssh.go`
- `GET` `could not get connection for batch request` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/tq/ssh.go`
- `GET` `no message provided` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/tq/ssh.go`
- `GET` `batch response: status %d from server (%s)` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/tq/ssh.go`
- `GET` `batch response: unsupported hash algorithm: %q` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/tq/ssh.go`
- `GET` `batch response: malformed response: %q` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/tq/ssh.go`
- `GET` `batch response: invalid size: %s` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/tq/ssh.go`
- `GET` `batch response: invalid expires-in: %s` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/tq/ssh.go`
- `GET` `batch response: invalid expires-at: %s` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/tq/ssh.go`
- `GET` `No download action for object: %s` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/tq/ssh.go`
- `GET` `got status %d when fetching OID %s: %s` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/tq/ssh.go`
- `GET` `unexpected size argument` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/tq/ssh.go`
- `GET` `expected valid size, got %q` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/tq/ssh.go`
- `GET` `no size argument seen` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/tq/ssh.go`
- `GET` `got status %d when verifying upload OID %s: %s` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/tq/ssh.go`
- `GET` `got status %d when verifying upload OID %s` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/tq/ssh.go`
- `GET` `SSH upload` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/tq/ssh.go`
- `GET` `got status %d when uploading OID %s` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/tq/ssh.go`
- `GET` `got status %d when uploading OID %s: %s` [auth, upload]
  `libs/cyberpunk_stack/git-lfs/tq/ssh.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `libs/cyberpunk_stack/git-lfs/locking/ssh.go`
- `libs/cyberpunk_stack/git-lfs/ssh/ssh.go`
- `libs/cyberpunk_stack/git-lfs/tq/ssh.go`

---
_Back to [overview.md](./overview.md)_
