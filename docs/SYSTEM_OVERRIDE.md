# SYSTEM_OVERRIDE.md — V18 Zenith Hyper-Core

**Version:** 18.0  
**Runtime:** Bun 1.3.11 (Zig-backed)  
**Codename:** Isomorphic GraphQL Ascension  
**Date:** 2026-05-08  

---

## Architecture

### Local-First MCP Fleet

The NPM Illusion has been shattered. All proprietary Google Labs packages are **compiled locally** from source code in `external_repos/`:

| Package | Source | Compiled Entry Point | Status |
|---------|--------|---------------------|--------|
| `@google/stitch-sdk` v0.3.4 | `external_repos/stitch-sdk/` | `packages/sdk/dist/src/index.js` | ✅ BUILT |
| `@google/jules-mcp` | `external_repos/jules-sdk/` | `packages/mcp/dist/cli.mjs` | ✅ BUILT |
| `@google/jules-sdk` | `external_repos/jules-sdk/` | `packages/core/` | ✅ BUILT |
| `@google/jules-fleet` | `external_repos/jules-sdk/` | `packages/fleet/dist/cli/index.mjs` | ✅ BUILT |

### Kriasoft Isomorphic Triad

| Repo | Package Name | Purpose | Location |
|------|-------------|---------|----------|
| `react-starter-kit` | `@repo/root` | Bun-native React monorepo (apps: api, app, email, web) | `external_repos/react-starter-kit/` |
| `graphql-starter-kit` | `root` | GraphQL API patterns (Yarn/Vitest) | `external_repos/graphql-starter-kit/` |
| `react-firebase-starter` | `app` | Firebase Auth + React + Relay | `external_repos/react-firebase-starter/` |

### API Gateway

`apps/api/server.ts` — Hono v4 on Bun.serve()

| Route | Function |
|-------|----------|
| `/health` | Cloud Run probe |
| `/graphql` | Federated GraphQL (schema-first) |
| `/webhook/stripe` | Raw body + signature verification |
| `/intake/tabular` | SheetJS → Gemini RAG |

### Stitch SDK Reality

The Stitch SDK exports **server-side primitives** — NOT React hooks:
- `Stitch`, `Project`, `Screen`, `DesignSystem`
- `StitchProxy`, `stitch` (singleton)
- `stitchTools`, `stitchAdkTools`

The `useStitchTheme()` hook is provided by the **facade** at `apps/client/src/core/stitch-bridge.tsx`. It bridges M3 design tokens into React context with graceful fallback to Material 3 defaults.

### Enterprise Registry

`.bunfig.toml` routes scoped packages:
- `@google/*` → GCP Artifact Registry (WIF auth)
- `@google-labs-code/*` → GitHub Packages
- `@stitch/*` → GitHub Packages
- `@firebase/*` → GitHub Packages
- `@shadowtag/*` → GCP Artifact Registry

### CI/CD

`.github/workflows/jules-ci.yml` — 3-phase pipeline:
1. **Build**: Bun install + typecheck + build
2. **Security**: Betterleaks + Biome
3. **Deploy**: WIF auth → Cloud Run

### MCP Motherboard

`cline_mcp_settings.json` — 13 servers:
- `jules-mcp-server`: LOCAL binary (`external_repos/jules-sdk/packages/mcp/dist/cli.mjs`)
- `stitch-mcp-server`: LOCAL binary (`external_repos/stitch-sdk/packages/sdk/dist/src/index.js`)
- `jules-fleet`: LOCAL binary (`external_repos/jules-sdk/packages/fleet/dist/cli/index.mjs`)
- `firebase-mcp-server`: npx firebase-tools
- `chrome-devtools-mcp`, `sequential-thinking`, `google-developer-knowledge`: Anthropic MCP packages
- `stripe-mcp`: @stripe/mcp
- Plus: gcloud-mcp, observability, cloud-run, storage, os-dart-compiler

---

## Ground Truth Axiom

> Local filesystem source code is **absolute ground truth**. The public NPM registry is a distribution mechanism for the masses; it is not the arbiter of reality. When bleeding-edge source code exists on this hard drive, that source code IS the package.
