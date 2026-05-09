# Migration Risk Register

**Project**: `Monorepo-Uphillsnowball` → `shadowtagai-monorepo-v2`
**Date**: May 9, 2026
**Review Frequency**: Weekly (every Monday)

---

## Risk Matrix

| Risk ID | Risk Description | Likelihood | Impact | Risk Score | Mitigation Strategy | Owner | Status |
|---------|------------------|------------|--------|------------|---------------------|-------|--------|
| **R01** | Loss of critical commit history during migration | Medium | High | **12** | Use selective `git cherry-pick` for important commits only. Keep old repo as read-only archive for reference. | Platform Team | Open |
| **R02** | Broken imports and dependency errors after refactoring | High | High | **16** | Run `repo_doctor.py` after every major refactor. Use automated import fixing scripts. | Engineering Leads | Open |
| **R03** | CI/CD pipeline downtime during cutover | Medium | High | **12** | Maintain parallel CI in both repos during transition. Freeze deployments 48h before cutover. | Platform Team | Open |
| **R04** | Secret or sensitive data leakage during migration | Low | Critical | **12** | Run `betterleaks` + `trufflehog` before every push. Use `repo_doctor.py` secret scan. | Security | Open |
| **R05** | Significant drop in team velocity during refactoring phase | High | Medium | **12** | Allocate 30% capacity buffer. Pair programming on monolith splits. | Engineering Leads | Open |
| **R06** | Infrastructure drift between old and new repos | Medium | High | **12** | Migrate infrastructure first (Phase 3). Freeze infra changes in old repo after May 20. | Platform Team | Open |
| **R07** | Test suite failures after code migration | Medium | High | **12** | Run full test suite in new repo daily during migration. Fix failing tests immediately. | Engineering | Open |
| **R08** | Scope creep — trying to refactor too many monoliths at once | Medium | Medium | **9** | Strict scope control. Only `layers.py` and `cor_orchestrator.py` in Phase 2. Everything else in Phase 6. | Engineering Leads | Open |
| **R09** | Key person dependency (only one person understands the monoliths) | Medium | High | **12** | Document architecture decisions. Pair program with at least one other engineer. | Engineering Leads | Open |
| **R10** | Rollback becomes difficult if major issues appear after cutover | Low | High | **8** | Keep old repo read-only but fully functional until June 10. Document rollback procedure. | Platform Team | Open |
| **R11** | Confusion among team members about which repo is active | Medium | Medium | **9** | Clear communication plan. Update all docs, Slack channels, and onboarding by May 30. | Platform Team | Open |
| **R12** | Performance regression in production after migration | Low | High | **8** | Run load tests (Locust) on new repo before cutover. Monitor key metrics for 7 days post-cutover. | Platform Team | Open |

---

## Risk Score Legend

| Score | Level | Action Required |
|-------|-------|-----------------|
| 1–6   | Low   | Monitor |
| 7–12  | Medium | Mitigation Plan Required |
| 13–20 | High  | Immediate Action + Weekly Review |
| 21–25 | Critical | Executive Escalation |

---

## Top 3 Highest Risks (Priority Focus)

| Rank | Risk ID | Score | Mitigation Owner | Next Review Date |
|------|---------|-------|------------------|------------------|
| 1    | **R02** | 16    | Engineering Leads | May 12 |
| 2    | **R03** | 12    | Platform Team     | May 12 |
| 3    | **R01** | 12    | Platform Team     | May 12 |

---

## Risk Register Owner & Review Cadence

- **Primary Owner**: Platform Team
- **Secondary Owner**: Engineering Leads
- **Review Cadence**: Every Monday at 10:00 AM PDT
- **Escalation Path**: Platform Lead → CTO if any risk score ≥ 16
