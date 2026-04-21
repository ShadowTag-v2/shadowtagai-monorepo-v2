# Config

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Config subsystem handles **24 routes** and touches: auth, db, queue, ai, cache, payment.

## Routes

- `GET` `/api/config` → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`
- `GET` `/config` → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`
- `PUT` `/api/config` → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`
- `GET` `default` [auth, db, cache, queue, payment]
  `external_repos/semaphore/util/config.go`
- `GET` `rule` [auth, db, cache, queue, payment]
  `external_repos/semaphore/util/config.go`
- `GET` `env` [auth, db, cache, queue, payment]
  `external_repos/semaphore/util/config.go`
- `GET` `Error reading `git config`: %s` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/config/config.go`
- `GET` `core.sharedrepository` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/config/config.go`
- `GET` `key %q has uppercase, shouldn't` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/config/config.go`
- `GET` `lfs.fetchinclude` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/config/config.go`
- `GET` `lfs.fetchexclude` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/config/config.go`
- `GET` `remote.lfsdefault` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/config/config.go`
- `GET` `remote.lfspushdefault` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/config/config.go`
- `GET` `remote.pushDefault` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/config/config.go`
- `GET` `core.hooksPath` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/config/config.go`
- `GET` `Error: %s` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/config/config.go`
- `GET` `lfs.storage` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/config/config.go`
- `GET` `GIT_` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/config/config.go`
- `GET` `user.name` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/config/config.go`
- `GET` `user.email` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/config/config.go`
- `GET` `EMAIL` [auth, cache]
  `libs/cyberpunk_stack/git-lfs/config/config.go`
- `GET` `configuration is read-only`
  `libs/cyberpunk_stack/git-lfs/git/config.go`
- `GET` `lfs.pruneremotetocheck`
  `libs/cyberpunk_stack/git-lfs/lfs/config.go`
- `GET` `config`
  `libs/cyberpunk_stack/lfs-test-server/config.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/super-dev/super_dev/web/api.py`
- `external_repos/semaphore/util/config.go`
- `libs/cyberpunk_stack/git-lfs/config/config.go`
- `libs/cyberpunk_stack/git-lfs/git/config.go`
- `libs/cyberpunk_stack/git-lfs/lfs/config.go`
- `libs/cyberpunk_stack/lfs-test-server/config.go`

---
_Back to [overview.md](./overview.md)_