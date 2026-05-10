# V11 Sprint Plan — CounselConduit

> **Version**: v1.0 | **Last Updated**: 2026-04-22
> **Target**: v11.0 release
> **Duration**: 30 days from v10.0 gold master

---

## Sprint Goals

1. **Citation UI** — Perplexity-style inline citations with legal authority chain
2. **Attorney Brief Builder** — Export-ready privileged document generation
3. **Sandbox Isolation** — Per-tenant isolated tool runners
4. **BYOC/BYOK Frontend** — Client-facing key management UI
5. **Frontend Rebuild** — Next.js App Router with design system components

---

## Week 1: Citation UI + Authority Chain

### Days 1-3: Backend
- [ ] Oracle Studio Stage 4 enhancement: structured citation output
- [ ] Citation schema: `{index, authority, excerpt, type, relevance_score}`
- [ ] Authority validation against Westlaw/LexisNexis API stubs
- [ ] Judge 6 citation integrity check

### Days 4-5: Frontend
- [ ] Citation component: inline superscript markers
- [ ] Citation panel: expandable authority details
- [ ] Relevance score visualization (progress bar)
- [ ] "View Source" deep link to authority

### Days 6-7: Integration
- [ ] E2E test: query → Oracle Studio → citations → UI rendering
- [ ] Performance: citation rendering < 50ms
- [ ] Mobile responsive citation panel

---

## Week 2: Attorney Brief Builder

### Days 8-10: Backend
- [ ] `brief_builder.py` — Generate privileged document from session
- [ ] Template: header (privilege notice) → summary → issues → actions → citations
- [ ] Kovel attestation embedding in brief metadata
- [ ] PDF export via WeasyPrint or ReportLab

### Days 11-12: Frontend
- [ ] Brief preview component on attorney dashboard
- [ ] One-click PDF download
- [ ] Print-optimized CSS

### Days 13-14: Testing
- [ ] Brief content accuracy test
- [ ] Privilege header verification
- [ ] GDPR: brief follows 30-day TTL rules

---

## Week 3: Sandbox Isolation

### Days 15-17: Architecture
- [ ] Per-tenant GCP sidecar design (from sidecar-isolation-protocol skill)
- [ ] Ephemeral sandbox-bound tokens (tied to tenant + session + TTL)
- [ ] Read-only filesystem for tool runners
- [ ] Egress restriction configuration

### Days 18-19: Implementation
- [ ] LiteLLM proxy token issuance (user-billed)
- [ ] Sandbox environment variable injection
- [ ] Circuit breaker for sandbox timeouts

### Days 20-21: Testing
- [ ] Tenant isolation verification (cross-tenant access denied)
- [ ] Token expiry test (TTL enforcement)
- [ ] Resource limits test (CPU/memory caps)

---

## Week 4: BYOC/BYOK Frontend + Polish

### Days 22-24: BYOK UI
- [ ] Key registration form (provider selector, key input, validation)
- [ ] Key status dashboard (active, expired, invalid)
- [ ] Key rotation reminder UI
- [ ] Provider-specific instructions (Gemini, Claude, GPT, Grok)

### Days 25-26: Frontend Rebuild Foundation
- [ ] Next.js App Router migration from stub `page.tsx`
- [ ] Design system token injection (from DESIGN_SYSTEM.md)
- [ ] Component library foundation (Button, Card, Input, Modal)
- [ ] Dark theme implementation

### Days 27-28: Polish
- [ ] Scroll-driven animations (Intersection Observer)
- [ ] Glassmorphism card components
- [ ] Micro-animation library (hover, focus, transition)
- [ ] PWA manifest update

### Days 29-30: Release
- [ ] Full regression test suite
- [ ] Lighthouse audit (target: same or better)
- [ ] CHANGELOG update
- [ ] Tag v11.0
- [ ] Deploy to production

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Citation accuracy | > 95% relevant citations per query |
| Brief generation time | < 5 seconds |
| Sandbox boot time | < 2 seconds |
| Frontend Lighthouse | P93+ / A93+ / BP100 / SEO100 |
| New test coverage | 40+ new tests |
| Total endpoints | 38+ (up from 33) |

---

## Dependencies

- Oracle Studio Stage 4 citation schema (backend first)
- Westlaw/LexisNexis API access (stub initially, live in v12.0)
- GCP sidecar configuration (Cloud Run revision)
- Next.js 15 App Router (migration from static HTML)

---

## Risk Register Additions

| Risk | Mitigation | Owner |
|------|-----------|-------|
| Citation hallucination | Judge 6 authority validation gate | Backend |
| Sandbox escape | Read-only FS + egress restrictions + token TTL | Infra |
| BYOK key leakage | Keys encrypted in Secret Manager, never logged | Security |
| Frontend regression | Lighthouse CI gate on every deploy | DevOps |
