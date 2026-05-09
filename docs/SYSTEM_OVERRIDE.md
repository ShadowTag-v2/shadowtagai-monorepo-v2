# SYSTEM_OVERRIDE.md — V25 Pinnacle (MCP Fleet Ascension + Manifest Gap Closure)

**Version:** 25  
**Runtime:** Bun 1.3.11 (Zig-backed)  
**Codename:** Pinnacle (24-Server MCP Fleet + 221/221 Test Suite + Manifest v23.0)  
**Date:** 2026-05-09  
**HEAD:** `649c25fc6` (V25 Pinnacle — manifest gap closure + Pomelli swarm CI)

---

## V22 Milestone: Phosphor-Shift

The Phosphor-Shift codename reflects two operational upgrades:

1. **Phosphor**: The luminescent elimination of third-party cookie penalties — Firebase SDK modules (Auth, Analytics, App Check) have been refactored from static imports to dynamic `import()`, removing all GAPI iframe and reCAPTCHA cookie side-effects from the initial bundle. Lighthouse Best Practices: 73 → **100**.
2. **Shift**: Complete branch hygiene — all 6 stale `perf/v21-*` local branches and 3 merged remote branches pruned. Branch state: `main` only, zero divergence.

### PR #90 — Dynamic Import Refactoring

| File | Change | Impact |
|------|--------|--------|
| `src/lib/firebase.ts` | Static SDK imports → async `getAuthInstance()`, `getAppCheck()`, `getAnalyticsInstance()` getters via `import()` | Zero Firebase code in initial JS bundle |
| `src/app/page.tsx` | `onAuthStateChanged` loaded dynamically inside auth effect | No GAPI iframe during SSR/hydration |
| `src/components/AuthWallModal.tsx` | `GoogleAuthProvider`, `OAuthProvider`, `signInWithPopup` deferred to click handler | Auth SDK loaded only on user interaction |
| `src/hooks/useVotes.ts` | `logEvent` dynamically imported inside vote handler | Analytics SDK excluded from initial chunk |

### Lighthouse Results (headfade.com — Post-V22)

| Category | Score |
|----------|-------|
| Performance | 100 |
| Accessibility | 100 |
| Best Practices | **100** (was 73) |
| SEO | 100 |
| Agentic Browsing | 100 |

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

### Port-Killer Process Sovereignty

`scripts/port_killer.sh` — Ported from `external_repos/port-killer/platforms/macos/Sources/PortScanner.swift` (Swift 6.0 actor):

| Command | Function |
|---------|----------|
| `./scripts/port_killer.sh scan` | Scan all listening TCP ports (lsof -iTCP -sTCP:LISTEN -P -n +c 0) |
| `./scripts/port_killer.sh --kill PORT` | Graceful kill: SIGTERM → 500ms grace → SIGKILL |
| `./scripts/port_killer.sh --deep PORT` | Deep kill: listener + ESTABLISHED connections |
| `./scripts/port_killer.sh --zombies [HOURS]` | Find zombie processes older than N hours |
| `./scripts/port_killer.sh --exterminate [HOURS]` | Kill zombies older than N hours |

### V19 Artifacts (Cognitive Router + FinOps Governor)

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

`.github/workflows/pomelli-brand-sync.yml` — Automated Pomelli design token sync across 3 brands.

### MCP Motherboard

**Antigravity Platform-Managed (5 servers):**
- `firebase-mcp-server` (45 tools): Auth, Firestore, Hosting, Functions, Storage
- `chrome-devtools-mcp` (29 tools): Browser automation, DOM, Lighthouse, perf traces
- `StitchMCP` (12 tools): Design systems, screen generation, UI variants
- `google-developer-knowledge` (3 tools): Developer docs search, grounded answers
- `sequential-thinking` (1 tool): Multi-step reasoning, hypothesis verification

**Cline Local (19 servers — verified 2026-05-09):**
- `bigquery`: BigQuery analytics, FinOps ROI queries
- `cloud-run`: Service deployment, revisions, traffic splitting
- `dart-language-server`: Dart/Flutter LSP analysis
- `database-insights`: Cloud SQL/Spanner performance advisor
- `firebase-mcp-server`: Firebase CLI operations (Cline-side)
- `gcloud`: GCP CLI operations
- `gemini-memory`: Persistent agent memory store
- `genkit`: Firebase Genkit AI framework
- `google-cloud-spanner`: Spanner DDL, queries, CDC
- `google-drive-api`: Google Drive file access
- `jules-mcp-server`: LOCAL binary — asynchronous cloud agent delegation
- `notebooklm-mcp`: NotebookLM epistemic corpus queries
- `observability`: Cloud Monitoring, Logging
- `playwright`: Browser automation E2E testing
- `pomelli-swarm`: Fleet Lighthouse optimization orchestration
- `semantic-scalpel`: AST-Grep semantic code surgery
- `spanner-toolbox`: Spanner schema, migration, introspection
- `storage`: Cloud Storage operations
- `stripe-governor`: Stripe payments, webhooks, billing

