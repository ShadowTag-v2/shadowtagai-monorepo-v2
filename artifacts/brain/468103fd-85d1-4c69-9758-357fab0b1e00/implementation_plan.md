# Implementation Plan - Monorepo Hardening

**Goal**: Enforce strict Monorepo structure for `ShadowTag-v2` as defined by the "Judge 6" protocol.

## User Review Required
> [!IMPORTANT]
> This operations involves **destructive deletion** of nested `.git` directories (`find . -mindepth 2 -name ".git" -type d -exec rm -rf {} +`). This was explicitly requested by the user.

## Proposed Changes

### Root Configuration
#### [NEW] [ShadowTag.code-workspace](file:///Users/pikeymickey/aiyou-stack/ShadowTag-v2/ShadowTag.code-workspace)
- Defines the workspace root.
- Locks `geminicodeassist` settings.
- Enforces terminal CWD and file watchers.

### Directory Structure
- Create directories:
    - `.agent/{rules,workflows,hooks}`
    - `.beads`
    - `src/{governance,jetski,architecture}`
    - `libs/steel`
    - `infrastructure/terraform`
    - `apps/playground`

### Git Configuration
#### [MODIFY] [.gitignore](file:///Users/pikeymickey/aiyou-stack/ShadowTag-v2/.gitignore)
- Add exclusions for `.beads/`, `browser_artifacts/`, `external_sdks/`, `*.tfstate`, `.env`.

### Playground
#### [NEW] [apps/playground/README.md](file:///Users/pikeymickey/aiyou-stack/ShadowTag-v2/apps/playground/README.md)
#### [NEW] [apps/playground/scratchpad.py](file:///Users/pikeymickey/aiyou-stack/ShadowTag-v2/apps/playground/scratchpad.py)

### Cleanup
- Remove nested `.git` folders.

## Verification Plan
### Automated Tests
- Run `ls -R` to verify directory structure.
- Check `.gitignore` content.
- Verify `ShadowTag.code-workspace` exists.

### Manual Verification
- User to open `ShadowTag.code-workspace` in VS Code to confirm settings.
