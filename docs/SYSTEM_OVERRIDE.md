# SYSTEM_OVERRIDE.md — V19 Archon-Bun Hyper-Core

**Version:** 19.0  
**Runtime:** Bun 1.3.11 (Zig-backed)  
**Codename:** Cognitive Router + FinOps Governor  
**Date:** 2026-05-09  
**HEAD:** `aec15aeb9` (merged via PR #88)

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

### V19 New Artifacts (Cognitive Router + FinOps Governor)

| Artifact | Path | Purpose | Status |
|----------|------|---------|--------|
| Cognitive Router | `tools/cognitive_router/dispatch.ts` | Multi-model dispatch (Gemini tiers + fallback) | ✅ DEPLOYED |
| FinOps Governor | `services/finops-governor/` | Cost guardrails, BigQuery billing analytics | ✅ DEPLOYED |
| `@google/genai` | `node_modules/` | Gemini 3.x generative AI SDK | ✅ INSTALLED |
| `@google-cloud/bigquery` | `node_modules/` | BigQuery client for FinOps analytics | ✅ INSTALLED |

### Kriasoft Isomorphic Triad (V18)

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

### Live Deployments

| Site | URL | Platform | Status |
|------|-----|----------|--------|
| HeadFade | `https://headfade.com` | Firebase Hosting | ✅ LIVE |
| CounselConduit | `https://counselconduit-767252945109.us-central1.run.app` | Cloud Run | ✅ LIVE |
| ShadowTagAI | Firebase Hosting target `shadowtagai` | Firebase Hosting | Configured |
| KovelAI | Firebase Hosting target `kovelai` | Firebase Hosting | Configured |
| CC Dashboard | Firebase Hosting target `counselconduit-dashboard` | Firebase Hosting | Configured |

### Monorepo Census

| Category | Count |
|----------|-------|
| Packages | 91 |
| Workspace Skills | 92 |
| External Repos | 21 |
| Firebase Hosting Targets | 4 |
| GitHub PRs Merged (V16→V19) | 4 |

---

## Ground Truth Axiom

> Local filesystem source code is **absolute ground truth**. The public NPM registry is a distribution mechanism for the masses; it is not the arbiter of reality. When bleeding-edge source code exists on this hard drive, that source code IS the package.

---

## Version History

| Version | Codename | HEAD Commit | PR | Date |
|---------|----------|-------------|-----|------|
| V19 | Cognitive Router + FinOps Governor | `aec15aeb9` | #88 (merged) | 2026-05-09 |
| V18 | Isomorphic GraphQL Ascension | `f35fb96ae` | — | 2026-05-08 |
| V17 | Archon-Bun Hyper-Core | `5ef4218b3` | — | 2026-05-08 |
| V16 | Absolute OS | `8b78eaaa4` | — | 2026-05-08 |
| V15 | Ground Truth Revision | `351ca4856` | — | 2026-05-07 |