### Live Deployments

| Site | URL | Platform | Status |
|------|-----|----------|--------|
| HeadFade | `https://headfade.com` | Firebase Hosting | ✅ LIVE (LH 100/100/100/100) |
| CounselConduit | `https://counselconduit-767252945109.us-central1.run.app` | Cloud Run | ✅ LIVE (200 OK, 0.33s) |
| ShadowTagAI | Firebase Hosting target `shadowtagai` | Firebase Hosting | Configured |
| KovelAI | Firebase Hosting target `kovelai` | Firebase Hosting | Configured |
| CC Dashboard | Firebase Hosting target `counselconduit-dashboard` | Firebase Hosting | Configured |

### Monorepo Census

| Category | Count |
|----------|-------|
| Packages | 95 |
| Workspace Skills | 92 |
| Global Skills | 298 |
| External Repos | 22 |
| Firebase Hosting Targets | 4 |
| Cline MCP Servers | 19 |
| Antigravity MCP Servers | 5 |
| **Total MCP Servers** | **24** |
| CI Workflows (active) | 70 |
| Merge Commits on `main` | 98 |
| Vitest Suite | **221/221 PASS** |
| Test Files (all runners) | 19 |
| Security Pipeline | 35-check |
| Repo Doctor Grade | C (2 non-critical errors) |
| Lighthouse (headfade.com) | **P100/A100/BP100/SEO100** |
| Lighthouse (shadowtagai.web.app) | P94/A100/BP100/SEO100 |

---

## Ground Truth Axiom

> Local filesystem source code is **absolute ground truth**. The public NPM registry is a distribution mechanism for the masses; it is not the arbiter of reality. When bleeding-edge source code exists on this hard drive, that source code IS the package.

---

## V22 Audit Results

### Branch Hygiene

| Action | Count | Detail |
|--------|-------|--------|
| Local branches deleted | 6 | `perf/v21-appcheck-lazy-init`, `perf/v21-bp100-dynamic-imports`, `perf/v21-complete-lazy-sdk-deferral`, `perf/v21-defer-auth-gapi`, `perf/v21-harden-auth-deferral`, `perf/v21-headfade-lighthouse-ascension` |
| Remote branches deleted | 3 | `feat/v20-sentinel-reaper`, `fix/sovereign-os-dockerfile-source-flags`, `perf/v21-bp100-dynamic-imports` |
| Remaining branches | 1 | `main` (local + remote) |

### Dynamic Import Pattern (Canonical)

```typescript
// CORRECT — dynamic import() for Firebase modules
export async function getAuthInstance() {
  if (!authInstance) {
    const { getAuth } = await import('firebase/auth');
    authInstance = getAuth(app);
  }
  return authInstance;
}
```

```typescript
// PROHIBITED — static import (causes GAPI iframe + cookie penalty)
import { getAuth } from 'firebase/auth'; // ← NEVER do this at module level
```

---

## Version History

| Version | Codename | HEAD Commit | PR | Date |
|---------|----------|-------------|-----|------|
| V25 | **Pinnacle** (MCP Fleet Ascension + Manifest Gap Closure) | `649c25fc6` | — | 2026-05-09 |
| V23 | Hyper-Core (Bun-Native Cascade + Pomelli Swarm) | `8bd3ac2c2` | — | 2026-05-09 |
| V22 | Phosphor-Shift (Dynamic Import Ascension) | `5744baeab` | #91 (merged) | 2026-05-09 |
| V20.1 | Sentinel-Reaper (Octal Fix) | `357ace6e9` | — | 2026-05-09 |
| V20 | Sentinel-Reaper | `e828b6abf` | — | 2026-05-09 |
| V19.1 | Fix Branch Consolidation | `8023e9925` | — (direct merge) | 2026-05-09 |
| V19 | Cognitive Router + FinOps Governor | `aec15aeb9` | #88 (merged) | 2026-05-09 |
| V18 | Isomorphic GraphQL Ascension | `f35fb96ae` | — | 2026-05-08 |
| V17 | Archon-Bun Hyper-Core | `5ef4218b3` | — | 2026-05-08 |
| V16 | Absolute OS | `8b78eaaa4` | — | 2026-05-08 |
| V15 | Ground Truth Revision | `351ca4856` | — | 2026-05-07 |
