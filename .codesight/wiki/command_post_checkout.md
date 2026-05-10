# Command_post_checkout

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Command_post_checkout subsystem handles **4 routes** and touches: payment.

## Routes

- `GET` `This should be run through Git's post-checkout hook.  Run `git lfs update` to install it.` [payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_post_checkout.go`
- `GET` `Warning: post-checkout rev diff %v:%v failed: %v` [payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_post_checkout.go`
- `GET` `Falling back on full scan.` [payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_post_checkout.go`
- `GET` `Warning: post-checkout locked file check failed: %v` [payment]
  `libs/cyberpunk_stack/git-lfs/commands/command_post_checkout.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `libs/cyberpunk_stack/git-lfs/commands/command_post_checkout.go`

---
_Back to [overview.md](./overview.md)_
