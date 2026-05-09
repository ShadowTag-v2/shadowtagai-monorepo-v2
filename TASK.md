# TASK.md — ShadowTagAI Monorepo v2 Migration Tracker

> **Created:** 2026-05-09 | **Status:** IN PROGRESS | **Owner:** Antigravity

---

## Phase 0: Infrastructure Scaffolding

| # | Task | Status | Notes |
|---|------|--------|-------|
| 0.1 | Clone `shadowtagai-monorepo-v2` | ✅ Done | `a358f2e` on `main` |
| 0.2 | Configure `MODULE.bazel` (TS/JS/Python/Go/Rust/OCI/Helm) | ✅ Done | 133 lines |
| 0.3 | Configure root `BUILD.bazel` | ✅ Done | pip_compile + formatting |
| 0.4 | Scaffold `.github/workflows/` | ✅ Done | `bazel-ci.yml`, `dependency-review.yml` |
| 0.5 | Configure `firebase.json` (4 hosting targets) | ✅ Done | shadowtagai, kovelai, headfade, counselconduit |
| 0.6 | Create `REVIEW.md` (sovereign review doctrine) | ✅ Done | Three-Tier verification |
| 0.7 | Create Jules PR Review workflow | ✅ Done | `.github/workflows/jules-pr-review.yml` |
| 0.8 | Create swarm orchestrator | ✅ Done | `tools/scripts/run_swarm.py` |
| 0.9 | Create findings poster | ✅ Done | `tools/scripts/post_pr_findings.py` |
| 0.10 | Create AST surgery script | ✅ Done | `scripts/ast_surgery.ts` |
| 0.11 | Clone `third_party/ANE` | ✅ Done | M1 Max ANE bridge |
| 0.12 | Create `.gemini/code-assist.yml` | ✅ Done | GCA config |
| 0.13 | Create `.gemini/prompts/` content | ✅ Done | PR review prompt |
| 0.14 | Create `.gemini/rules/` content | ✅ Done | Monorepo rules |
| 0.15 | Create `trigger-pr-review.sh` | ✅ Done | Manual execution |
| 0.16 | Create `omni-ci.yml` | ✅ Done | Full CI pipeline |
| 0.17 | Create `TASK.md` | ✅ Done | This file |
| 0.18 | Create `docs/decision-log.md` | ✅ Done | ADR log |

## Phase 1: Migration Extraction

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1.1 | Extract `headfade-pwa` → `apps/headfade/` | ✅ Done | Next.js PWA |
| 1.2 | Extract `counselconduit-api` → `apps/counselconduit/` | ✅ Done | FastAPI backend |
| 1.3 | Extract `aiyou_stack` → `apps/aiyou_stack/` | ✅ Done | FastAPI services |
| 1.4 | Scaffold `apps/claurst/` | ✅ Done | Rust agent loop |
| 1.5 | Wire `ane_bridge.py` + `zero_cpu_router.py` | ✅ Done | ANE orchestrator |
| 1.6 | Create `BUILD.bazel` for migrated apps | ✅ Done | Per-app targets |
| 1.7 | Inventory old repo components | 🔲 Pending | `repo_doctor.py` |
| 1.8 | Rollback playbook | ✅ Done | `docs/rollback-playbook.md` |

## Phase 2: Build System Verification

| # | Task | Status | Notes |
|---|------|--------|-------|
| 2.1 | Install `ibazel` | 🔲 Pending | Hot-reload |
| 2.2 | Run `pip_generate_requirements_txt` | 🔲 Pending | Python lock |
| 2.3 | Set up Go module support | ✅ Done | `go.mod` scaffold |
| 2.4 | Verify Rust toolchain | 🔲 Pending | `cargo check` |
| 2.5 | Create Docker/OCI targets | ✅ Done | `infra/docker/` |
| 2.6 | Wire Helm chart templates | ✅ Done | `infra/helm/` |
| 2.7 | Verify MODULE.bazel integrity | 🔲 Pending | `bazel build //...` |

## Phase 3: CI/CD & Tooling

| # | Task | Status | Notes |
|---|------|--------|-------|
| 3.1 | Full GitHub Actions CI | ✅ Done | `omni-ci.yml` |
| 3.2 | Configure Renovate Bot | ✅ Done | `renovate.json` exists |
| 3.3 | Set up testing framework | ✅ Done | pytest + vitest + go test |
| 3.4 | Update clone script (remove 4 dead repos) | 🔲 Pending | |
| 3.5 | Run external repo cloner (100+ repos) | 🔲 Pending | ~2GB |

## Phase 4: Verification & Audit

| # | Task | Status | Notes |
|---|------|--------|-------|
| 4.1 | Run `repo_doctor.py` on old monorepo | 🔲 Pending | |
| 4.2 | Run Lighthouse on HeadFade production | 🔲 Pending | Pre-migration baseline |
| 4.3 | Push to origin via SSH | 🔲 Pending | |
| 4.4 | Push `a358f2e` to old repo via GitHub App JWT | 🔲 Pending | |
| 4.5 | Generate IaC repos (`generate-three-repos.sh`) | 🔲 Pending | |

## Phase 5: Production Cutover

| # | Task | Status | Notes |
|---|------|--------|-------|
| 5.1 | DNS/CDN switchover plan | 🔲 Pending | |
| 5.2 | Stripe webhook re-pointing | 🔲 Pending | |
| 5.3 | Cloud Run service migration | 🔲 Pending | |
| 5.4 | Final rollback verification | 🔲 Pending | |
