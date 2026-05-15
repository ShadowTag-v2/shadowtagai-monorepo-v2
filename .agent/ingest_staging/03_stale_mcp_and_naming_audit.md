# 03_stale_mcp_and_naming_audit.md

## MCP drift

### Canonical intent
The repo handoff says:
- use the canonical MCP config
- do not create a second control plane
- do not revive superseded artifacts

### Confirmed competing MCP surfaces

#### A. `.vscode/mcp.json` creation path in `antigravity_block_3.sh`
This script creates a VS Code MCP config with:
- `quibbler`
- `deep-research`

That is a direct competing MCP surface unless explicitly marked adapter-only.

#### B. Apigee MCP bridge scripts
`deploy_apigee_mcp.sh` appears in multiple backup/recovery locations and still includes:
- older project id `shadowtag-omega-v2`
- generated MCP client config instructions
- separate MCP server path assumptions

This is not harmless if future agents search broadly and mistake it for active control-plane guidance.

## Naming drift

### Confirmed mixed naming in repo content
Observed active/reachable terms include:
- `ShadowTagAI-Omega`
- `ShadowTagAI v2`
- `shadowtag-omega-v4`
- `UphillSnowball`
- `pnkln`
- `counselconduit`
- `antigravity`

Examples:
- `GEMINI.md` still anchors to `ShadowTagAI-Omega` and the old root path.
- `autoresearch.py` registers “ShadowTagAI v2 tools” and “UphillSnowball tools” in the same runtime.

## Why this matters

This is not cosmetic. Mixed naming causes:
- wrong root assumptions
- wrong product/lab boundaries
- wrong tool registration behavior
- wrong search and patch targeting
- future memory drift

## Patch rule

### MCP
Every MCP-related file must be labeled as one of:
- canonical
- adapter-only
- retired
- archived

### Naming
Every major namespace should be assigned one role:
- `counselconduit` = product
- `uphillsnowball` = lab
- `pnkln` = doctrine/control plane
- `antigravity` = agent operating layer

Old names like `ShadowTagAI-Omega` and `ShadowTagAI v2` should be treated as legacy references unless intentionally preserved in archived docs.
