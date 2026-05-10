# ANTIGRAVITY_CONTROL_PLANE.md

## Purpose

This document defines the control plane for the pnkln workspace.

## Operator entrypoint

Open the workspace through:

`pnkln.code-workspace`

That is the intended top-level entry for daily work.

## Sources of truth

### Workspace truth

- `monorepo_manifest.yaml`

### MCP truth

- `antigravity-mcp-config.json`

### Agent behavior truth

- `AGENTS.md`

### Surviving pack truth

- `docs/UPDATED_pnkln_PACK.md`

## Multi-root layout

The workspace is organized as one control plane with multiple live roots:

- monorepo root
- `apps/counselconduit`
- `labs/uphillsnowball`
- `apps/pnkln-stack_stack/pnkln-stack-fastapi-services`
- `apps/pnkln-stack_stack/Pipeline`
- `apps/pnkln-stack_stack/nascent-apollo`

## Product split

### counselconduit

Google-native MVP path.

- project: `shadowtag-omega-v4`
- model: `gemini-3.1-flash-lite-preview`

### uphillsnowball

Apple Silicon local R&D path.

- used for experimentation and method improvement
- not the product control plane

## Agent split

### Gemini Code Assist

- trusted workspace
- YOLO mode allowed inside canonical workspace root only

### Cline

- auto-approve allowed for routine in-workspace actions
- broader risky work should happen on disposable branches

### Pickle Rick

- skills layer only
- not a second control plane
- must conform to `AGENTS.md`, `monorepo_manifest.yaml`, and `antigravity-mcp-config.json`

## MCP model

There must be exactly one canonical MCP config:

- `antigravity-mcp-config.json`

Other MCP-related files are adapters or retired surfaces only.

## Secret handling

- all API tokens belong in `.env`
- no live secrets in committed workspace JSON
- `.env.example` files define shape, not values

## Merge truth

The four live canonical roots remain:

- `apps/pnkln-stack_stack/pnkln-stack-fastapi-services`
- `apps/pnkln-stack_stack/cosmic-crab-payload`
- `apps/pnkln-stack_stack/Pipeline`
- `apps/pnkln-stack_stack/nascent-apollo`

## Operating rule

Fix in this order:

1. workspace truth
2. merge truth
3. MCP truth
4. runtime truth
5. product hardening

## Non-goals

- no second source of truth
- no inline secrets
- no revival of superseded thread artifacts
