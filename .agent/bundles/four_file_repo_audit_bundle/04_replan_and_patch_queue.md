# 04_replan_and_patch_queue.md

## Replan

The thread should now move in this order:

1. Fix live stale models
2. Neutralize competing MCP surfaces
3. Fix stale project/root references
4. Normalize naming in live control-plane docs and runtime code
5. Tighten workspace/search exclusions so backups stop polluting future reasoning
6. Only then regenerate the polished pack/report again

## Patch queue

### PR-1: live stale-model cleanup
**Goal**
Replace stale model identifiers in live code/docs with the approved `gemini-3.1-family`.

**Known targets from repo pass**
- `apps/nascent-apollo/src/antigravity/flying_monkeys.py`
- live `GEMINI.md` if still in authoritative search path
- generator/bootstrap scripts like `antigravity_block_3.sh` if still used

### PR-2: stale MCP neutralization
**Goal**
Mark every non-canonical MCP surface as adapter-only or retired.

**Known targets**
- `.vscode/mcp.json` creation path in `antigravity_block_3.sh`
- Apigee MCP bridge scripts in backup/recovery trees

### PR-3: stale project/root cleanup
**Goal**
Remove or quarantine live references to:
- `shadowtag-omega-v2`
- `/Users/pikeymickey/pnkln-stack/ShadowTag-v2/ShadowTag-Omega`

**Known targets**
- `deploy_apigee_mcp.sh` backups show `shadowtag-omega-v2` still present
- `GEMINI.md` shows old repo/root path

### PR-4: naming rationalization
**Goal**
Make live docs and code obey the product/lab/control-plane split.

**Known targets**
- mixed namespace runtime registration in `flying_monkeys.py`

### PR-5: quarantine hardening
**Goal**
Ensure `_PRE_OMEGA_BACKUP_*`, recovered architecture trees, and old doctrine trees cannot masquerade as live truth during future agent passes.

## Final canonical statement after these PRs

- one monorepo
- one MCP truth
- one approved model family
- one project id
- one role map for naming
- backups searchable only when explicitly requested
