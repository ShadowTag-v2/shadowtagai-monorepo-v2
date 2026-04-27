# AGENTS.md

## Scope
This is the root behavior contract for the merged pack.
Use it as the first file a coding agent reads.

## Control planes
There is exactly one root control plane in this pack:
1. `AGENTS.md` at the repo root for global behavior.
2. `governance/` for portable engineering rules.
3. `operations/` for workspace truth, MCP truth, and operational scripts.
4. `overlay_shadowtag/` only when you are working on the ShadowTag-specific monorepo posture.

## Rule precedence
1. Safety, secrets hygiene, and verified facts.
2. Workspace truth and canonical paths.
3. Repo-local linting, tests, CI, schemas, and policy code.
4. Portable governance rules.
5. Optional ShadowTag overlay rules.

## Default mode
- Start with `governance/AGENTS.md`.
- Apply `operations/AGENTS.md` if the task touches workspace structure, MCP config, product/lab splits, or operational scripts.
- Apply `overlay_shadowtag/AGENTS.md` only for ShadowTag-specific work.

## Non-negotiables
- Never create a second source of truth for MCP or workspace state.
- Never commit real secrets.
- Prefer automation over prose.
- Prefer small, reviewable changes.
- State assumptions when facts are unknown.

## Canonical install order
Read `INSTALL_ORDER.md` before making changes.
