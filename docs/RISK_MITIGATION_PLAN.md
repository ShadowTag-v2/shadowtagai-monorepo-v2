# Risk Mitigation Action Plan

**Project**: Migration to `shadowtagai-monorepo-v2`
**Date**: May 9, 2026
**Focus**: Top 6 Highest Risks

---

## 1. Risk R02: Broken Imports and Dependency Errors (Highest Priority)

**Risk Score**: 16 (High)

| Step | Action | Owner | Deadline | Success Criteria |
|------|--------|-------|----------|------------------|
| 1 | Run `repo_doctor.py --fix-imports` after every major refactor | Engineering | Ongoing | < 5 import errors per module |
| 2 | Create automated import fixer script using `ast-grep` | Platform Team | May 14 | Script passes 90% of cases |
| 3 | Add import validation step to pre-commit hooks | Platform Team | May 15 | All PRs blocked on import errors |
| 4 | Pair programming on all monolith splits | Engineering Leads | May 16–22 | Every split reviewed by 2 people |
| 5 | Daily import health check in CI | Platform Team | May 17 onward | Zero broken imports in main branch |

**Contingency**: If import errors exceed 50 after refactoring, pause Phase 2 and dedicate 2 days to stabilization.

---

## 2. Risk R03: CI/CD Pipeline Downtime During Cutover

**Risk Score**: 12 (Medium-High)

| Step | Action | Owner | Deadline | Success Criteria |
|------|--------|-------|----------|------------------|
| 1 | Run parallel CI in both old and new repo until June 3 | Platform Team | May 20 | Both pipelines green daily |
| 2 | Freeze all deployments 48 hours before cutover | Engineering Leads | May 29 | No production changes after May 29 |
| 3 | Create rollback playbook and test it | Platform Team | May 28 | Rollback tested successfully in staging |
| 4 | Maintain old repo as hot standby until June 10 | Platform Team | June 3 | Old repo remains fully functional |
| 5 | Set up Slack alerts for pipeline failures | Platform Team | May 18 | Alerts fire within 2 minutes |

**Contingency**: If new repo CI fails on cutover day, immediately switch back to old repo and delay migration by 48 hours.

---

## 3. Risk R01: Loss of Critical Commit History

**Risk Score**: 12 (Medium-High)

| Step | Action | Owner | Deadline | Success Criteria |
|------|--------|-------|----------|------------------|
| 1 | Identify top 20 most important commits (legal, security, architecture decisions) | Engineering Leads | May 15 | List approved by team |
| 2 | Use `git cherry-pick` to bring important commits into new repo | Platform Team | May 25 | 100% of critical commits preserved |
| 3 | Keep old repo as permanent read-only archive | Platform Team | June 3 | Old repo archived with clear README |
| 4 | Document key decisions in new repo's `docs/decision-log.md` | Engineering | May 26 | All major decisions documented |
| 5 | Create migration commit message template | Platform Team | May 14 | Consistent history in new repo |

---

## 4. Risk R05: Significant Drop in Team Velocity

**Risk Score**: 12 (Medium-High)

| Step | Action | Owner | Deadline | Success Criteria |
|------|--------|-------|----------|------------------|
| 1 | Allocate 30% capacity buffer for refactoring phase | Engineering Leads | May 13 | Sprint capacity adjusted |
| 2 | Use pair programming on all monolith splits | Engineering | May 14–22 | 100% of refactors done in pairs |
| 3 | Limit refactoring to maximum 2 files per day per engineer | Engineering Leads | May 14 | Velocity drop < 25% |
| 4 | Daily standup focused only on migration blockers | All Teams | May 15 onward | Blockers resolved within 24h |
| 5 | Celebrate small wins (e.g., after each monolith split) | Engineering Leads | Weekly | Team morale maintained |

---

## 5. Risk R09: Key Person Dependency

**Risk Score**: 12 (Medium-High)

| Step | Action | Owner | Deadline | Success Criteria |
|------|--------|-------|----------|------------------|
| 1 | Identify single points of failure (who knows the monoliths best) | Engineering Leads | May 12 | List created |
| 2 | Schedule knowledge transfer sessions (minimum 3 sessions) | Engineering | May 13–20 | At least 2 engineers understand each monolith |
| 3 | Document architecture decisions in `docs/architecture.md` | Engineering | May 18 | Documentation covers 90% of logic |
| 4 | Create "Bus Factor" report for critical components | Platform Team | May 19 | No component has bus factor of 1 |
| 5 | Rotate ownership of refactored modules | Engineering Leads | May 22 | Every module has at least 2 owners |

---

## 6. Risk R04: Secret or Sensitive Data Leakage

**Risk Score**: 12 (Medium-High)

| Step | Action | Owner | Deadline | Success Criteria |
|------|--------|-------|----------|------------------|
| 1 | Run `betterleaks` + `trufflehog` on every commit | Platform Team | Ongoing | Zero secrets in git history |
| 2 | Add secret scanning to pre-commit and CI | Platform Team | May 14 | All PRs blocked on secret detection |
| 3 | Replace all hardcoded secrets with GCP Secret Manager references | Engineering | May 18 | 100% of secrets in Secret Manager |
| 4 | Audit `.gitignore` for secret exclusion patterns | Security | May 15 | No secrets committed |
| 5 | Final secret scan before cutover | Security | May 30 | Clean report |

---

## Risk Mitigation Summary Table

| Risk ID | Risk | Mitigation Owner | Key Deadline | Residual Risk |
|---------|------|------------------|--------------|---------------|
| R02     | Broken imports | Engineering Leads | May 22 | Low |
| R03     | CI/CD downtime | Platform Team | May 29 | Low |
| R01     | History loss | Platform Team | May 25 | Low |
| R05     | Velocity drop | Engineering Leads | May 22 | Medium |
| R09     | Key person dependency | Engineering Leads | May 20 | Low |
| R04     | Secret leakage | Security | May 30 | Very Low |
