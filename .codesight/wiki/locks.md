# Locks

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Locks subsystem handles **22 routes** and touches: auth, db, cache.

## Routes

- `ALL` `/{user}/{repo}/locks` params(user, repo) [auth, db, upload]
  `libs/cyberpunk_stack/lfs-test-server/server.go`
- `ALL` `/{user}/{repo}/locks/{id}/unlock` params(user, repo, id) [auth, db, upload]
  `libs/cyberpunk_stack/lfs-test-server/server.go`
- `GET` `no matching locks found` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/locking/locks.go`
- `GET` `multiple locks found; ambiguous` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/locking/locks.go`
- `GET` `lock cache initialization` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/locking/locks.go`
- `GET` `locking API` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/locking/locks.go`
- `GET` `server unable to create lock: %s` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/locking/locks.go`
- `GET` `lock cache` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/locking/locks.go`
- `GET` `make lock path absolute` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/locking/locks.go`
- `GET` `set file write flag` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/locking/locks.go`
- `GET` `unable to get lock ID: %v` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/locking/locks.go`
- `GET` `server unable to unlock: %s` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/locking/locks.go`
- `GET` `error caching unlock information: %v` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/locking/locks.go`
- `GET` `can't search cached locks when filter or limit is set` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/locking/locks.go`
- `GET` `can't search cached locks when limit is set` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/locking/locks.go`
- `GET` `server error searching locks: %s` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/locking/locks.go`
- `GET` `locking` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/locking/locks.go`
- `GET` `server error searching for locks: %s` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/locking/locks.go`
- `GET` `inititalization of cache directory %s failed: already exists, but is no directory` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/locking/locks.go`
- `GET` `initiailization of cache directory %s failed: directory creation failed` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/locking/locks.go`
- `GET` `initialization of cache directory %s failed` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/locking/locks.go`
- `GET` `no cached locks present` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/locking/locks.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `libs/cyberpunk_stack/lfs-test-server/server.go`
- `libs/cyberpunk_stack/git-lfs/locking/locks.go`

---
_Back to [overview.md](./overview.md)_
