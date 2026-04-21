# Git

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Git subsystem handles **57 routes** and touches: auth, cache, payment.

## Routes

- `GET` `failed to find `git hash-object`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `Failed to run `git update-index`` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `error building Git blob OID: %s` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `remote required` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `Git can't resolve ref: %q` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `not on a branch` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `remote not found for branch %q` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to find `git remote`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to call `git remote`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to find `git remote -v`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to call `git remote -v`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to find `git show-ref`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to call `git show-ref`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `invalid remote name: %q` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `invalid remote URL protocol %q in %q` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to find `git for-each-ref`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to call `git for-each-ref`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to find `git show`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to call `git show`: %v %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `Unexpected output from `git show`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to find `git rev-parse --git-dir --show-toplevel`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to call `git rev-parse --git-dir --show-toplevel`: %q` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `bad `git rev-parse` output: %q` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `error converting %q to absolute: %s` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to find `git rev-parse --show-toplevel`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to call `git rev-parse --show-toplevel`: %v %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `no output from `git rev-parse --show-toplevel`` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to find `git rev-parse --git-dir`` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to call `git rev-parse --git-dir`` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to find `git rev-parse --git-common-dir`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to call `git rev-parse --git-common-dir`: %v %v: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to find `git worktree`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to open output pipe to `git worktree`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to open error pipe to `git worktree`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to start `git worktree`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `error in `git worktree`: %v: %s` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to find `git clone`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to start `git clone`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` ``git clone` failed: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to find `git ls-remote`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to call `git ls-remote`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `unexpected tag returned by `git ls-remote --heads`: %s %s` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `cannot open pipe` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `invalid `git for-each-ref` line: %q` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to find `git ls-files`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to call `git ls-files`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to find `git diff-tree`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to call `git diff-tree`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to start `git diff-tree`: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` ``git diff-tree` failed: %v` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `failed to find `git status`` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `Failed to call `git status`` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `Failed to start `git status`` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` ``git status` failed` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `GIT_OBJECT_DIRECTORY` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `extensions.objectformat` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`
- `GET` `unsupported repository hash algorithm %q` [auth, cache, payment, upload]
  `libs/cyberpunk_stack/git-lfs/git/git.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `libs/cyberpunk_stack/git-lfs/git/git.go`

---
_Back to [overview.md](./overview.md)_