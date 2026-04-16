# ShadowTag Omega v4 — Project Changelog

All notable changes to the ShadowTag Omega v4 monorepo are documented here.

## [2026-04-16] — Batch 3 Production Hardening

### Added
- Firebase MCP-First Deployment Protocol (`GEMINI.md` v8.5)
- `skills/firebase-mcp-deploy-doctrine/SKILL.md` enforcement skill
- CSP security headers on both KovelAI and ShadowTagAI (8/8 headers)
- A/B testing framework on KovelAI (`variant-` class patterns)
- Video engagement tracking for hero video
- 16-test Stripe webhook pytest suite
- Cloud Monitoring alert policy (Cloud Function error rate)
- Email notification channel (`founder@shadowtagai.com`)
- GCS CORS hotlink protection on `shadowtag-omega-v4-archive`
- Hero image `<link rel="preload">` on ShadowTagAI for LCP improvement
- Firebase Storage initialized with zero-trust deny-all rules
- KovelAI lead capture scaffold (Cloud Function `captureLead` — ACTIVE)
- Nag protocol bumped 12→22 for 2x output density

### Changed
- `AGENTS.md` bumped to v8.5 (2 Firestore DBs, MCP-first, 3 hosting targets)
- KovelAI hero image converted to WebP (89% LCP reduction)
- All below-fold images: `loading="lazy"` + `decoding="async"` enforced
- Hero LCP image: `fetchpriority="high"` on both sites
- ShadowTagAI: `dns-prefetch` hints for CDN/Storage/Google domains

### Fixed
- Tablet 768px responsive clamp for KovelAI hero typography
- Overflow-x hidden to prevent horizontal scroll shift
- Cookie consent banner persistence

### Security
- Zero-trust Firestore rules (admin-only) on both databases
- Zero-trust Storage rules (deny-all)
- HSTS with `includeSubDomains; preload`
- `X-Frame-Options: DENY` + full CSP on both sites
- GA4 Consent Mode v2 defaulting to denied
- reCAPTCHA v3 for all lead capture forms

### Deployed
- `kovelai.web.app` (KovelAI production)
- `shadowtagai.web.app` (ShadowTagAI production)
- `shadowtag-omega-v4.web.app` (default site)

### Lighthouse
| Site | A11y | Best Practices | SEO | Perf |
|------|:---:|:---:|:---:|:---:|
| KovelAI | 100 | 100 | 100 | 78 |
| ShadowTagAI | 100 | 96 | 100 | 77 |

---

## [2026-04-15] — UI Parity & Cookie Compliance

### Added
- Unusual Machines-style cookie consent banner (GDPR/CCPA compliant)
- First-party data harvesting engine & cookie audit tables
- Persistent cookie settings float button
- Fluid Kinetic Aura parity between KovelAI and ShadowTagAI

### Fixed
- Hero layout centering + broken hero image visibility
- Gold border line removed from hero image container
- Cache-bust meta tags

---

## [2026-04-14] — Infrastructure Hardening

### Added
- Omega Sync CI workflow (`peter-murray/workflow-application-token-action@v4`)
- 14-server MCP fleet with DK URL fix
- IDOR/BAC security hardening
- Gmail MX DNS configuration
- Stripe webhook handler (FastAPI)
- LanceDB overwrite fix + re-ingestion
- 8 novel skills installed, 3 core skills upgraded
- Cor artifacts extracted (Shield/GEPA/ST3GG/Objections)

### Fixed
- All F821 undefined name errors with `TYPE_CHECKING` guards
- Monkey Ban enforced (0 violations)
- Skill consolidation

### Removed
- All 13 git submodules (absorbed as plain directories)
