# Changelog

All notable changes to this project will be documented in this file.
Format follows [Conventional Commits](https://www.conventionalcommits.org/).

## [Unreleased]

### 2026-04-16

#### Infrastructure & Monitoring
- **fix(lint):** ruff --fix UP045 annotation + omega debris cleanup (`21362b85ce1`)
- **fix(infra):** dead code cleanup + uptime monitoring + Lighthouse CI (`46cc52e0fc8`)
- **chore:** update BUSINESS_CONTEXT_LOCKED to v8.5 with full deployment state (`f8aa3c9ae9c`)
- **feat:** production hardening batch — CSP fix, preview channels, GSC meta, deploy (`32fb1341fc6`)

#### Security & Compliance
- **docs(agents):** bump hardened state to v8.5 — 2 Firestore DBs, MCP-first, 3 hosting targets, CSP parity (`76ab6506657`)
- **docs(doctrine):** add Firebase MCP-first deploy protocol, close risk #21, bump to v8.5 (`87aa1feac49`)
- **feat(infra):** batch-3 hardening — CSP headers, A/B testing, WebP, Stripe tests (`7489d6a015f`)

#### Performance
- **perf(hosting):** CSP headers, 404 pages, WebP optimization for both sites (`c76b496fdd4`)
- **perf(kovelai):** WebP image optimization — 89% LCP reduction on hero-bg (`ef74aee97bf`)
- **feat(kovelai):** full 22-item production hardening sweep (`710fb36b47f`)

### 2026-04-15

#### Frontend
- **fix(kovelai):** tablet 768px responsive clamp + ruff auto-fix labs quickstarts (`0f286e81466`)
- **fix(kovelai):** tighten hero clamp for 768px + ruff dead code cleanup (`2c617eadc42`)
- **fix(kovelai):** fluid clamp() typography + container padding for responsive hero (`29d0a7f2235`)
- **feat(kovelai):** add first-party data harvesting engine & cookie audit tables (`e79f1c5701d`)
- **feat(kovelai):** persistent cookie float button + cache-bust meta tags (`36ffd30a6bb`)
- **feat(kovelai):** Unusual Machines cookie consent + no-cache headers (`e1db791b933`)
- **feat(shadowtagai):** finalize hero and research pipeline sections (`3ce0278ccde`)
- **feat(kovelai):** apply Fluid Kinetic Aura parity with ShadowTagAI (`2c30b24782b`)

#### Infrastructure
- **fix(mcp):** eliminate all npx cold-starts, add firebase-mcp-fast.js direct entrypoint (`d12b29cc8dd`)
- **chore(sync):** monorepo bulk ingestion batch 1 of 1 (25MB chunks) (`7459f094e07`)

### 2026-04-14

#### Core Features
- **feat(security):** harden IDOR/BAC + repair MCP fleet + Gmail MX DNS (`1ad98522d93`)
- **feat:** Stripe webhook handler + Lighthouse performance hardening (`83176949efd`)
- **feat(mcp):** rewrite fleet to 9-server config, enforce MCP-first routing (`e37229636a2`)
- **feat(skills):** mega-audit 31 repos, install 8 novel skills, upgrade 3 core skills (`19fcaef9c34`)
- **fix(models):** resolve all F821 undefined name errors with TYPE_CHECKING guards (`c2820ede672`)
- **feat:** Compiler Guillotine sweep + Autoresearch Triad + Ignite Sovereign (`cee4f776f1a`)
- **feat(invariants):** v8.6 — Sovereign State Protocol folded into 7 skills (`be70f168831`)

---

*Generated from `git log --oneline --no-merges` on 2026-04-16.*
