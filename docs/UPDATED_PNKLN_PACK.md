# UPDATED_PNKLN_PACK.md

## Canonical surviving files

### Control plane
- `monorepo_manifest.yaml`
- `docs/MERGE_STATUS.md`
- `antigravity-mcp-config.json`

### Demoted adapters
- `/Users/pikeymickey/.gemini/antigravity/mcp_config.json`
- `.vscode/cline_mcp_settings.json`

### Product env templates
- `apps/kovelai/.env.example`
- `labs/uphillsnowball/.env.example`

### Runtime support
- `database_tools.yaml`
- `scripts/verify_mcp.sh`
- `scripts/pnkln_lancedb.py`
- `scripts/pnkln_root_guard.sh`

### Operator guidance
- `AGENTS.md`
- `docs/Cor.Constitution.v3.md`
- `.cursor/rules/cor-vibe-coding.mdc`

## What this pack supersedes

This pack supersedes:
- historical duplicate MCP config surfaces as sources of truth
- unresolved four-repo merge claims
- older partial pnkln pack drafts
- stale cross-thread MCP snippets
- non-canonical repo-root interpretations
- `ShadowTag-v2_stack` path references (real path is `aiyou_stack`)
- `counselconduit` branding (renamed to `kovelai`)

## Current truth

- four repos are canonical in `monorepo_manifest.yaml`
- one MCP config is canonical (7 servers, latest-only pack)
- all secrets belong in `.env`
- `kovelai` (formerly counselconduit) is the Google-native billing gateway
- `uphillsnowball` is the local Apple Silicon lab path
