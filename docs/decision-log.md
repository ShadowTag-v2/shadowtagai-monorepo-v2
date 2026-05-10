# Architecture Decision Log

> **Project:** ShadowTagAI Monorepo v2
> **Started:** 2026-05-09

---

## ADR-001: Bazel as Primary Build System

**Date:** 2026-05-09
**Status:** Accepted
**Context:** Need a polyglot build system supporting TS/JS, Python, Go, Rust, OCI containers, and Helm charts in a single monorepo.
**Decision:** Use Bazel (via Aspect CLI) with `MODULE.bazel` (Bzlmod) for dependency management.
**Consequences:** Steeper learning curve offset by hermetic builds, remote caching, and cross-language dependency tracking. All apps share a single build graph.

---

## ADR-002: pnpm as Node Package Manager

**Date:** 2026-05-09
**Status:** Accepted
**Context:** npm causes lockfile conflicts. yarn v4 has PnP complexity. pnpm provides fast, disk-efficient installs with strict dependency isolation.
**Decision:** Standardize on pnpm with `pnpm-workspace.yaml` for all Node.js packages.
**Consequences:** All `package.json` files must use pnpm. No npm/yarn lockfiles allowed.

---

## ADR-003: Three-Tier PR Verification Architecture

**Date:** 2026-05-09
**Status:** Accepted
**Context:** Automated PR reviews need hardware-aware verification beyond simple linting.
**Decision:** Three tiers: Tier 1 (Linting — Ruff/Biome), Tier 2 (Cloud GPU — Colab T4/IPC), Tier 3 (Local ANE — M1 Max).
**Consequences:** Critical findings require physical behavioral verification. Speculative linting alone cannot produce 🔴 Critical severity.

---

## ADR-004: Firebase Hosting Multi-Target Configuration

**Date:** 2026-05-09
**Status:** Accepted
**Context:** Four distinct web properties (ShadowTagAI, KovelAI, HeadFade, CounselConduit Dashboard) need independent hosting targets with shared security headers.
**Decision:** Use Firebase multi-site hosting with per-target CSP policies. All targets share HSTS preload, X-Frame-Options DENY, and Permissions-Policy.
**Consequences:** Each app deploys independently. CSP policies are tailored per app (e.g., HeadFade allows Unsplash, CounselConduit does not).

---

## ADR-005: GitHub App PEM as Sole Authentication

**Date:** 2026-05-09
**Status:** Accepted
**Context:** PATs are insecure and non-auditable. Deploy keys lack granularity. `gh auth login` creates stale credentials.
**Decision:** All GitHub API operations use GitHub App installation tokens generated from PEM (App ID: 3018200). SSH is primary transport for git operations.
**Consequences:** JWT generation required for every API call. 5-tier PEM fallback chain ensures availability.

---

## ADR-006: Monorepo Directory Structure

**Date:** 2026-05-09
**Status:** Accepted
**Context:** Need clear separation between apps, shared libraries, infrastructure, and tooling.
**Decision:**
```
apps/           → Deployable applications
libs/           → Shared libraries and packages
infra/          → Infrastructure-as-Code (Terraform, Helm, Docker)
tools/          → Developer tooling and scripts
scripts/        → Build and automation scripts
third_party/    → Vendored external code
external_repos/ → Cloned reference repositories
docs/           → Documentation
```
**Consequences:** All new code must go into the correct directory. No top-level app code.

---

## ADR-007: GCP Secret Manager as Sole Secrets Store

**Date:** 2026-05-09
**Status:** Accepted
**Context:** `.env` files are banned. Hardcoded secrets are a security violation.
**Decision:** All secrets fetched from GCP Secret Manager. Local dev uses `scripts/load_mcp_secrets.sh`. Production uses `valueFrom.secretKeyRef`.
**Consequences:** No `.env` files. No `python-dotenv`. MCP config uses `${VAR}` references resolved by platform.

---

## ADR-008: CounselConduit Migration Strategy

**Date:** 2026-05-09
**Status:** Accepted
**Context:** CounselConduit backend (FastAPI) must migrate from old monorepo without downtime.
**Decision:** Copy-and-adapt migration. Production Cloud Run service (`counselconduit-00037-7mf`) continues running from old repo until new repo CI/CD is verified. Canary deployment with 10% → 50% → 100% traffic shift.
**Consequences:** Dual-repo period required. Rollback is instant (revert traffic routing).

---

## ADR-009: Rust Agent Loop (Claurst)

**Date:** 2026-05-09
**Status:** Proposed
**Context:** High-performance agent execution loop needs sub-millisecond latency for real-time inference routing.
**Decision:** Implement core agent loop in Rust (`apps/claurst/`) with Python FFI bridge for ML model integration.
**Consequences:** Requires Rust toolchain in CI. Python bridge via PyO3.
