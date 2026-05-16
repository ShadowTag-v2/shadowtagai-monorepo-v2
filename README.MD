# AGNT_OS v15.0 — ShadowTagAI Monorepo

**Google-style monorepo operating system** with agent-native architecture, living memory, and production-grade security.

## Quick Start

```bash
git clone git@github.com:ShadowTag-v2/shadowtagai-monorepo-v2.git
cd shadowtagai-monorepo-v2

# Clone all reference repos (22 groups, 100+ repos)
./scripts/clone-external-reference-repos.sh

# Generate infrastructure repos (OpenTofu + Terragrunt + Pulumi)
./scripts/generate-three-repos.sh

# Run health check
python scripts/repo_doctor.py
```

## Architecture

- **Bazel** — Structural truth layer
- **Nx** — Developer experience layer
- **WanderEngine + Memory Kernel** — Living knowledge
- **Ruler + OpenFGA** — Agent doctrine & safety
- **repo_doctor.py** — Self-healing system (ripgrep + ast-grep + betterleaks + Buildifier)
- **Pulumi + OpenTofu + Terragrunt** — Side-by-side IaC (run them together)

## Key Infrastructure Repos (Side-by-Side)

| Repo | Purpose | IaC Tool |
|------|---------|----------|
| `infrastructure-catalog-gcp-cloud-run` | Reusable Cloud Run Gen2 modules | OpenTofu |
| `infrastructure-live-gcp` | Live Terragrunt configuration | Terragrunt |
| `infrastructure-pulumi` | Pulumi TypeScript monorepo | Pulumi |

## Monorepo Structure

```
shadowtagai-monorepo-v2/
├── apps/                          # Application services
│   ├── kovelai/                   # KovelAI agent platform
│   ├── shadowtag-agent/           # Core agent runtime
│   └── counselconduit/            # Legal AI SaaS
├── libs/                          # Shared libraries
├── packages/                      # Published packages
├── infra/                         # Infrastructure-as-Code
├── tools/                         # Developer tooling
├── scripts/                       # Automation scripts
├── docs/                          # Documentation
│   ├── PLAYBOOK.md               # OpenTofu / Pulumi playbook
│   ├── MIGRATION_PLAN.md         # Full migration plan
│   ├── MIGRATION_CHECKLIST.md    # Detailed task checklist
│   ├── RISK_REGISTER.md          # 12-risk register
│   └── RISK_MITIGATION_PLAN.md   # Mitigation actions
├── experimental/                  # Experimental features
├── external_repos/                # Cloned reference repos (22 groups)
├── MODULE.bazel                   # Bazel module definition
├── BUILD.bazel                    # Root build file
├── CONTRIBUTING.md                # How to contribute
└── renovate.json                  # Automated dependency updates
```

## Documentation

| Document | Purpose |
|----------|---------|
| [PLAYBOOK.md](docs/PLAYBOOK.md) | Comprehensive IaC workflow (OpenTofu + Pulumi + Crossplane comparison) |
| [MIGRATION_PLAN.md](docs/MIGRATION_PLAN.md) | 6-phase migration from Monorepo-Uphillsnowball |
| [MIGRATION_CHECKLIST.md](docs/MIGRATION_CHECKLIST.md) | 33-task checklist with owners and deadlines |
| [RISK_REGISTER.md](docs/RISK_REGISTER.md) | 12-risk register with scoring matrix |
| [RISK_MITIGATION_PLAN.md](docs/RISK_MITIGATION_PLAN.md) | Detailed mitigation for top 6 risks |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Development workflow and coding standards |

## Migration Status

Migrating from [`Monorepo-Uphillsnowball`](https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball) (read-only archive after cutover).

| Phase | Status | Target |
|-------|--------|--------|
| 0. Preparation | ✅ Complete | May 13 |
| 1. Audit & Inventory | ⬜ Ready | May 14 |
| 2. Rich Hickey Refactoring | ⬜ Ready | May 22 |
| 3. Infrastructure Migration | ⬜ Ready | May 23 |
| 4. Code Migration & Cutover | ⬜ Ready | May 30 |
| 5. Final Verification | ⬜ Ready | June 3 |
| 6. Post-Migration Cleanup | ⬜ Ready | June 5 |

## Philosophy

We build systems that enforce physics, safety, memory, and doctrine at the architectural level.

**Simple Made Easy.** Unentangled > Familiar.

**Version:** v15.0 (May 2026)
