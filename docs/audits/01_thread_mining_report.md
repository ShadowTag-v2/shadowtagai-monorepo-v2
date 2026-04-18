# 01_thread_mining_report.md

## Executive finding

The thread did not primarily fail from lack of ideas. It failed from control-plane drift:
- multiple MCP surfaces
- multiple workspace truths
- multiple naming regimes
- stale model strings surviving in code and docs
- backup and recovered trees still leaking into reasoning

The strongest surviving authority order in-repo is explicit:
1. `AGENTS.md`
2. `monorepo_manifest.yaml`
3. `antigravity-mcp-config.json`
4. beads / recovery memory

This is stated directly in `antigravity_handoff.txt`.

## What the repo itself confirms

### Canonical control-plane intent exists
`antigravity_handoff.txt` says the monorepo is the only canonical workspace, MCP config must be canonical, and superseded artifacts must not be revived. It also defines a Stage 3 verification checklist covering active files, workspace, MCP, runtime, and drift.

### Stale doctrine still exists in live-accessible repo content
A surviving `GEMINI.md` still points at:
- repository `ShadowTag-Omega`
- root `/Users/pikeymickey/aiyou-stack/ShadowTag-v2/ShadowTag-Omega`
- recursive agent model `gemini-2.5-pro`
- deep research model `gemini-3-pro-interactions-exp`

That is direct evidence of stale repo/root/model drift.

### Live code also contains stale model drift
`apps/nascent-apollo/src/antigravity/flying_monkeys.py` still says:
- “Migrated from v8 FULL to pure Gemini 1.5 Pro”
- `MODEL_NAME = "gemini-1.5-pro-001"`
- constructor default `model: str = "gemini-1.5-pro-001"`

So stale model drift is not only in docs; it is in code.

## Reams left on the table

1. **True repo-level stale-model sweep**
   The thread kept asserting the right model target, but the repo still contains old model families and intermediate experiments.

2. **True stale-MCP sweep**
   The thread wanted one MCP truth, but repo artifacts still include alternate MCP ideas like `.vscode/mcp.json`, legacy Apigee MCP bridges, and older server patterns.

3. **True stale-root / stale-project sweep**
   There are still references to old roots and old project ids like `shadowtag-omega-v2` in deployment code.

4. **True naming rationalization**
   The repo still mixes `ShadowTag`, `ShadowTag-Omega`, `aiyou`, `UphillSnowball`, `pnkln`, and product/lab/control-plane language in ways that increase ambiguity.

5. **Backups and recovered trees still pollute search space**
   Multiple `_PRE_OMEGA_BACKUP_*` trees are showing up in search results, and recovered docs are still close enough to live paths to confuse future passes.

## Bottom line

The thread’s next correct move is not more doctrine drafting.
It is:
- repo-wide stale-model audit
- repo-wide stale-MCP audit
- repo-wide stale-root/project audit
- repo-wide stale-naming audit
- then patch queue, smallest-first
