# Cor.30 Quarterly Re-Audit Calendar

> Enforces regular security hygiene review per the Cor.30 Anti-Vibe Security Doctrine.

## Quarterly Schedule

| Quarter | Due Date | Focus | Scope |
|---------|----------|-------|-------|
| Q3 2026 | 2026-07-15 | Full Cor.30 checklist + third-party audit | All 6 pillars |
| Q4 2026 | 2026-10-15 | Dependency + supply chain audit | Pillars 2, 3 |
| Q1 2027 | 2027-01-15 | Identity + session + payments review | Pillars 1, 5 |
| Q2 2027 | 2027-04-15 | Full Cor.30 re-certification | All 6 pillars |

## Checklist Per Audit

### Pre-Audit (day before)
- [ ] Run `gitleaks detect --source apps/ --config .gitleaks.toml`
- [ ] Run `vulture` + `ruff --fix` on all production paths
- [ ] Verify `.gitleaksignore` fingerprint count matches expectations
- [ ] Check RISK_REGISTER.md for open items

### During Audit
- [ ] Run full Cor.30 6-pillar checklist (`docs/SECURITY_DOD.md`)
- [ ] Review OWASP LLM Top 10 compliance
- [ ] Test Stripe webhook HMAC verification
- [ ] Review Cloud Armor WAF rules
- [ ] Check secret rotation dates
- [ ] Run Lighthouse (A11y + BP + SEO + Performance)
- [ ] Review pre-commit hook state

### Post-Audit
- [ ] Update RISK_REGISTER.md with new findings
- [ ] Update AGENTS.md hardened state block
- [ ] Create GitHub issues for any remediation work
- [ ] Archive audit CSV to NotebookLM Master Brain
- [ ] Commit and push audit artifacts

## Tooling

| Tool | Command | Purpose |
|------|---------|---------|
| Gitleaks Guardian | `python3 scripts/gitleaks_guardian.py --mode scan --scope production` | Secret detection |
| Vulture | `python3 -m vulture scripts/ --min-confidence 80` | Dead code |
| Ruff | `python3 -m ruff check apps/ scripts/ tests/` | Lint |
| Lighthouse | `npx lighthouse https://kovelai.web.app --output=json` | Web quality |
| Dream Consolidation | `/opt/homebrew/bin/python3 scripts/dream_consolidation.py` | KI maintenance |

## Baseline (Q2 2026 — Audit #0)

- **Date**: 2026-04-19
- **Gitleaks**: 686 third-party findings audited → 0 risk
- **Production scan**: 33 findings (all aiyou_stack `.example` files — false positives)
- **Vulture**: 0 violations at 80%+ confidence
- **Ruff**: 0 in counselconduit
- **Lighthouse**: A93+ / BP100 / SEO100
- **Risk Register**: 43 risks tracked (0 critical open)
