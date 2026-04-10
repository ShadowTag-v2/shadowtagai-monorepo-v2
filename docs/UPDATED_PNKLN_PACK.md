# UPDATED_pnkln_PACK.md

## Canonical surviving files

### Control plane
- `monorepo_manifest.yaml`
- `docs/MERGE_STATUS.md`
- `antigravity-mcp-config.json`

### Demoted adapters
- `/Users/pikeymickey/.gemini/antigravity/mcp_config.json`
- `.vscode/cline_mcp_settings.json`

### Product env templates
- `apps/counselconduit/.env.example`
- `labs/uphillsnowball/.env.example`

### Runtime support
- `database_tools.yaml`
- `scripts/verify_mcp.sh`
- `scripts/pnkln_lancedb.py`
- `scripts/pnkln_root_guard.sh`
- `scripts/green_loop.py`
- `scripts/drive_ingest_daemon.py`
- `scripts/retriever_eval.py`
- `scripts/ocr_summary_ingest.py`

### Product and lab support
- `configs/feature_flags.yaml`
- `apps/counselconduit/spec/MVP.md`
- `apps/counselconduit/spec/PRICING.md`
- `apps/counselconduit/spec/VALUATION.md`
- `ops/nginx/csp_collector.conf`
- `ops/audits/third_party_inventory.md`

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
- repeated doctrine-only drafts that were not backed by operational files

## Strategic recovery

### Highest-value missed opportunity 1
You already have enough recovered material to make `counselconduit` commercially coherent and `uphillsnowball` technically useful, but the repo still lacked a single truthful backbone. Fixing truth surfaces first unlocks everything else.

### Highest-value missed opportunity 2
Operationalize recovered code instead of redrafting it again:
- green loop
- CSP collector
- retriever eval
- feature flags
- pricing model
- OCR summaries
- Drive-ingest daemon

### Highest-value missed opportunity 3
The recovered CounselConduit blueprint is already stronger than later wandering branches. It should become the business-facing spec while `pnkln/uphillsnowball` remains the internal engine.

## Current truth

- four repos are canonical once the manifest patch lands
- one MCP config is canonical
- all secrets belong in `.env`
- `counselconduit` is the Google-native MVP product path
- `uphillsnowball` is the local Apple Silicon lab path
