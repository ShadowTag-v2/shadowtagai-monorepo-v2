# Cor.Constitution.v3

## Core posture

Operate with disciplined, high-signal execution.
Prefer one source of truth per layer.
Prefer canonical roots over copied ambiguity.
Prefer automation over prose where possible.

## Canonical order

1. workspace truth
2. merge truth
3. MCP truth
4. runtime truth
5. product hardening

## Security

- all API tokens live in `.env`
- no secret material in committed JSON
- local adapters may exist, but must not become truth surfaces

## Product split

### counselconduit
Google-native MVP path.
Built for production readiness.

### uphillsnowball
Local Apple Silicon research path.
Used to improve internal methods and experimentation.
Not the product control plane.

## Non-negotiables

- `monorepo_manifest.yaml` is canonical workspace truth
- `antigravity-mcp-config.json` is canonical MCP truth
- all four repos remain live canonical roots
- no unresolved repo root may remain in steady state
