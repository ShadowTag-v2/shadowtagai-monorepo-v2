# Release checklist — v8.3

## 0. Memory gate first
Before calling anything final:
- acknowledge invariants without reprinting the full list
- state `LOCKED` or `DRIFTED` (if drifted, stop and re-lock)
- verify `DEVELOPER_KNOWLEDGE_API_KEY` and project lock: `shadowtag-omega-v4`

## 1. Truth surfaces
Confirm alignment of: `AGENTS.md`, `CLAUDE.md`, `monorepo_manifest.yaml`, `antigravity-mcp-config.json`, `operator_invariants.json`, `BUSINESS_CONTEXT_LOCKED.md`.

## 2. MCP-first barriers
Before any code that depends on live systems:
- query live DB schema via database MCP
- fetch live/current SDK surface via Documentation MCP
- ensure the implementation plan explicitly declared those MCP calls

## 3. GitHub control plane
- Use GitHub App (`3018200` via PEM) for repo truth and PR operations.
- Use `gh auth login && gh auth setup-git` only if local auth repair is needed.

## 4. Code and config gates
- run `scripts/dead-code-audit.sh`
- no `.env*` files staged
- no production secrets in source
- no production source maps enabled
- lockfile updated when dependency manifests changed
- typecheck, lint, and relevant validation succeed
