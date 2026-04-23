# v12 Release Scope Plan

## Codename: **Citadel**

## Prior Release Summary
- **v11.0-obsidian**: Lighthouse Budget + 11x Extractor + IDE Governance + Epistemic Airgap

## v12 Priority Areas

### 🔒 P0 — Security & Infra Blockers
1. **uuid7 Cloud Run fix** — Rebuild container with monorepo-resolved uuid7. Eliminates `try/except ImportError` workaround in container `counselconduit-00015-mmq` → `counselconduit-00036+`.
2. **firebase-admin upgrade** in `lead-capture-router` — Breaking change from `>=10.2.0` → `10.1.0` to resolve all 10 npm moderate vulns (@tootallnate/once, http-proxy-agent, uuid).
3. **Firebase Storage Rules** — Console initialization needed. Currently deny-all.
4. **Branch protection** — Requires GitHub Pro upgrade or make repo public. Defer or upgrade.

### 🧪 P1 — Test Coverage Sprint
- Current: **11.18%** (287 passed, 2 skipped)
- Target: **20%** by v12
- Strategy: Cover `vent_mode.py` (112 LOC), `workspace_alerts.py` (98 LOC), `stripe_connect.py` (66 LOC), `sandbox/runner.py` (69 LOC)
- Coverage threshold bumped from 10% → 15% → 20% progressive gates

### 📊 P2 — Performance
- **kovelai.web.app**: Perf 78 (FCP 2.7s, LCP 4.4s) — GTM external script (62KB wasted), Next.js chunk (23KB). Defer GTM to requestIdleCallback. Code-split Next.js chunk.
- **shadowtagai.web.app**: Perf 94, A11y 95, BP 96, SEO 100 — healthy baseline.

### 🛠 P3 — Developer Experience
- **GPG key upload** to GitHub for verified commit badges — manual step.
- **pre-commit hooks** wired (✅ done).
- **Dependabot** active (✅ done).
- **NotebookLM MCP CLI** install (`uv tool install notebooklm-mcp-cli`).

### 🔌 P4 — Feature Development
- **Stripe Connect onboarding** end-to-end test suite
- **Vent Mode** SSE streaming performance tests
- **Oracle Studio** 7-stage pipeline integration tests
- **Judge 6** gate automated CI enforcement
- **GDPR 30-day delete** Cloud Tasks job verification

## Release Criteria
- [ ] 20% test coverage
- [ ] uuid7 container fix deployed
- [ ] firebase-admin vuln resolved
- [ ] Lighthouse Performance ≥ 85 on kovelai.web.app
- [ ] All CI gates green
- [ ] CHANGELOG.md updated
