# Migration Checklist

**Project**: Migrate from `Monorepo-Uphillsnowball` → `shadowtagai-monorepo-v2`
**Start Date**: May 11, 2026
**Target Completion**: June 5, 2026 (4 weeks)
**Overall Owner**: Platform Team + Engineering Leads

---

## Phase 0: Preparation (May 11 – May 13)

| # | Task | Owner | Deadline | Status |
|---|------|-------|----------|--------|
| 0.1 | Create `shadowtagai-monorepo-v2` using template | Platform Team | May 11 | ✅ Done |
| 0.2 | Clone both repos locally | Platform Team | May 11 | ✅ Done |
| 0.3 | Run `repo_doctor.py` on current repo | Platform Team | May 12 | ⬜ Ready |
| 0.4 | Set up new repo structure (apps/, libs/, infra/, tools/) | Platform Team | May 13 | ⬜ Ready |
| 0.5 | Create GitHub Projects board for migration | Platform Team | May 13 | ⬜ Ready |

---

## Phase 1: Audit & Inventory (May 12 – May 14)

| # | Task | Owner | Deadline | Status |
|---|------|-------|----------|--------|
| 1.1 | Inventory all services, libraries, and monoliths | Engineering Leads | May 13 | ⬜ Ready |
| 1.2 | Document all nested `.git` directories | Platform Team | May 13 | ⬜ Ready |
| 1.3 | Map current files to new repo structure | Platform Team | May 14 | ⬜ Ready |
| 1.4 | Identify which components move to `infrastructure-catalog-gcp-cloud-run` | Platform Team | May 14 | ⬜ Ready |
| 1.5 | Create migration decision log (Notion / Google Doc) | Platform Team | May 14 | ⬜ Ready |

---

## Phase 2: Rich Hickey Refactoring (May 14 – May 22)

| # | Task | Owner | Deadline | Status |
|---|------|-------|----------|--------|
| 2.1 | Refactor `layers.py` (13 classes → 9 focused files) | Engineering Leads | May 18 | ⬜ Ready |
| 2.2 | Refactor `cor_orchestrator.py` (9 classes → 5 files) | Engineering Leads | May 19 | ⬜ Ready |
| 2.3 | Extract `KineticActionParser` into separate module | Engineering | May 20 | ⬜ Ready |
| 2.4 | Extract `OracleStudio` into separate module | Engineering | May 20 | ⬜ Ready |
| 2.5 | Move shared logic into `libs/` and `packages/` | Engineering | May 21 | ⬜ Ready |
| 2.6 | Run `repo_doctor.py` after each major refactor | Platform Team | May 22 | ⬜ Ready |

---

## Phase 3: Infrastructure Migration (May 15 – May 23) — Parallel Track

| # | Task | Owner | Deadline | Status |
|---|------|-------|----------|--------|
| 3.1 | Create `infrastructure-catalog-gcp-cloud-run` repo | Platform Team | May 15 | ⬜ Ready |
| 3.2 | Create `infrastructure-live-gcp` repo | Platform Team | May 15 | ⬜ Ready |
| 3.3 | Create `infrastructure-pulumi` repo | Platform Team | May 15 | ⬜ Ready |
| 3.4 | Migrate Cloud Run modules + Cloud Deploy canary pipeline | Platform Team | May 20 | ⬜ Ready |
| 3.5 | Migrate Terragrunt stacks | Platform Team | May 21 | ⬜ Ready |
| 3.6 | Migrate Pulumi components (if applicable) | Platform Team | May 22 | ⬜ Ready |
| 3.7 | Set up GitHub Actions in all three repos | Platform Team | May 23 | ⬜ Ready |

---

## Phase 4: Code Migration & Cutover (May 23 – May 30)

| # | Task | Owner | Deadline | Status |
|---|------|-------|----------|--------|
| 4.1 | Final freeze of development on old repo | Engineering Leads | May 23 | ⬜ Ready |
| 4.2 | Copy refactored code into new repo structure | Engineering | May 26 | ⬜ Ready |
| 4.3 | Create clean commits with clear messages | Engineering | May 27 | ⬜ Ready |
| 4.4 | Migrate critical history via `git cherry-pick` (if needed) | Platform Team | May 28 | ⬜ Ready |
| 4.5 | Update all internal imports and paths | Engineering | May 29 | ⬜ Ready |
| 4.6 | Run full test suite in new repo | Engineering | May 30 | ⬜ Ready |

---

## Phase 5: Final Cutover & Verification (May 30 – June 3)

| # | Task | Owner | Deadline | Status |
|---|------|-------|----------|--------|
| 5.1 | Final run of `repo_doctor.py` on new repo | Platform Team | May 30 | ⬜ Ready |
| 5.2 | Push all changes to `shadowtagai-monorepo-v2` | Platform Team | May 31 | ⬜ Ready |
| 5.3 | Update all CI/CD pipelines to point to new repo | Platform Team | June 1 | ⬜ Ready |
| 5.4 | Update documentation and internal links | Platform Team | June 1 | ⬜ Ready |
| 5.5 | Make old repo read-only | Platform Team | June 2 | ⬜ Ready |
| 5.6 | Final verification (builds, tests, deployments) | All Teams | June 3 | ⬜ Ready |

---

## Phase 6: Post-Migration Cleanup (June 3 – June 5)

| # | Task | Owner | Deadline | Status |
|---|------|-------|----------|--------|
| 6.1 | Remove nested `.git` directories from old repo | Platform Team | June 3 | ⬜ Ready |
| 6.2 | Consolidate CI workflows (target: 60 → ~15) | Platform Team | June 4 | ⬜ Ready |
| 6.3 | Archive old repo (or move to archive organization) | Platform Team | June 4 | ⬜ Ready |
| 6.4 | Update onboarding docs and runbooks | Platform Team | June 5 | ⬜ Ready |
| 6.5 | Celebrate + retrospective | All Teams | June 5 | ⬜ Ready |

---

## Summary

| Phase | Dates | Main Owner | Key Deliverable |
|-------|-------|------------|-----------------|
| 0. Preparation | May 11–13 | Platform Team | New repo created + structure ready |
| 1. Audit | May 12–14 | Platform + Engineering | Full inventory completed |
| 2. Refactoring | May 14–22 | Engineering Leads | Monoliths broken into focused modules |
| 3. Infrastructure | May 15–23 | Platform Team | Three new IaC repos live |
| 4. Migration | May 23–30 | All Teams | Code moved + tests passing |
| 5. Cutover | May 30 – June 3 | Platform Team | New repo is production |
| 6. Cleanup | June 3–5 | Platform Team | Old repo archived + docs updated |
